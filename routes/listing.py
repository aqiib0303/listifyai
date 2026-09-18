from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ai_services.llm_client import generate
from ai_services.prompt_builder import listing_prompt
from ai_services.filter import filter_negative_keywords
from ai_services.scorer import score_description
from config import Config

listing_bp = Blueprint('listing', __name__)


@listing_bp.route('/listing', methods=['GET'])
@login_required
def listing_page():
    return render_template('modules/listing.html', active_tab='listing')


@listing_bp.route('/api/v1/generate-listing', methods=['POST'])
@login_required
def generate_listing():
    if not current_user.can_generate(Config.DAILY_GENERATION_LIMIT):
        return jsonify({'error': 'Daily generation limit reached. Upgrade your plan for more.'}), 429

    data = request.get_json()
    required = ['product_name', 'features', 'audience', 'tone', 'word_count']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400

    system_prompt, user_prompt = listing_prompt(
        product_name=data['product_name'],
        features=data['features'],
        audience=data['audience'],
        tone=data['tone'],
        keywords=data.get('keywords', ''),
        word_count=data.get('word_count', 200),
        season=data.get('season', ''),
    )

    try:
        raw_output = generate(system_prompt, user_prompt, max_new_tokens=1024)
    except Exception as e:
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500

    filter_result = filter_negative_keywords(raw_output)
    score = score_description(filter_result['filtered_text'])
    current_user.increment_usage()

    return jsonify({
        'success': True,
        'output':  filter_result['filtered_text'],
        'flagged': filter_result['flagged'],
        'is_clean': filter_result['is_clean'],
        'score':   score,
    })