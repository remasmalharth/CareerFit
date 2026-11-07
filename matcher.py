import re
 
# ---------------------------------------------------------------------------
# 1. Skills dictionary:  name -> (category, [aliases])
#    An alias that starts with "re:" is a regular expression.
#    Only add skills you could talk about in an interview.
# ---------------------------------------------------------------------------
SKILLS = {
    # Programming languages
    "Python": ("Programming Languages", ["python"]),
    "Java": ("Programming Languages", ["java"]),
    "C++": ("Programming Languages", ["c++", "cpp"]),
    "C#": ("Programming Languages", ["c#", "csharp"]),
    "JavaScript": ("Programming Languages", ["javascript", "js"]),
    "TypeScript": ("Programming Languages", ["typescript"]),
    "PHP": ("Programming Languages", ["php"]),
    "Kotlin": ("Programming Languages", ["kotlin"]),
    "Swift": ("Programming Languages", ["swiftui", "swift programming"]),
    "Dart": ("Programming Languages", ["dart"]),
    # Web and mobile
    "HTML": ("Web & Mobile", ["html", "html5"]),
    "CSS": ("Web & Mobile", ["css", "css3"]),
    "React": (
        "Web & Mobile",
        [r"re:react(?:\.?js)?(?!\s+(?:to|quickly|fast|well|effectively|positively|appropriately)\b)"],
    ),
    "Angular": ("Web & Mobile", ["angular", "angularjs"]),
    "Vue": ("Web & Mobile", ["vue", "vue.js", "vuejs"]),
    "Node.js": ("Web & Mobile", ["node.js", "nodejs", "node js"]),
    "Django": ("Web & Mobile", ["django"]),
    "Flask": ("Web & Mobile", ["flask"]),
    "FastAPI": ("Web & Mobile", ["fastapi"]),
    "Spring Boot": ("Web & Mobile", ["spring boot", "springboot"]),
    "Flutter": ("Web & Mobile", ["flutter"]),
    # Databases
    "SQL": ("Databases", ["sql", "structured query language"]),
    "MySQL": ("Databases", ["mysql"]),
    "PostgreSQL": ("Databases", ["postgresql", "postgres"]),
    "MongoDB": ("Databases", ["mongodb"]),
    "Oracle": ("Databases", ["oracle"]),
    "Databases": (
        "Databases",
        ["database", "databases", "قواعد البيانات", "قواعد بيانات"],
    ),
    # Data and AI
    "Machine Learning": (
        "Data & AI",
        ["machine learning", "تعلم الآلة", "التعلم الآلي"],
    ),
    "Deep Learning": ("Data & AI", ["deep learning", "التعلم العميق"]),
    "NLP": ("Data & AI", ["nlp", "natural language processing"]),
    "Computer Vision": ("Data & AI", ["computer vision"]),
    "Data Analysis": (
        "Data & AI",
        ["data analysis", "data analytics", "تحليل البيانات"],
    ),
    "Data Visualization": (
        "Data & AI",
        ["data visualization", "data visualisation"],
    ),
    "Pandas": ("Data & AI", ["pandas"]),
    "NumPy": ("Data & AI", ["numpy"]),
    "Scikit-learn": ("Data & AI", ["scikit-learn", "sklearn", "scikit learn"]),
    "TensorFlow": ("Data & AI", ["tensorflow"]),
    "PyTorch": ("Data & AI", ["pytorch"]),
    "Power BI": ("Data & AI", ["power bi", "powerbi"]),
    "Tableau": ("Data & AI", ["tableau"]),
    "Excel": (
        "Data & AI",
        [
            r"re:excel(?!\s+(?:in|at|as|with)\b)",
            "microsoft excel",
            "اكسل",
            "إكسل",
        ],
    ),
    "Statistics": ("Data & AI", ["statistics", "statistical analysis"]),
    "ETL": ("Data & AI", ["etl"]),
    # Cloud and DevOps
    "AWS": ("Cloud & DevOps", ["aws", "amazon web services"]),
    "Azure": ("Cloud & DevOps", ["azure", "microsoft azure"]),
    "Google Cloud": ("Cloud & DevOps", ["google cloud", "gcp"]),
    "Docker": ("Cloud & DevOps", ["docker"]),
    "Kubernetes": ("Cloud & DevOps", ["kubernetes", "k8s"]),
    "Linux": ("Cloud & DevOps", ["linux"]),
    "CI/CD": ("Cloud & DevOps", ["ci/cd", "cicd", "continuous integration"]),
    "Git": ("Cloud & DevOps", ["git"]),
    "GitHub": ("Cloud & DevOps", ["github"]),
    # Security and networking
    "Cybersecurity": (
        "Security & Networking",
        ["cybersecurity", "cyber security", "الأمن السيبراني"],
    ),
    "Networking": (
        "Security & Networking",
        ["computer networks", "computer networking", "network administration", "tcp/ip", "الشبكات"],
    ),
    # Tools and practices
    "APIs": (
        "Tools & Practices",
        ["api", "apis", "rest api", "application programming interface"],
    ),
    "Agile": ("Tools & Practices", ["agile", "scrum"]),
    "Jira": ("Tools & Practices", ["jira"]),
    "Figma": ("Tools & Practices", ["figma"]),
    "SAP": ("Tools & Practices", ["sap"]),
    "ERP": ("Tools & Practices", ["erp"]),
    "Software Testing": (
        "Tools & Practices",
        ["software testing", "software test", "unit testing"],
    ),
    "Debugging": ("Tools & Practices", ["debugging", "debug"]),
    "Object-Oriented Programming": (
        "Tools & Practices",
        [
            "object-oriented programming",
            "object oriented programming",
            "oop",
        ],
    ),
    "Data Structures": ("Tools & Practices", ["data structures"]),
    "Algorithms": ("Tools & Practices", ["algorithms"]),
    # Soft skills (shown separately, never counted in the score)
    "Communication": ("Soft Skills", ["communication", "communicate", "التواصل"]),
    "Teamwork": (
        "Soft Skills",
        ["teamwork", "team work", "collaboration", "العمل الجماعي"],
    ),
    "Project Management": (
        "Soft Skills",
        ["project management", "إدارة المشاريع"],
    ),
    "Problem Solving": (
        "Soft Skills",
        ["problem solving", "problem-solving", "حل المشكلات"],
    ),
}
 
