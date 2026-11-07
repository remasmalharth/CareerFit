import pandas as pd
import streamlit as st
 
from extractors import extract_text
from matcher import analyze
 
 
st.set_page_config(page_title="CareerFit")
 
st.title("CareerFit")
st.write(
    "Compare the skills in your resume with the skills required by a job "
    "and see which skills are missing."
)
 
 
def label(priority):
    return "Required" if priority == "required" else "Preferred"
 
 
resume_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
 
job_description = st.text_area("Paste the job description", height=220)
 
use_semantic = st.checkbox("Use semantic matching (understands meaning, slower)")
 
if st.button("Compare Skills"):
    if resume_file is None:
        st.warning("Please upload a PDF or DOCX resume.")
 
    elif not job_description.strip():
        st.warning("Please paste a job description.")
 
    else:
        try:
            resume_text = extract_text(resume_file.name, resume_file.getvalue())
 
            if not resume_text.strip():
                st.error(
                    "No readable text was found. The PDF may be scanned "
                    "or image-based."
                )
 
            else:
                if use_semantic:
                    try:
                        from semantic_matcher import find_skills_hybrid
 
                        result = analyze(
                            resume_text,
                            job_description,
                            extractor=find_skills_hybrid,
                        )
                    except ImportError:
                        st.warning(
                            "Semantic matching is not installed here, "
                            "using keyword matching instead."
                        )
                        result = analyze(resume_text, job_description)
                else:
                    result = analyze(resume_text, job_description)
 
                if result["score"] is None:
                    st.warning(
                        "No technical skills from the current skill list "
                        "were found in the job description."
                    )
 
                else:
                    st.metric("Weighted Match Score", f"{result['score']}%")
 
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Matched", len(result["matched"]))
                    col2.metric("Related experience", len(result["partial"]))
                    col3.metric("Missing", len(result["missing"]))
 
                    st.caption(
                        "Required skills count fully, preferred skills count "
                        "half, and a related skill you already have counts as "
                        "half credit. Soft skills are not included in the score. "
                        "Matching is keyword-based, so unusual wording may be "
                        "missed."
                    )
 
                    tab_matched, tab_related, tab_missing, tab_details = st.tabs(
                        [
                            "Matched",
                            "Related experience",
                            "Missing",
                            "Details",
                        ]
                    )
 
                    with tab_matched:
                        if result["matched"]:
                            for item in result["matched"]:
                                st.markdown(
                                    f"- **{item['skill']}** ({label(item['priority'])})"
                                )
                        else:
                            st.write("No matching skills detected.")
 
                    with tab_related:
                        if result["partial"]:
                            st.caption(
                                "You do not list these exactly, but you have "
                                "closely related skills. Mention the connection "
                                "in your resume or interview."
                            )
                            for item in result["partial"]:
                                st.markdown(
                                    f"- **{item['skill']}** ({label(item['priority'])})"
                                    f" — you have: {', '.join(item['related'])}"
                                )
                        else:
                            st.write("No related skills found.")
 
                    with tab_missing:
                        if result["missing"]:
                            for item in result["missing"]:
                                st.markdown(
                                    f"- **{item['skill']}** ({label(item['priority'])})"
                                )
                        else:
                            st.success("No missing skills detected.")
 
                    with tab_details:
                        if result["categories"]:
                            st.markdown("#### Coverage by category")
                            chart = pd.DataFrame(
                                {"Coverage %": result["categories"]}
                            )
                            st.bar_chart(chart)
 
                        if result["soft"]:
                            st.markdown("#### Soft skills mentioned in the job")
                            st.write(
                                ", ".join(
                                    f"{item['skill']} (in your resume)"
                                    if item["in_resume"]
                                    else f"{item['skill']} (not found)"
                                    for item in result["soft"]
                                )
                            )
 
                        if result["extras"]:
                            st.markdown("#### Skills in your resume this job did not ask for")
                            st.write(", ".join(result["extras"]))
 
                        with st.expander("Skills detected"):
                            left, right = st.columns(2)
                            with left:
                                st.markdown("**In your resume**")
                                st.write(
                                    ", ".join(result["resume_skills"])
                                    or "None detected."
                                )
                            with right:
                                st.markdown("**In the job description**")
                                st.write(
                                    ", ".join(result["job_skills"])
                                    or "None detected."
                                )
 
                        with st.expander("Review extracted resume text"):
                            st.text(resume_text)
 
        except Exception as error:
            st.error(f"Could not read this file: {error}")