"""
Resume analysis API route.
POST /api/analyze - accepts file upload, returns analysis JSON.
"""
from flask import Blueprint, request, jsonify
from config import Config
from services.parser import extract_text
from services.analyzer import analyze_resume
from services.gemini_service import get_ai_analysis

analyze_bp = Blueprint('analyze', __name__)


@analyze_bp.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze an uploaded resume file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not Config.allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type. Please upload PDF or DOCX.'}), 400
    
    try:
        file_bytes = file.read()
        
        # Step 1: Extract text
        text = extract_text(file_bytes, file.filename)
        
        if not text.strip():
            return jsonify({'error': 'Could not extract text from the file. The file may be image-based or corrupted.'}), 400
        
        # Step 2 & 3: Analyze and score
        analysis = analyze_resume(text)
        
        # Step 4: AI analysis
        ai_feedback = get_ai_analysis(
            text,
            analysis['scores'],
            analysis['sections']
        )
        
        # Combine results
        result = {
            'success': True,
            'scores': analysis['scores'],
            'sections': analysis['sections'],
            'word_count': analysis['word_count'],
            'ai_analysis': ai_feedback,
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
