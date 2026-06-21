"""
ResumeForge AI - Flask Backend
Main application entry point.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes.analyze import analyze_bp
from routes.generate import generate_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000", "*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
        }
    })
    
    # Register blueprints
    app.register_blueprint(analyze_bp)
    app.register_blueprint(generate_bp)
    
    # Health check
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'ResumeForge AI Backend',
            'gemini_configured': bool(Config.GEMINI_API_KEY),
        })
    
    # Error handlers
    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error.'}), 500
    
    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
