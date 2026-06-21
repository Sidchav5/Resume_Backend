"""
LaTeX generation API route.
POST /api/generate-latex - accepts resume JSON, returns LaTeX string.
"""
from flask import Blueprint, request, jsonify
from services.latex_generator import generate_latex

generate_bp = Blueprint('generate', __name__)


@generate_bp.route('/api/generate-latex', methods=['POST'])
def generate():
    """Generate LaTeX from structured resume data."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        latex_code = generate_latex(data)
        
        return jsonify({
            'success': True,
            'latex': latex_code,
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'LaTeX generation failed: {str(e)}'}), 500
