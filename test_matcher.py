from matcher import analyze, classify_job_skills, find_skills
 
 
def test_nodejs_is_not_javascript():
    skills = find_skills("We use Node.js on the backend")
    assert "Node.js" in skills
    assert "JavaScript" not in skills
 
 
def test_java_is_not_javascript():
    skills = find_skills("Strong JavaScript skills")
    assert "JavaScript" in skills
    assert "Java" not in skills
 
 
def test_react_verb_is_not_the_skill():
    assert "React" not in find_skills("You must react quickly to changes")
    assert "React" in find_skills("Experience with React.js")
 
 
def test_excel_verb_is_not_the_skill():
    assert "Excel" not in find_skills("Candidates who excel in a team")
    assert "Excel" in find_skills("Proficient in Microsoft Excel")
 
 
def test_arabic_alias():
    assert "Databases" in find_skills("خبرة في قواعد البيانات")
 
 
def test_required_vs_preferred():
    job = "Requirements: Python. Nice to have: Docker."
    priorities = classify_job_skills(job)
    assert priorities["Python"] == "required"
    assert priorities["Docker"] == "preferred"
 
 
def test_score_counts_missing_skills():
    result = analyze("Python SQL", "Requirements: Python, SQL, Docker")
    assert [m["skill"] for m in result["matched"]] == ["Python", "SQL"]
    assert [m["skill"] for m in result["missing"]] == ["Docker"]
    assert result["score"] == 67
 
 
def test_preferred_skill_counts_half():
    result = analyze("Python", "Requirements: Python. Nice to have: Docker.")
    assert result["score"] == 67  # 1.0 earned out of 1.5
 
 
def test_related_skill_gets_partial_credit():
    result = analyze("PyTorch", "Requirements: TensorFlow")
    assert result["partial"][0]["skill"] == "TensorFlow"
    assert result["partial"][0]["related"] == ["PyTorch"]
    assert result["score"] == 50
 
 
def test_soft_skills_do_not_count():
    result = analyze("Python", "We need good communication and teamwork")
    assert result["score"] is None
    assert {s["skill"] for s in result["soft"]} == {"Communication", "Teamwork"}
 
 
def test_custom_extractor_is_used():
    def fake_extractor(text):
        return ["Docker"]
 
    result = analyze("anything", "anything", extractor=fake_extractor)
    assert result["score"] == 100
 