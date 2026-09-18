import os
import threading
from flask import Flask, redirect, url_for, jsonify
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload folder exists
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'static/uploads'), exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login_page'
    login_manager.login_message = 'Please log in to access ListifyAI.'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Register all blueprints ──────────────────────────────────────
    from routes.listing     import listing_bp
    from routes.ab_test     import ab_test_bp
    from routes.variants    import variants_bp
    from routes.seo         import seo_bp
    from routes.translate   import translate_bp
    from routes.competitor  import competitor_bp
    from routes.ocr         import ocr_bp
    from routes.performance import performance_bp
    from routes.export      import export_bp
    from routes.tone        import tone_bp
    from routes.image       import image_bp
    from routes.auth        import auth_bp

    for bp in [listing_bp, ab_test_bp, variants_bp, seo_bp, translate_bp,
               competitor_bp, ocr_bp, performance_bp, export_bp, tone_bp,
               image_bp, auth_bp]:
        app.register_blueprint(bp)

    # ── Model status endpoint (for header badge) ─────────────────────
    @app.route('/api/v1/model-status')
    def model_status():
        from ai_services.llm_client import _pipeline, _use_stub
        return jsonify({
            'loaded': _pipeline is not None,
            'stub':   _use_stub,
        })

    # ── Root redirect ────────────────────────────────────────────────
    @app.route('/')
    def index():
        return redirect(url_for('listing.listing_page'))

    # ── Create DB tables ─────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    # ── Pre-load the model in a background thread so Flask starts
    #    instantly but the model warms up concurrently ────────────────
    def _preload():
        with app.app_context():
            try:
                from ai_services.llm_client import get_pipeline
                get_pipeline()
            except Exception as e:
                print(f'[ListifyAI] Model pre-load error: {e}')

    t = threading.Thread(target=_preload, daemon=True)
    t.start()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    # use_reloader=False prevents the model loading twice in debug mode