from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ai_services.llm_client import generate
from ai_services.prompt_builder import competitor_match_prompt

competitor_bp = Blueprint('competitor', __name__)


@competitor_bp.route('/competitor', methods=['GET'])
@login_required
def competitor_page():
    return render_template('modules/competitor.html', active_tab='competitor')


@competitor_bp.route('/api/v1/competitor-match', methods=['POST'])
@login_required
def competitor_match():
    data = request.get_json()
    if not data.get('competitor_urls') or not data.get('product'):
        return jsonify({'error': 'Missing competitor_urls or product'}), 400

    urls = [u.strip() for u in data['competitor_urls'] if u.strip()]
    system_prompt, user_prompt = competitor_match_prompt(
        competitor_urls=urls,
        product=data['product'],
    )

    try:
        output = generate(system_prompt, user_prompt, max_new_tokens=900)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    current_user.increment_usage()
    return jsonify({'success': True, 'output': output})