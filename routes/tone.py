from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ai_services.llm_client import generate
from ai_services.prompt_builder import tone_training_prompt

tone_bp = Blueprint('tone', __name__)


@tone_bp.route('/tone', methods=['GET'])
@login_required
def tone_page():
    return render_template('modules/tone.html', active_tab='tone')


@tone_bp.route('/api/v1/tone-train', methods=['POST'])
@login_required
def tone_train():
    data = request.get_json()
    if not data.get('sample_text') or not data.get('new_product'):
        return jsonify({'error': 'Missing sample_text or new_product'}), 400

    system_prompt, user_prompt = tone_training_prompt(
        sample_text=data['sample_text'],
        new_product=data['new_product'],
    )

    try:
        output = generate(system_prompt, user_prompt, max_new_tokens=900)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    current_user.increment_usage()
    return jsonify({'success': True, 'output': output})