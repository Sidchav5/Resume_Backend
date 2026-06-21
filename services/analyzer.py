"""
Resume scoring and analysis service.
Provides rule-based scoring for ATS compatibility, content quality,
formatting, and technical relevance.
"""
import re
from services.parser import detect_sections


# Keywords that ATS systems commonly look for
ATS_KEYWORDS = {
    'action_verbs': [
        'developed', 'implemented', 'designed', 'managed', 'led', 'created',
        'built', 'optimized', 'improved', 'achieved', 'delivered', 'analyzed',
        'coordinated', 'established', 'increased', 'reduced', 'launched',
        'maintained', 'resolved', 'streamlined', 'collaborated', 'mentored',
        'architected', 'automated', 'deployed', 'integrated', 'engineered',
    ],
    'technical_terms': [
        'python', 'javascript', 'react', 'node', 'sql', 'api', 'git',
        'docker', 'aws', 'azure', 'machine learning', 'data', 'agile',
        'ci/cd', 'rest', 'html', 'css', 'java', 'typescript', 'database',
        'linux', 'cloud', 'kubernetes', 'tensorflow', 'flask', 'django',
    ],
    'metrics_pattern': r'\d+[%+]|\$[\d,]+|\d+x|\d+\s*(users|clients|projects|teams|members)',
}


def calculate_ats_score(text, sections):
    """Calculate ATS compatibility score (0-100)."""
    score = 0
    text_lower = text.lower()
    
    # Section presence (40 points)
    essential_sections = ['contact', 'education', 'experience', 'skills']
    good_sections = ['summary', 'projects', 'certifications', 'achievements']
    
    for section in essential_sections:
        if sections.get(section):
            score += 8  # 32 points for essentials
    
    for section in good_sections:
        if sections.get(section):
            score += 2  # 8 points for good-to-have
    
    # Action verbs (20 points)
    verb_count = sum(1 for v in ATS_KEYWORDS['action_verbs'] if v in text_lower)
    score += min(20, verb_count * 2)
    
    # Technical terms (20 points)
    tech_count = sum(1 for t in ATS_KEYWORDS['technical_terms'] if t in text_lower)
    score += min(20, tech_count * 2)
    
    # Quantifiable metrics (10 points)
    metrics = re.findall(ATS_KEYWORDS['metrics_pattern'], text_lower)
    score += min(10, len(metrics) * 3)
    
    # Length check (10 points) - ideal 300-1000 words
    word_count = len(text.split())
    if 300 <= word_count <= 1000:
        score += 10
    elif 200 <= word_count < 300 or 1000 < word_count <= 1500:
        score += 6
    elif word_count > 100:
        score += 3
    
    return min(100, score)


def calculate_content_score(text, sections):
    """Calculate content quality score (0-100)."""
    score = 0
    text_lower = text.lower()
    word_count = len(text.split())
    
    # Sufficient content depth (25 points)
    if word_count >= 400:
        score += 25
    elif word_count >= 250:
        score += 18
    elif word_count >= 150:
        score += 10
    else:
        score += 5
    
    # Action verbs diversity (25 points)
    verbs_found = [v for v in ATS_KEYWORDS['action_verbs'] if v in text_lower]
    unique_verbs = len(set(verbs_found))
    score += min(25, unique_verbs * 3)
    
    # Quantifiable achievements (25 points)
    metrics = re.findall(ATS_KEYWORDS['metrics_pattern'], text_lower)
    score += min(25, len(metrics) * 5)
    
    # Section completeness (25 points)
    total_sections = len(sections)
    present_sections = sum(1 for v in sections.values() if v)
    if total_sections > 0:
        score += int((present_sections / total_sections) * 25)
    
    return min(100, score)


def calculate_formatting_score(text):
    """Calculate formatting quality score (0-100)."""
    score = 0
    lines = text.split('\n')
    
    # Consistent line lengths (20 points)
    non_empty_lines = [l for l in lines if l.strip()]
    if non_empty_lines:
        avg_len = sum(len(l) for l in non_empty_lines) / len(non_empty_lines)
        if 30 <= avg_len <= 100:
            score += 20
        else:
            score += 10
    
    # Bullet points usage (20 points)
    bullet_patterns = re.findall(r'[•\-\*\u2022]\s', text)
    if len(bullet_patterns) >= 5:
        score += 20
    elif len(bullet_patterns) >= 2:
        score += 12
    else:
        score += 5
    
    # Proper spacing (20 points)
    if len(non_empty_lines) >= 10:
        score += 20
    elif len(non_empty_lines) >= 5:
        score += 12
    else:
        score += 5
    
    # Not too long (20 points) - 1-2 pages ideal
    word_count = len(text.split())
    if 250 <= word_count <= 800:
        score += 20
    elif 150 <= word_count <= 1200:
        score += 14
    else:
        score += 7
    
    # No excessive whitespace / clean structure (20 points)
    empty_line_ratio = (len(lines) - len(non_empty_lines)) / max(len(lines), 1)
    if empty_line_ratio < 0.4:
        score += 20
    elif empty_line_ratio < 0.6:
        score += 12
    else:
        score += 5
    
    return min(100, score)


def calculate_technical_score(text):
    """Calculate technical relevance score (0-100)."""
    score = 0
    text_lower = text.lower()
    
    # Technical terms (40 points)
    tech_found = [t for t in ATS_KEYWORDS['technical_terms'] if t in text_lower]
    score += min(40, len(tech_found) * 4)
    
    # Project descriptions (20 points)
    project_indicators = ['built', 'developed', 'created', 'implemented', 'designed', 'deployed']
    project_count = sum(1 for p in project_indicators if p in text_lower)
    score += min(20, project_count * 4)
    
    # GitHub/portfolio links (15 points)
    url_pattern = r'(github\.com|gitlab\.com|linkedin\.com|portfolio|http[s]?://)'
    urls = re.findall(url_pattern, text_lower)
    score += min(15, len(urls) * 5)
    
    # Technical depth - specific versions, frameworks (25 points)
    depth_patterns = [
        r'v\d+', r'\d+\.\d+', r'python\s*\d', r'react\s*\d',
        r'node\s*\d', r'java\s*\d', r'version',
    ]
    depth_count = sum(1 for p in depth_patterns if re.search(p, text_lower))
    score += min(25, depth_count * 5)
    
    return min(100, score)


def analyze_resume(text):
    """Run full analysis and return structured results."""
    sections = detect_sections(text)
    
    ats_score = calculate_ats_score(text, sections)
    content_score = calculate_content_score(text, sections)
    formatting_score = calculate_formatting_score(text)
    technical_score = calculate_technical_score(text)
    
    overall_score = int(
        ats_score * 0.35 +
        content_score * 0.25 +
        formatting_score * 0.15 +
        technical_score * 0.25
    )
    
    # Identify missing sections
    missing = [s for s, present in sections.items() if not present]
    present = [s for s, p in sections.items() if p]
    
    return {
        'scores': {
            'overall': overall_score,
            'ats': ats_score,
            'content': content_score,
            'formatting': formatting_score,
            'technical': technical_score,
        },
        'sections': {
            'present': present,
            'missing': missing,
        },
        'word_count': len(text.split()),
        'text': text,
    }