SOFT_SKILLS = {name for name, (cat, _) in SKILLS.items() if cat == "Soft Skills"}
 
# Kept so older code that imports SKILL_ALIASES still works.
SKILL_ALIASES = {name: aliases for name, (_, aliases) in SKILLS.items()}
SKILL_CATEGORY = {name: cat for name, (cat, _) in SKILLS.items()}
 
# ---------------------------------------------------------------------------
# 2. Related skills. If a required skill is missing but you have a close
#    one (for example you know PyTorch and the job wants TensorFlow),
#    you get partial credit instead of zero.
# ---------------------------------------------------------------------------
RELATED_GROUPS = [
    {"PyTorch", "TensorFlow", "Deep Learning"},
    {"Machine Learning", "Scikit-learn", "Deep Learning", "NLP"},
    {"AWS", "Azure", "Google Cloud"},
    {"Power BI", "Tableau", "Data Visualization"},
    {"SQL", "MySQL", "PostgreSQL", "Oracle", "Databases"},
    {"React", "Angular", "Vue"},
    {"Django", "Flask", "FastAPI"},
    {"Docker", "Kubernetes"},
    {"Git", "GitHub"},
    {"JavaScript", "TypeScript"},
    {"Java", "C#"},
    {"Pandas", "NumPy", "Data Analysis"},
    {"Software Testing", "Debugging"},
]
 
PRIORITY_WEIGHT = {"required": 1.0, "preferred": 0.5}
PARTIAL_CREDIT = 0.5
 
PREFERRED_CUES = [
    "preferred",
    "nice to have",
    "nice-to-have",
    "good to have",
    "bonus",
    "advantage",
    "a plus",
    "desirable",
    "مفضل",
    "يفضل",
    "ميزة",
]
REQUIRED_CUES = [
    "requirement",
    "required",
    "qualification",
    "must have",
    "must-have",
    "responsibilit",
    "we need",
    "you will",
    "المتطلبات",
    "المؤهلات",
    "المهام",
]
 
 
# ---------------------------------------------------------------------------
# 3. Skill detection
# ---------------------------------------------------------------------------
def contains_phrase(text, phrase):
    # (?<![\w.]) stops "js" from matching inside "node.js" or "react.js"
    body = phrase[3:] if phrase.startswith("re:") else re.escape(phrase)
    pattern = rf"(?<![\w.]){body}(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None
 
 
