from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ai_services.llm_client import generate
from ai_services.prompt_builder import translate_prompt

translate_bp = Blueprint('translate', __name__)


@translate_bp.route('/translate', methods=['GET'])
@login_required
def translate_page():
    return render_template('modules/translate.html', active_tab='translate')


@translate_bp.route('/api/v1/translate', methods=['POST'])
@login_required
def translate():
    data = request.get_json()
    for field in ['text', 'language', 'market']:
        if not data.get(field):
            return jsonify({'error': f'Missing field: {field}'}), 400

    system_prompt, user_prompt = translate_prompt(
        text=data['text'],
        language=data['language'],
        market=data['market'],
    )

    try:
        output = generate(system_prompt, user_prompt, max_new_tokens=1000)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    current_user.increment_usage()
    return jsonify({'success': True, 'output': output})