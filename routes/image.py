import os
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename

image_bp = Blueprint('image', __name__)

ALLOWED = {'png', 'jpg', 'jpeg', 'webp'}


def _allowed(fn):
    return '.' in fn and fn.rsplit('.', 1)[1].lower() in ALLOWED


@image_bp.route('/image', methods=['GET'])
@login_required
def image_page():
    return render_template('modules/image.html', active_tab='image')


@image_bp.route('/api/v1/process-image', methods=['POST'])
@login_required
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if not file or not _allowed(file.filename):
        return jsonify({'error': 'Invalid file type. Use PNG, JPG, JPEG, or WEBP.'}), 400

    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
    os.makedirs(upload_dir, exist_ok=True)
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    options = {
        'remove_bg': request.form.get('remove_bg') == 'true',
        'add_shadow': request.form.get('add_shadow') == 'true',
        'white_bg':  request.form.get('white_bg') == 'true',
    }

    try:
        with open(filepath, 'rb') as f:
            image_bytes = f.read()

        from image_services.bg_remover import remove_background
        result = remove_background(image_bytes)

        return jsonify({
            'success':     True,
            'transparent': result['transparent'],
            'white_bg':    result['white_bg'],
            'shadow':      result['shadow'],
            'options':     options,
        })
    except Exception as e:
        return jsonify({'error': f'Image processing failed: {str(e)}'}), 500