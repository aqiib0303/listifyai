import os
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ai_services.llm_client import generate
from ai_services.prompt_builder import ocr_listing_prompt

ocr_bp = Blueprint('ocr', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}


def _allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _ocr_image(filepath: str) -> str:
    """Run pytesseract OCR if available, otherwise return placeholder."""
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(filepath)
        return pytesseract.image_to_string(img)
    except ImportError:
        return f'[OCR stub — pytesseract not installed. File: {os.path.basename(filepath)}]'
    except Exception as e:
        return f'[OCR error: {e}]'


@ocr_bp.route('/ocr', methods=['GET'])
@login_required
def ocr_page():
    return render_template('modules/ocr.html', active_tab='ocr')


@ocr_bp.route('/api/v1/ocr-listing', methods=['POST'])
@login_required
def ocr_listing():
    extracted_text = ''

    # --- image upload path ---
    if 'image' in request.files:
        file = request.files['image']
        if file and _allowed(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            extracted_text = _ocr_image(filepath)

    # --- manual text path ---
    manual = request.form.get('text') or (request.get_json(silent=True) or {}).get('text', '')
    if manual:
        extracted_text = manual

    if not extracted_text.strip():
        return jsonify({'error': 'No text extracted and no manual text provided'}), 400

    system_prompt, user_prompt = ocr_listing_prompt(extracted_text)

    try:
        output = generate(system_prompt, user_prompt, max_new_tokens=900)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    current_user.increment_usage()
    return jsonify({'success': True, 'output': output, 'extracted_text': extracted_text})