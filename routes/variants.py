from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ai_services.llm_client import generate
from ai_services.prompt_builder import bulk_variants_prompt

variants_bp = Blueprint('variants', __name__)


@variants_bp.route('/variants', methods=['GET'])
@login_required
def variants_page():
    return render_template('modules/variants.html', active_tab='variants')


@variants_bp.route('/api/v1/bulk-variants', methods=['POST'])
@login_required
def generate_variants():
    data = request.get_json()
    for field in ['product', 'base_desc', 'variation_type', 'variants']:
        if not data.get(field):
            return jsonify({'error': f'Missing field: {field}'}), 400

    variants_list = [v.strip() for v in data['variants'] if v.strip()]
    if not variants_list:
        return jsonify({'error': 'Provide at least one variant'}), 400

    system_prompt, user_prompt = bulk_variants_prompt(
        product=data['product'],
        base_desc=data['base_desc'],
        variation_type=data['variation_type'],
        variants_list=variants_list,
    )

    try:
        output = generate(system_prompt, user_prompt, max_new_tokens=1500)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    current_user.increment_usage()
    return jsonify({'success': True, 'output': output, 'count': len(variants_list)})