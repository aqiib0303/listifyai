from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ai_services.llm_client import generate
from ai_services.prompt_builder import seo_keywords_prompt

seo_bp = Blueprint('seo', __name__)


@seo_bp.route('/seo', methods=['GET'])
@login_required
def seo_page():
    return render_template('modules/seo.html', active_tab='seo')


@seo_bp.route('/api/v1/seo-keywords', methods=['POST'])
@login_required
def generate_seo():
    data = request.get_json()
    if not data.get('product_description'):
        return jsonify({'error': 'Missing product_description'}), 400

    system_prompt, user_prompt = seo_keywords_prompt(
        product_description=data['product_description'],
        marketplace=data.get('marketplace', 'amazon'),
    )

    try:
        output = generate(system_prompt, user_prompt, max_new_tokens=800)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    current_user.increment_usage()
    return jsonify({'success': True, 'output': output})