def find_skills(text):
    found = []
 
    for skill, (_, aliases) in SKILLS.items():
        if any(contains_phrase(text, alias) for alias in aliases):
            found.append(skill)
 
    return found
 
 
# ---------------------------------------------------------------------------
# 4. Required vs preferred detection
# ---------------------------------------------------------------------------
def classify_job_skills(job_text):
    """Return {skill: "required" | "preferred"} for a job description.
 
    A skill is "preferred" only when every place it is mentioned sits in a
    nice-to-have context ("Nice to have:", "Docker is a plus", ...).
    """
    segments = re.split(r"[\n\r•·▪●■]+|(?<=[.!?؟;])\s+", job_text)
 
    mode = "required"
    priorities = {}
 
    for raw in segments:
        line = raw.strip(" \t-–*")
        if not line:
            continue
 
        lower = line.lower()
        skills_in_line = find_skills(line)
 
        # A header looks like "Nice to have:" or "Requirements"
        lead = re.match(r"^([^:：]{1,40})[:：]", line)
        if lead:
            head = lead.group(1).lower()
        elif len(line) <= 60 and not skills_in_line:
            head = lower
        else:
            head = ""
 
        if any(cue in head for cue in PREFERRED_CUES):
            mode = "preferred"
        elif any(cue in head for cue in REQUIRED_CUES):
            mode = "required"
 
        has_preferred_cue = any(cue in lower for cue in PREFERRED_CUES)
        line_priority = (
            "preferred" if (mode == "preferred" or has_preferred_cue) else "required"
        )
 
        for skill in skills_in_line:
            if priorities.get(skill) != "required":
                priorities[skill] = line_priority
 
    return priorities
 
 
# ---------------------------------------------------------------------------
# 5. Main analysis
# ---------------------------------------------------------------------------
def related_in_resume(skill, resume_skills):
    related = set()
    for group in RELATED_GROUPS:
        if skill in group:
            related |= group
    related.discard(skill)
    return sorted(related & resume_skills)
 
 
def analyze(resume_text, job_text, extractor=None):
    """extractor: a function text -> list of skills (default: keyword matching)."""
    extractor = extractor or find_skills
 
    resume_skills = set(extractor(resume_text))
    priorities = classify_job_skills(job_text)
 
    # Skills found only by a smarter extractor (semantic) count as required.
    for skill in extractor(job_text):
        priorities.setdefault(skill, "required")
 
    matched, partial, missing, soft = [], [], [], []
    earned = total = 0.0
    category_totals = {}
 
    ordered = sorted(priorities.items(), key=lambda kv: (kv[1] != "required", kv[0]))
 
    for skill, priority in ordered:
        if skill in SOFT_SKILLS:
            soft.append(
                {
                    "skill": skill,
                    "priority": priority,
                    "in_resume": skill in resume_skills,
                }
            )
            continue
 
        weight = PRIORITY_WEIGHT[priority]
        category = SKILL_CATEGORY[skill]
        total += weight
        bucket = category_totals.setdefault(category, [0.0, 0.0])
        bucket[1] += weight
 
        if skill in resume_skills:
            matched.append({"skill": skill, "priority": priority})
            earned += weight
            bucket[0] += weight
        else:
            related = related_in_resume(skill, resume_skills)
            if related:
                partial.append(
                    {"skill": skill, "priority": priority, "related": related}
                )
                earned += weight * PARTIAL_CREDIT
                bucket[0] += weight * PARTIAL_CREDIT
            else:
                missing.append({"skill": skill, "priority": priority})
 
    score = round(earned / total * 100) if total else None
 
    categories = {
        cat: round(got / possible * 100)
        for cat, (got, possible) in category_totals.items()
    }
 
    extras = sorted(
        s for s in resume_skills if s not in priorities and s not in SOFT_SKILLS
    )
 
    return {
        "score": score,
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "soft": soft,
        "categories": categories,
        "resume_skills": sorted(resume_skills),
        "job_skills": list(priorities),
        "extras": extras,
    }
 