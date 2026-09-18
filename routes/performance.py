from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ai_services.llm_client import generate
from ai_services.prompt_builder import performance_analysis_prompt

performance_bp = Blueprint('performance', __name__)


@performance_bp.route('/performance', methods=['GET'])
@login_required
def performance_page():
    return render_template('modules/performance.html', active_tab='performance')


@performance_bp.route('/api/v1/performance', methods=['POST'])
@login_required
def analyze_performance():
    data = request.get_json()
    if not data.get('product'):
        return jsonify({'error': 'Missing product name'}), 400

    old_metrics = data.get('old_metrics', {})
    new_metrics = data.get('new_metrics', {})

    system_prompt, user_prompt = performance_analysis_prompt(
        product=data['product'],
        old_metrics=old_metrics,
        new_metrics=new_metrics,
    )

    try:
        output = generate(system_prompt, user_prompt, max_new_tokens=700)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Calculate delta metrics client-friendly
    def pct(old, new):
        try:
            o, n = float(old), float(new)
            if o == 0:
                return None
            return round(((n - o) / o) * 100, 1)
        except Exception:
            return None

    deltas = {
        'views':      pct(old_metrics.get('views', 0),      new_metrics.get('views', 0)),
        'conversion': pct(old_metrics.get('conversion', 0), new_metrics.get('conversion', 0)),
        'revenue':    pct(old_metrics.get('revenue', 0),    new_metrics.get('revenue', 0)),
    }

    current_user.increment_usage()
    return jsonify({'success': True, 'output': output, 'deltas': deltas})