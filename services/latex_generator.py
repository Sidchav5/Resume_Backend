"""
LaTeX resume template generator.
Generates professional ATS-friendly LaTeX code from structured resume data.
"""


def generate_latex(data):
    """Generate a complete LaTeX resume from structured JSON data."""
    
    personal = data.get('personalInfo', {})
    summary = data.get('summary', '')
    education = data.get('education', [])
    experience = data.get('experience', [])
    projects = data.get('projects', [])
    skills = data.get('skills', {})
    certifications = data.get('certifications', [])
    achievements = data.get('achievements', [])
    positions = data.get('positions', [])
    extracurricular = data.get('extracurricular', [])
    
    latex = []
    
    # Preamble
    latex.append(r"""\documentclass[a4paper,11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=0.75in]{geometry}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{fontawesome5}

% Colors
\definecolor{headingcolor}{HTML}{2563EB}
\definecolor{accentcolor}{HTML}{1E40AF}
\definecolor{linkcolor}{HTML}{2563EB}

% Section formatting
\titleformat{\section}{\large\bfseries\color{headingcolor}}{}{0em}{}[\titlerule]
\titlespacing*{\section}{0pt}{12pt}{6pt}

% Remove page numbers
\pagestyle{empty}

% Hyperlink setup
\hypersetup{colorlinks=true, linkcolor=linkcolor, urlcolor=linkcolor}

\begin{document}
""")
    
    # Header / Personal Info
    name = _escape(personal.get('fullName', 'Your Name'))
    latex.append(f"\\begin{{center}}")
    latex.append(f"  {{\\LARGE\\bfseries {name}}} \\\\[4pt]")
    
    contact_parts = []
    if personal.get('email'):
        contact_parts.append(f"\\faEnvelope\\ \\href{{mailto:{_escape(personal['email'])}}}{{{_escape(personal['email'])}}}")
    if personal.get('phone'):
        contact_parts.append(f"\\faPhone\\ {_escape(personal['phone'])}")
    if personal.get('location'):
        contact_parts.append(f"\\faMapMarker\\ {_escape(personal['location'])}")
    if contact_parts:
        latex.append(f"  {' $|$ '.join(contact_parts)} \\\\[2pt]")
    
    link_parts = []
    if personal.get('linkedin'):
        latex_url = _escape(personal['linkedin'])
        link_parts.append(f"\\faLinkedin\\ \\href{{{latex_url}}}{{LinkedIn}}")
    if personal.get('github'):
        latex_url = _escape(personal['github'])
        link_parts.append(f"\\faGithub\\ \\href{{{latex_url}}}{{GitHub}}")
    if personal.get('portfolio'):
        latex_url = _escape(personal['portfolio'])
        link_parts.append(f"\\faGlobe\\ \\href{{{latex_url}}}{{Portfolio}}")
    if link_parts:
        latex.append(f"  {' $|$ '.join(link_parts)}")
    
    latex.append(f"\\end{{center}}\n")
    
    # Professional Summary
    if summary.strip():
        latex.append(f"\\section{{Professional Summary}}")
        latex.append(f"{_escape(summary)}\n")
    
    # Education
    if education:
        latex.append(f"\\section{{Education}}")
        for edu in education:
            degree = _escape(edu.get('degree', ''))
            college = _escape(edu.get('college', ''))
            cgpa = _escape(edu.get('cgpa', ''))
            duration = _escape(edu.get('duration', ''))
            latex.append(f"\\textbf{{{degree}}} \\hfill {duration} \\\\")
            cgpa_str = f" -- CGPA: {cgpa}" if cgpa else ""
            latex.append(f"{college}{cgpa_str}\n")
    
    # Experience
    if experience:
        latex.append(f"\\section{{Experience}}")
        for exp in experience:
            role = _escape(exp.get('role', ''))
            company = _escape(exp.get('company', ''))
            duration = _escape(exp.get('duration', ''))
            responsibilities = exp.get('responsibilities', '')
            latex.append(f"\\textbf{{{role}}} -- {company} \\hfill {duration}")
            if responsibilities:
                items = [r.strip() for r in responsibilities.split('\n') if r.strip()]
                if not items:
                    items = [responsibilities]
                latex.append(f"\\begin{{itemize}}[leftmargin=*, nosep]")
                for item in items:
                    latex.append(f"  \\item {_escape(item)}")
                latex.append(f"\\end{{itemize}}\n")
    
    # Projects
    if projects:
        latex.append(f"\\section{{Projects}}")
        for proj in projects:
            name_p = _escape(proj.get('name', ''))
            tech = _escape(proj.get('techStack', ''))
            desc = _escape(proj.get('description', ''))
            github = proj.get('github', '')
            
            title_line = f"\\textbf{{{name_p}}}"
            if tech:
                title_line += f" | \\textit{{{tech}}}"
            if github:
                title_line += f" | \\href{{{_escape(github)}}}{{\\faGithub}}"
            latex.append(title_line)
            
            if desc:
                items = [d.strip() for d in desc.split('\n') if d.strip()]
                if not items:
                    items = [desc]
                latex.append(f"\\begin{{itemize}}[leftmargin=*, nosep]")
                for item in items:
                    latex.append(f"  \\item {_escape(item)}")
                latex.append(f"\\end{{itemize}}\n")
    
    # Skills
    if any(skills.get(k) for k in ['languages', 'frameworks', 'tools']):
        latex.append(f"\\section{{Technical Skills}}")
        latex.append(f"\\begin{{itemize}}[leftmargin=*, nosep]")
        if skills.get('languages'):
            latex.append(f"  \\item \\textbf{{Languages:}} {_escape(skills['languages'])}")
        if skills.get('frameworks'):
            latex.append(f"  \\item \\textbf{{Frameworks:}} {_escape(skills['frameworks'])}")
        if skills.get('tools'):
            latex.append(f"  \\item \\textbf{{Tools:}} {_escape(skills['tools'])}")
        latex.append(f"\\end{{itemize}}\n")
    
    # Certifications
    if certifications:
        certs = [c for c in certifications if isinstance(c, str) and c.strip()]
        if not certs and certifications:
            certs = [c.get('name', '') for c in certifications if isinstance(c, dict) and c.get('name')]
        if certs:
            latex.append(f"\\section{{Certifications}}")
            latex.append(f"\\begin{{itemize}}[leftmargin=*, nosep]")
            for cert in certs:
                latex.append(f"  \\item {_escape(cert)}")
            latex.append(f"\\end{{itemize}}\n")
    
    # Achievements
    if achievements:
        achs = [a for a in achievements if isinstance(a, str) and a.strip()]
        if not achs and achievements:
            achs = [a.get('name', '') for a in achievements if isinstance(a, dict) and a.get('name')]
        if achs:
            latex.append(f"\\section{{Achievements}}")
            latex.append(f"\\begin{{itemize}}[leftmargin=*, nosep]")
            for ach in achs:
                latex.append(f"  \\item {_escape(ach)}")
            latex.append(f"\\end{{itemize}}\n")
    
    # Positions of Responsibility
    if positions:
        pos_list = [p for p in positions if isinstance(p, str) and p.strip()]
        if not pos_list and positions:
            pos_list = [p.get('name', '') for p in positions if isinstance(p, dict) and p.get('name')]
        if pos_list:
            latex.append(f"\\section{{Positions of Responsibility}}")
            latex.append(f"\\begin{{itemize}}[leftmargin=*, nosep]")
            for pos in pos_list:
                latex.append(f"  \\item {_escape(pos)}")
            latex.append(f"\\end{{itemize}}\n")
    
    # Extracurricular
    if extracurricular:
        ext_list = [e for e in extracurricular if isinstance(e, str) and e.strip()]
        if not ext_list and extracurricular:
            ext_list = [e.get('name', '') for e in extracurricular if isinstance(e, dict) and e.get('name')]
        if ext_list:
            latex.append(f"\\section{{Extracurricular Activities}}")
            latex.append(f"\\begin{{itemize}}[leftmargin=*, nosep]")
            for ext in ext_list:
                latex.append(f"  \\item {_escape(ext)}")
            latex.append(f"\\end{{itemize}}\n")
    
    # End document
    latex.append(r"\end{document}")
    
    return '\n'.join(latex)


def _escape(text):
    """Escape special LaTeX characters."""
    if not text:
        return ''
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text
