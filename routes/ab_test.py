from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ai_services.llm_client import generate
from ai_services.prompt_builder import ab_test_prompt
from ai_services.scorer import score_description

ab_test_bp = Blueprint('ab_test', __name__)


@ab_test_bp.route('/ab-test', methods=['GET'])
@login_required
def ab_test_page():
    return render_template('modules/ab_test.html', active_tab='ab')


@ab_test_bp.route('/api/v1/ab-test', methods=['POST'])
@login_required
def generate_ab():
    data = request.get_json()
    for field in ['product', 'features', 'audience']:
        if not data.get(field):
            return jsonify({'error': f'Missing field: {field}'}), 400

    system_prompt, user_prompt = ab_test_prompt(
        product=data['product'],
        features=data['features'],
        audience=data['audience'],
    )

    try:
        raw = generate(system_prompt, user_prompt, max_new_tokens=800)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    version_a, version_b = _split_ab(raw)
    current_user.increment_usage()

    return jsonify({
        'success':   True,
        'version_a': version_a,
        'version_b': version_b,
        'score_a':   score_description(version_a),
        'score_b':   score_description(version_b),
    })


def _split_ab(text: str):
    import re
    parts = re.split(r'---\s*VERSION\s*[AB]\s*---', text, flags=re.IGNORECASE)
    parts = [p.strip() for p in parts if p.strip()]
    a = parts[0] if len(parts) > 0 else text
    b = parts[1] if len(parts) > 1 else ''
    return a, b