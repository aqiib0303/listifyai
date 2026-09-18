import io
import csv
from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from ai_services.llm_client import generate
from ai_services.prompt_builder import export_format_prompt

export_bp = Blueprint('export', __name__)


@export_bp.route('/export', methods=['GET'])
@login_required
def export_page():
    return render_template('modules/export.html', active_tab='export')


@export_bp.route('/api/v1/export-format', methods=['POST'])
@login_required
def format_export():
    data = request.get_json()
    if not data.get('listing_content') or not data.get('platform'):
        return jsonify({'error': 'Missing listing_content or platform'}), 400

    system_prompt, user_prompt = export_format_prompt(
        platform=data['platform'],
        listing_content=data['listing_content'],
    )

    try:
        output = generate(system_prompt, user_prompt, max_new_tokens=900)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    current_user.increment_usage()
    return jsonify({'success': True, 'output': output, 'platform': data['platform']})


@export_bp.route('/api/v1/export-download', methods=['POST'])
@login_required
def download_export():
    """Generate and stream a CSV file for download."""
    data = request.get_json()
    content  = data.get('content', '')
    platform = data.get('platform', 'shopify')

    buf = io.StringIO()
    writer = csv.writer(buf)

    if platform == 'shopify':
        writer.writerow(['Handle', 'Title', 'Body (HTML)', 'Tags', 'Published', 'Variant Price'])
        writer.writerow(['my-product', 'Product Title', f'<p>{content}</p>', 'tag1,tag2', 'true', '29.99'])
    elif platform == 'woocommerce':
        writer.writerow(['ID', 'Name', 'Description', 'Short description', 'Tags', 'Regular price', 'SKU'])
        writer.writerow(['1', 'Product Name', content, content[:120], 'tag1,tag2', '29.99', 'SKU-001'])
    else:  # daraz
        writer.writerow(['Item Name', 'Product Description', 'Keywords', 'Key Features'])
        writer.writerow(['Product', content, 'keyword1;keyword2', 'feature1|feature2'])

    buf.seek(0)
    mem = io.BytesIO(buf.getvalue().encode())
    mem.seek(0)

    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'listifyai-{platform}-export.csv',
    )