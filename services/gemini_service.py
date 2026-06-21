"""
Google Gemini AI integration service.
Uses the free-tier Gemini API for resume analysis.
"""
import json
import google.generativeai as genai
from config import Config


def get_ai_analysis(resume_text, scores, sections):
    """
    Get AI-powered resume analysis from Gemini.
    Returns structured feedback or a fallback if API unavailable.
    """
    if not Config.GEMINI_API_KEY:
        return _fallback_analysis(scores, sections)
    
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        
        prompt = _build_prompt(resume_text, scores, sections)
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048,
            )
        )
        
        # Parse the JSON response
        response_text = response.text.strip()
        
        # Handle markdown code blocks in response
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            lines = lines[1:]  # Remove opening ```json
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]  # Remove closing ```
            response_text = '\n'.join(lines)
        
        analysis = json.loads(response_text)
        return analysis
        
    except json.JSONDecodeError:
        # If Gemini returns non-JSON, wrap it
        return {
            'strengths': [response_text[:500] if 'response_text' in dir() else 'Analysis completed'],
            'weaknesses': [],
            'ats_improvements': [],
            'project_feedback': [],
            'skill_feedback': [],
            'overall_recommendations': ['Please review the detailed scores for insights.'],
        }
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        return _fallback_analysis(scores, sections)


def _build_prompt(resume_text, scores, sections):
    """Build the analysis prompt for Gemini."""
    return f"""You are an expert resume reviewer and career coach. Analyze the following resume text and provide detailed, actionable feedback.

RESUME TEXT:
\"\"\"
{resume_text[:3000]}
\"\"\"

CURRENT SCORES:
- ATS Score: {scores.get('ats', 0)}/100
- Content Score: {scores.get('content', 0)}/100
- Formatting Score: {scores.get('formatting', 0)}/100
- Technical Score: {scores.get('technical', 0)}/100
- Overall Score: {scores.get('overall', 0)}/100

SECTIONS FOUND: {', '.join(sections.get('present', []))}
SECTIONS MISSING: {', '.join(sections.get('missing', []))}

Respond with ONLY valid JSON in this exact format (no markdown, no code blocks):
{{
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
    "ats_improvements": ["improvement 1", "improvement 2", "improvement 3"],
    "project_feedback": ["feedback 1", "feedback 2"],
    "skill_feedback": ["feedback 1", "feedback 2"],
    "overall_recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"]
}}

Provide 3-5 items per category. Be specific, actionable, and reference the actual resume content. Focus on what would make this resume more competitive for tech jobs."""


def _fallback_analysis(scores, sections):
    """Provide rule-based analysis when Gemini API is unavailable."""
    strengths = []
    weaknesses = []
    ats_improvements = []
    
    # Analyze scores
    if scores.get('ats', 0) >= 70:
        strengths.append('Good ATS compatibility - your resume is likely to pass automated screening systems.')
    else:
        weaknesses.append('Low ATS score - consider adding more relevant keywords and standardizing section headings.')
        ats_improvements.append('Use standard section headings like "Experience", "Education", "Skills".')
    
    if scores.get('content', 0) >= 70:
        strengths.append('Strong content quality with good detail in descriptions.')
    else:
        weaknesses.append('Content could be more detailed - add quantifiable achievements and action verbs.')
    
    if scores.get('technical', 0) >= 70:
        strengths.append('Good technical depth with relevant technologies mentioned.')
    else:
        weaknesses.append('Consider adding more technical details, specific technologies, and project links.')
    
    # Section-based feedback
    missing = sections.get('missing', [])
    present = sections.get('present', [])
    
    if len(present) >= 5:
        strengths.append(f'Well-structured resume with {len(present)} key sections identified.')
    
    if missing:
        weaknesses.append(f'Missing sections: {", ".join(missing)}. Adding these would strengthen your resume.')
    
    if 'summary' in missing:
        ats_improvements.append('Add a Professional Summary section at the top of your resume.')
    
    if 'skills' in missing:
        ats_improvements.append('Add a dedicated Skills section with categorized technical skills.')
    
    if 'certifications' in missing:
        ats_improvements.append('Consider adding relevant certifications to stand out.')
    
    return {
        'strengths': strengths if strengths else ['Resume submitted successfully for analysis.'],
        'weaknesses': weaknesses if weaknesses else ['No critical weaknesses identified.'],
        'ats_improvements': ats_improvements if ats_improvements else ['Resume follows basic ATS guidelines.'],
        'project_feedback': ['Add quantifiable impact to project descriptions.', 'Include links to live demos or GitHub repositories.'],
        'skill_feedback': ['Categorize skills by type (Languages, Frameworks, Tools).', 'Prioritize skills that match your target job descriptions.'],
        'overall_recommendations': [
            'Tailor your resume for each job application by matching keywords from the job description.',
            'Keep your resume to 1-2 pages for the best impact.',
            'Use consistent formatting throughout all sections.',
        ],
    }
