import pymupdf
import streamlit as st
import requests
from docx import Document


# CareerFit Frontend
st.set_page_config(page_title="CareerFit", page_icon="💼")

st.title("💼 CareerFit")
st.write(
    "Compare the skills in your resume "
    "with the skills required by a job."
)


# Extract text from PDF
def extract_text_from_pdf(uploaded_file):
    pdf = pymupdf.open(
        stream=uploaded_file.getvalue(),
        filetype="pdf"
    )

    try:
        text = "\n".join(page.get_text() for page in pdf)
    finally:
        pdf.close()

    return text


# Extract text from DOCX
def extract_text_from_docx(uploaded_file):
    document = Document(uploaded_file)

    parts = [
        paragraph.text
        for paragraph in document.paragraphs
    ]

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                parts.append(cell.text)

    return "\n".join(parts)


# User inputs
resume_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"]
)

job_description = st.text_area(
    "Paste the job description",
    height=220
)


# Compare skills
if st.button("Compare Skills"):

    if resume_file is None:
        st.warning("Please upload a PDF or DOCX resume.")

    elif not job_description.strip():
        st.warning("Please paste a job description.")

    else:
        try:
            # Step 1: Extract resume text
            if resume_file.name.lower().endswith(".pdf"):
                resume_text = extract_text_from_pdf(resume_file)
            else:
                resume_text = extract_text_from_docx(resume_file)

            if not resume_text.strip():
                st.error(
                    "No readable text was found. "
                    "The PDF may be scanned or image-based."
                )

            else:
                # Step 2: Send data to FastAPI
                response = requests.post(
                    "http://127.0.0.1:8000/match",
                    json={
                        "cv_text": resume_text,
                        "job_text": job_description
                    },
                    timeout=30
                )

                response.raise_for_status()

                # Step 3: Read API response
                result = response.json()

                # Step 4: Display results
                if result["score"] is None:
                    st.warning(
                        "No technical skills were detected "
                        "in the job description."
                    )

                else:
                    st.metric(
                        "Technical Skill Match",
                        f"{result['score']}%"
                    )

                    matched_skills = result["matched_skills"]
                    missing_skills = result["missing_skills"]
                    total_required = result["total_required"]

                    st.caption(
                        f"{len(matched_skills)} of "
                        f"{total_required} required technical "
                        "skills were found in your resume. "
                        "This is a keyword-based comparison."
                    )

                    st.subheader("Skills Comparison")

                    matched_col, missing_col = st.columns(2)

                    with matched_col:
                        st.markdown("#### Matched Skills")

                        if matched_skills:
                            for skill in matched_skills:
                                st.success(skill)
                        else:
                            st.info("No matching skills detected.")

                    with missing_col:
                        st.markdown("#### Missing Skills")

                        if missing_skills:
                            for skill in missing_skills:
                                st.warning(skill)
                        else:
                            st.success("No missing skills detected.")

                # Show extracted resume text
                with st.expander("Review Extracted Resume Text"):
                    st.text(resume_text)

        except requests.exceptions.RequestException as error:
            st.error(
                f"Could not connect to CareerFit API: {error}"
            )

        except Exception as error:
            st.error(f"An error occurred: {error}")