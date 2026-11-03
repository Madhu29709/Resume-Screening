import streamlit as st
import pickle
import re
import io

from pypdf import PdfReader
from docx import Document


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Resume Screening",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #0E1117;
}

[data-testid="stSidebar"] {
    background-color: #171B26;
}

.main-title {
    font-size: 34px;
    font-weight: 700;
    color: #FFFFFF;
}

.subtitle {
    color: #A0AEC0;
    font-size: 15px;
}

.section-title {
    font-size: 22px;
    font-weight: 600;
    color: #FFFFFF;
    margin-top: 20px;
}

.metric-card {
    background: linear-gradient(135deg, #1D293B, #263B56);
    padding: 25px;
    border-radius: 12px;
    border: 1px solid #334155;
    min-height: 120px;
}

.metric-label {
    color: #A0AEC0;
    font-size: 14px;
}

.metric-value {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: bold;
    margin-top: 10px;
}

.result-card {
    background: linear-gradient(135deg, #123B35, #145A4A);
    padding: 30px;
    border-radius: 15px;
    border: 1px solid #21866D;
}

.result-label {
    color: #A7F3D0;
    font-size: 15px;
}

.result-value {
    color: white;
    font-size: 30px;
    font-weight: bold;
    margin-top: 10px;
}

.upload-box {
    background-color: #1B2433;
    padding: 25px;
    border-radius: 12px;
    border: 1px solid #334155;
}

div.stButton > button {
    background-color: #2563EB;
    color: white;
    border-radius: 8px;
    border: none;
    height: 45px;
    font-weight: 600;
    width: 100%;
}

div.stButton > button:hover {
    background-color: #1D4ED8;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# LOAD MODEL
# ==========================================

@st.cache_resource
def load_models():

    with open("clf.pkl", "rb") as f:
        clf = pickle.load(f)

    with open("tfidf.pkl", "rb") as f:
        tfidf = pickle.load(f)

    return clf, tfidf


clf, tfidf = load_models()


# ==========================================
# CATEGORY MAPPING
# ==========================================

category_mapping = {
    0: 'Advocate',
    1: 'Arts',
    2: 'Automation Testing',
    3: 'Blockchain',
    4: 'Business Analyst',
    5: 'Civil Engineer',
    6: 'Data Science',
    7: 'Database',
    8: 'DevOps Engineer',
    9: 'DotNet Developer',
    10: 'ETL Developer',
    11: 'Electrical Engineering',
    12: 'HR',
    13: 'Hadoop',
    14: 'Health and fitness',
    15: 'Java Developer',
    16: 'Mechanical Engineer',
    17: 'Network Security Engineer',
    18: 'Operations Manager',
    19: 'PMO',
    20: 'Python Developer',
    21: 'SAP Developer',
    22: 'Sales',
    23: 'Testing',
    24: 'Web Designing'
}


# ==========================================
# RESUME CLEANING
# ==========================================

def cleanResume(txt):

    txt = re.sub(r'http\S+\s', ' ', txt)
    txt = re.sub(r'RT|cc', ' ', txt)
    txt = re.sub(r'#\S+\s', ' ', txt)
    txt = re.sub(r'@\S+', ' ', txt)

    txt = re.sub(
        r"""[!"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~]""",
        ' ',
        txt
    )

    txt = re.sub(r'[^\x00-\x7f]', ' ', txt)
    txt = re.sub(r'\s+', ' ', txt)

    return txt.strip()


# ==========================================
# EXTRACT RESUME TEXT
# ==========================================

def extract_text(uploaded_file):

    extension = uploaded_file.name.split(".")[-1].lower()

    if extension == "pdf":

        pdf = PdfReader(io.BytesIO(uploaded_file.getvalue()))

        text = ""

        for page in pdf.pages:
            text += page.extract_text() or ""

        return text

    elif extension == "docx":

        doc = Document(io.BytesIO(uploaded_file.getvalue()))

        return "\n".join(
            paragraph.text for paragraph in doc.paragraphs
        )

    elif extension == "txt":

        return uploaded_file.getvalue().decode("utf-8")

    return ""


# ==========================================
# EXTRACT RESUME INFORMATION
# ==========================================

def extract_information(text):

    email = re.findall(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        text
    )

    phone = re.findall(
        r'\+?\d[\d\s\-()]{8,}\d',
        text
    )

    return {
        "email": email[0] if email else "Not found",
        "phone": phone[0] if phone else "Not found"
    }


# ==========================================
# SKILLS EXTRACTION
# ==========================================

def extract_skills(text):

    skills_list = [
        "Python", "Java", "C++", "C",
        "SQL", "MySQL", "PostgreSQL",
        "Machine Learning", "Deep Learning",
        "Data Science", "Data Analytics",
        "Pandas", "NumPy", "Scikit-learn",
        "TensorFlow", "PyTorch",
        "HTML", "CSS", "JavaScript",
        "React", "Node.js", "Django",
        "Flask", "FastAPI", "Spring Boot",
        "AWS", "Azure", "Docker",
        "Kubernetes", "Git", "GitHub",
        "Power BI", "Tableau",
        "NLP", "Artificial Intelligence",
        "Excel", "Communication",
        "Leadership", "Project Management"
    ]

    found_skills = []

    for skill in skills_list:

        pattern = r'(?<!\w)' + re.escape(skill) + r'(?!\w)'

        if re.search(pattern, text, re.IGNORECASE):

            found_skills.append(skill)

    return found_skills


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("## 📄 ResumeAI")

    st.caption("AI-Powered Resume Screening")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📊 About Project"
        ]
    )

    st.divider()

    st.markdown("### Supported Formats")

    st.write("📄 PDF")
    st.write("📝 DOCX")
    st.write("📃 TXT")

    st.divider()

    st.caption("Powered by Python & Machine Learning")


# ==========================================
# DASHBOARD
# ==========================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="main-title">AI Resume Screening System</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Upload, analyze and classify resumes using Machine Learning.</div>',
        unsafe_allow_html=True
    )

    st.divider()

    # Upload section

    st.markdown(
        '<div class="section-title">📤 Upload Your Resume</div>',
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Choose your resume",
        type=["pdf", "docx", "txt"]
    )

    if uploaded_file:

        st.success(f"Uploaded successfully: {uploaded_file.name}")

    analyze = st.button(
        "🔍 Analyze Resume",
        disabled=uploaded_file is None
    )

    if analyze:

        try:

            with st.spinner("Analyzing your resume..."):

                resume_text = extract_text(uploaded_file)

                if not resume_text.strip():

                    st.error(
                        "No text found. Please upload a text-based resume."
                    )

                else:

                    cleaned_resume = cleanResume(resume_text)

                    input_features = tfidf.transform(
                        [cleaned_resume]
                    )

                    prediction_id = int(
                        clf.predict(input_features)[0]
                    )

                    category_name = category_mapping.get(
                        prediction_id,
                        "Unknown"
                    )

                    information = extract_information(resume_text)

                    skills = extract_skills(resume_text)

                    st.session_state["result"] = {
                        "category": category_name,
                        "prediction_id": prediction_id,
                        "information": information,
                        "skills": skills,
                        "resume_text": resume_text,
                        "filename": uploaded_file.name,
                        "features": input_features
                    }

        except Exception as e:

            st.error(f"Something went wrong: {e}")


    # ======================================
    # DISPLAY RESULTS
    # ======================================

    if "result" in st.session_state:

        result = st.session_state["result"]

        st.divider()

        st.markdown(
            '<div class="section-title">📊 Resume Analysis Results</div>',
            unsafe_allow_html=True
        )

        st.success("Resume analyzed successfully!")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(f"""
            <div class="result-card">
                <div class="result-label">Predicted Job Category</div>
                <div class="result-value">{result['category']}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Category ID</div>
                <div class="metric-value">{result['prediction_id']}</div>
            </div>
            """, unsafe_allow_html=True)


        # ==================================
        # PERSONAL INFORMATION
        # ==================================

        st.markdown(
            '<div class="section-title">👤 Resume Information</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("**Email Address**")

            st.write(result["information"]["email"])

        with col2:

            st.markdown("**Phone Number**")

            st.write(result["information"]["phone"])


        # ==================================
        # SKILLS
        # ==================================

        st.markdown(
            '<div class="section-title">💡 Skills Identified</div>',
            unsafe_allow_html=True
        )

        if result["skills"]:

            st.write("Skills found in your resume:")

            st.write(" | ".join(result["skills"]))

        else:

            st.info("No matching skills found.")


        # ==================================
        # TOP 3 PREDICTIONS
        # ==================================

        st.markdown(
            '<div class="section-title">🏆 Top Job Categories</div>',
            unsafe_allow_html=True
        )

        if hasattr(clf, "predict_proba"):

            probabilities = clf.predict_proba(
                result["features"]
            )[0]

            top_indices = probabilities.argsort()[::-1][:3]

            for index in top_indices:

                class_id = int(clf.classes_[index])

                name = category_mapping.get(
                    class_id,
                    "Unknown"
                )

                score = float(probabilities[index])

                st.write(f"**{name}**")

                st.progress(score)

                st.caption(
                    f"Model score: {score * 100:.2f}%"
                )

        else:

            st.info("Probability scores are not available for this model.")


        # ==================================
        # RESUME PREVIEW
        # ==================================

        st.markdown(
            '<div class="section-title">📄 Resume Preview</div>',
            unsafe_allow_html=True
        )

        with st.expander("View Extracted Resume Text"):

            st.text(result["resume_text"])


        # ==================================
        # DOWNLOAD REPORT
        # ==================================

        report = f"""
AI RESUME SCREENING REPORT

File Name: {result['filename']}

Predicted Category: {result['category']}

Category ID: {result['prediction_id']}

Email: {result['information']['email']}

Phone: {result['information']['phone']}

Skills Identified:
{', '.join(result['skills'])}

-----------------------------------

Extracted Resume Text:

{result['resume_text']}
"""

        st.download_button(
            label="📥 Download Analysis Report",
            data=report,
            file_name="Resume_Analysis_Report.txt",
            mime="text/plain",
            use_container_width=True
        )


# ==========================================
# ABOUT PROJECT
# ==========================================

elif page == "📊 About Project":

    st.title("About ResumeAI")

    st.write(
        """
        ResumeAI is a Machine Learning-based Resume Screening
        System that automatically classifies resumes into
        different job categories.
        """
    )

    st.subheader("Technology Stack")

    st.write("""
    - Python
    - Streamlit
    - Scikit-learn
    - TF-IDF Vectorization
    - K-Nearest Neighbors (KNN)
    - Regular Expressions
    """)

    st.subheader("Available Job Categories")

    for category_id, category in category_mapping.items():

        st.write(f"{category_id}. {category}")

    st.divider()

    st.caption("AI Resume Screening System | Machine Learning Project")
    