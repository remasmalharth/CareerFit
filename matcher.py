import re

SOFT_SKILLS = {
    "Communication",
    "Teamwork",
    "Problem Solving",
    "Project Management",
}

#skills
SKILL_ALIASES = {
    # Programming languages
    "Python": ["python"],
    "Java": ["java"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "csharp"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript"],
    "PHP": ["php"],
    "Kotlin": ["kotlin"],
    "Swift": ["swift"],
    "Dart": ["dart"],
    # Web
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "React": ["react", "react.js", "reactjs"],
    "Angular": ["angular"],
    "Vue": ["vue", "vue.js", "vuejs"],
    "Node.js": ["node.js", "nodejs"],
    "Django": ["django"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi"],
    "Spring Boot": ["spring boot", "springboot"],
    "Flutter": ["flutter"],
    # Databases
    "SQL": ["sql", "structured query language"],
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MongoDB": ["mongodb"],
    "Oracle": ["oracle"],
    "Databases": ["database", "databases", "قواعد البيانات", "قواعد بيانات"],
    # Data and AI
    "Machine Learning": ["machine learning", "تعلم الآلة", "التعلم الآلي"],
    "Deep Learning": ["deep learning", "التعلم العميق"],
    "NLP": ["nlp", "natural language processing"],
    "Computer Vision": ["computer vision"],
    "Data Analysis": [
        "data analysis",
        "data analytics",
        "تحليل البيانات",
    ],
    "Data Visualization": ["data visualization", "data visualisation"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Excel": ["excel", "microsoft excel"],
    "Statistics": ["statistics", "statistical analysis"],
    "ETL": ["etl"],
    # Cloud and DevOps
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure", "microsoft azure"],
    "Google Cloud": ["google cloud", "gcp"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Linux": ["linux"],
    "CI/CD": ["ci/cd", "cicd", "continuous integration"],
    "Git": ["git"],
    "GitHub": ["github"],
    # Security and networking
    "Cybersecurity": ["cybersecurity", "cyber security", "الأمن السيبراني"],
    "Networking": ["networking", "tcp/ip"],
    # Practices and tools
    "APIs": ["api", "apis", "rest api", "application programming interface"],
    "Agile": ["agile", "scrum"],
    "Jira": ["jira"],
    "Figma": ["figma"],
    "Software Testing": ["software testing", "software test", "unit testing"],
    "Debugging": ["debugging", "debug"],
    "Object-Oriented Programming": [
        "object-oriented programming",
        "object oriented programming",
        "oop",
    ],
    "Data Structures": ["data structures"],
    "Algorithms": ["algorithms"],
    # Soft skills (not counted in the percentage)
    "Communication": ["communication", "communicate", "التواصل"],
    "Teamwork": ["teamwork", "team work", "collaboration", "العمل الجماعي"],
    "Project Management": ["project management", "إدارة المشاريع"],
    "Problem Solving": ["problem solving", "problem-solving", "حل المشكلات"],
}
 
 
def contains_phrase(text, phrase):
    # (?<![\w.]) stops "js" from matching inside "node.js" or "react.js"
    pattern = rf"(?<![\w.]){re.escape(phrase)}(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None
 
 
def find_skills(text):
    found = []
 
    for skill, aliases in SKILL_ALIASES.items():
        if any(contains_phrase(text, alias) for alias in aliases):
            found.append(skill)
 
    return found


def match_skills(cv_text, job_text):
    cv_skills = set(find_skills(cv_text)) 
    job_skills = set(find_skills(job_text)) 

    matched = cv_skills & job_skills
    missing = job_skills - cv_skills

    if not job_skills:
        return {
            "score": None,
            "matched_skills": [],
            "missing_skills": [],
            "total_required": 0
        }

    score = round(len(matched) / len(job_skills) * 100)

    return {
        "score": score,
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "total_required": len(job_skills)
    }

if __name__ == "__main__":

    cv = "I know Python, SQL, and Docker"

    job = "We need Python, SQL, AWS, and Docker"

    result = match_skills(cv, job)

    print(result)