import streamlit as st
import tempfile
import os
from io import StringIO
from utils.pdf_extractor import extract_text_from_pdf
from utils.docx_extractor import extract_text_from_docx
from utils.text_processor import preprocess_text
from utils.resume_analyzer import ResumeAnalyzer
from utils.database import init_database, save_analysis, get_user_history, update_user_session, get_analytics_data
from utils.openai_service import get_openai_service
import uuid

# Page configuration with enhanced styling
st.set_page_config(
    page_title="ResumeFit - AI Resume Optimizer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI/UX
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 0;
    }

    /* Card styling */
    .card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e0e6ed;
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }

    /* Score display styling */
    .score-container {
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }

    .score-large {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
    }

    .score-label {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        cursor: pointer !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) !important;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3) !important;
    }

    /* Fix button focus states */
    .stButton > button:focus {
        outline: 2px solid #667eea !important;
        outline-offset: 2px !important;
    }

    /* Enhanced progress bar styling */
    .stProgress .st-bo {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 16px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }

    .stProgress .st-bo::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: progressShimmer 2s infinite;
    }

    @keyframes progressShimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }

    /* Enhanced alert styling */
    .alert-success {
        background: linear-gradient(135deg, rgba(86, 171, 47, 0.9) 0%, rgba(168, 230, 207, 0.9) 100%);
        backdrop-filter: blur(10px);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 25px rgba(86, 171, 47, 0.3);
    }

    .alert-info {
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.9) 0%, rgba(133, 193, 229, 0.9) 100%);
        backdrop-filter: blur(10px);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 25px rgba(52, 152, 219, 0.3);
    }

    /* Enhanced sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
    }

    /* Enhanced success/error message styling */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important;
    }

    /* File uploader styling */
    .uploadedFile {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
        transition: all 0.2s ease;
    }

    .uploadedFile:hover {
        border-color: #764ba2;
        background: #f0f2ff;
    }

    /* Text area border color override */
    textarea#text_area_1,
    textarea#text_area_1:focus,
    .stTextArea textarea:focus {
        border: 2px solid #667eea !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /* Metric styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }

    /* Metric button styling */
    div[data-testid="column"] .stButton > button {
        background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%) !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        font-weight: 600 !important;
        text-align: center !important;
        white-space: pre-line !important;
        height: 120px !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="column"] .stButton > button:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
    }

    /* Enhanced responsive design */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2rem;
        }

        .header-subtitle {
            font-size: 1rem;
        }

        .card {
            padding: 1.5rem;
            margin-bottom: 1rem;
        }

        .score-large {
            font-size: 2.5rem;
        }

        .metric-card {
            margin-bottom: 0.5rem;
        }

        .stButton > button {
            padding: 0.5rem 1.5rem;
            font-size: 0.9rem;
        }
    }

    @media (max-width: 480px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
            padding-top: 1rem;
        }

        .header-container {
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .header-title {
            font-size: 1.8rem;
        }

        .header-subtitle {
            font-size: 0.9rem;
        }

        .card {
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .score-large {
            font-size: 2rem;
        }

        .metric-card {
            padding: 1rem;
            margin-bottom: 0.5rem;
        }

        .stButton > button {
            padding: 0.5rem 1rem;
            font-size: 0.8rem;
        }

        /* Stack columns on mobile */
        .stColumns {
            flex-direction: column;
        }

        .stColumns > div {
            width: 100% !important;
            margin-bottom: 1rem;
        }
    }

    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .card {
            background: #2b2b2b;
            border-color: #404040;
            color: #ffffff;
        }

        .metric-card {
            background: #2b2b2b;
            border-left-color: #667eea;
        }
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize database with better error handling
try:
    if init_database():
        print("Database initialized successfully")
    else:
        st.warning("Database connection failed. History and analytics features will be limited.")
except Exception as e:
    st.warning(f"Database error: {str(e)}. The app will work without history features.")
    print(f"Database initialization error: {e}")

# Initialize session state
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'user_session_id' not in st.session_state:
    st.session_state.user_session_id = str(uuid.uuid4())

def main():
    # Modern header with gradient background
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🚀 ResumeFit</h1>
        <p class="header-subtitle">AI-Powered Resume Optimizer - Achieve 80%+ Job Match Scores</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for history and analytics
    with st.sidebar:
        st.header("Dashboard")

        # Analytics
        analytics = get_analytics_data()
        if analytics:
            st.subheader("Analytics")
            st.metric("Total Analyses", analytics.get('total_analyses', 0))
            st.metric("Average Score", f"{analytics.get('average_score', 0)}%")
            st.metric("Total Users", analytics.get('total_sessions', 0))

        # Analysis History
        st.subheader("Your History")
        history = get_user_history(st.session_state.user_session_id, limit=5)

        if history:
            for i, analysis in enumerate(history, 1):
                with st.expander(f"Analysis #{i} - {analysis.final_score:.0f}%"):
                    st.write(f"**File:** {analysis.resume_filename}")
                    st.write(f"**Score:** {analysis.final_score:.1f}%")
                    st.write(f"**Date:** {analysis.created_at.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.write("No analysis history yet.")

    # Create responsive columns for upload and job description
    col1, col2 = st.columns([1, 1], gap="large")

    # Store filename for database
    uploaded_filename = "text_input"

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📄 Upload Your Resume")
        st.markdown("*Supported formats: PDF, TXT, DOCX*")

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'txt', 'docx'],
            help="Upload your resume in PDF, TXT, or DOCX format for AI analysis (max 5MB)",
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            # Check file size (5MB limit)
            file_size = len(uploaded_file.getvalue())
            max_size = 5 * 1024 * 1024  # 5MB in bytes

            if file_size > max_size:
                st.error(f"File size ({file_size / (1024*1024):.1f} MB) exceeds the 5MB limit. Please upload a smaller file.")
                return
            uploaded_filename = uploaded_file.name
            try:
                if uploaded_file.type == "application/pdf":
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name

                    # Extract text from PDF
                    resume_text = extract_text_from_pdf(tmp_file_path)

                    # Clean up temporary file
                    os.unlink(tmp_file_path)

                    if resume_text.strip():
                        st.session_state.resume_text = resume_text
                        st.success("Resume uploaded successfully!")
                        with st.expander("View extracted text"):
                            st.text_area("Resume content", resume_text, height=200, disabled=True)
                    else:
                        st.error("Could not extract text from PDF. Please try a different file.")

                elif uploaded_file.type == "text/plain":
                    # Handle text files
                    string_data = StringIO(uploaded_file.getvalue().decode("utf-8"))
                    resume_text = string_data.read()
                    st.session_state.resume_text = resume_text
                    st.success("Resume uploaded successfully!")
                    with st.expander("View uploaded text"):
                        st.text_area("Resume content", resume_text, height=200, disabled=True)

                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    # Handle DOCX files
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name

                    # Extract text from DOCX
                    resume_text = extract_text_from_docx(tmp_file_path)

                    # Clean up temporary file
                    os.unlink(tmp_file_path)

                    if resume_text and resume_text.strip():
                        st.session_state.resume_text = resume_text
                        st.success("Resume uploaded successfully!")
                        with st.expander("View extracted text"):
                            st.text_area("Resume content", resume_text, height=200, disabled=True)
                    else:
                        st.error("Could not extract text from DOCX. Please try a different file.")
                else:
                    st.error("Unsupported file format. Please upload PDF, TXT, or DOCX files.")

            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Target Job Description")
        st.markdown("*Paste the complete job posting for AI optimization*")

        job_description = st.text_area(
            "Job Description",
            placeholder="Paste the full job description here...\n\nInclude:\n• Job title and responsibilities\n• Required skills and qualifications\n• Experience requirements\n• Company information",
            height=300,
            value=st.session_state.job_description,
            label_visibility="collapsed"
        )

        if job_description and job_description.strip():
            st.session_state.job_description = job_description
            st.success(f"✅ Job description loaded ({len(job_description.split())} words)")

        st.markdown('</div>', unsafe_allow_html=True)

    # Enhanced analysis section
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h3 style="color: #667eea; margin-bottom: 1rem;">🔍 Ready to Analyze?</h3>
        <p style="color: #666; margin-bottom: 2rem;">Get your resume compatibility score and AI optimization suggestions</p>
    </div>
    """, unsafe_allow_html=True)

    # Create centered button with custom styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
            if not st.session_state.resume_text or not st.session_state.resume_text.strip():
                st.error("Please upload a resume first.")
                return

            if not st.session_state.job_description or not st.session_state.job_description.strip():
                st.error("Please enter a job description.")
                return

            # Clear previous AI-enhanced results for fresh analysis
            if 'original_resume_text' in st.session_state:
                del st.session_state.original_resume_text
            if 'original_analysis' in st.session_state:
                del st.session_state.original_analysis
            if 'rewritten_resume' in st.session_state:
                del st.session_state.rewritten_resume
            if 'rewritten_analysis' in st.session_state:
                del st.session_state.rewritten_analysis

            # Show loading spinner
            with st.spinner("Analyzing resume..."):
                try:
                    analyzer = ResumeAnalyzer()
                    results = analyzer.analyze_resume(
                        st.session_state.resume_text,
                        st.session_state.job_description
                    )
                    st.session_state.analysis_results = results

                    # Save analysis to database
                    save_analysis(
                        st.session_state.user_session_id,
                        uploaded_filename,
                        st.session_state.resume_text,
                        st.session_state.job_description,
                        results
                    )

                    # Update user session
                    update_user_session(st.session_state.user_session_id)

                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    return

    # Display results
    if st.session_state.analysis_results:
        st.markdown("---")
        display_results(st.session_state.analysis_results)

        # AI-Powered Enhancement Section
        st.markdown("---")
        st.subheader("🤖 AI-Powered Resume Enhancement")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Get AI Tailoring Suggestions", type="secondary"):
                with st.spinner("Generating AI-powered suggestions..."):
                    try:
                        openai_service = get_openai_service()
                        if openai_service:
                            ai_suggestions = openai_service.generate_tailored_suggestions(
                                st.session_state.resume_text,
                                st.session_state.job_description,
                                st.session_state.analysis_results
                            )

                            if ai_suggestions:
                                st.session_state.ai_suggestions = ai_suggestions
                                st.success("AI suggestions generated!")
                            else:
                                st.error("Failed to generate AI suggestions.")
                        else:
                            st.error("OpenAI service not available.")
                    except Exception as e:
                        st.error(f"Error generating AI suggestions: {str(e)}")

        with col2:
            # Show different optimization options based on current score
            current_score = st.session_state.analysis_results.get('score', 0)

            if current_score < 85:
                button_text = "🚀 MAXIMUM AI Optimization"
                button_help = "Aggressive transformation for dramatic improvement"
            else:
                button_text = "🔥 AI Rewrite Resume" 
                button_help = "Standard AI optimization"

            if st.button(button_text, type="primary", help=button_help):
                with st.spinner("AI is performing advanced resume transformation..."):
                    openai_service = get_openai_service()
                    if openai_service:
                        # Always store original resume and analysis before any rewriting
                        if 'original_resume_text' not in st.session_state:
                            st.session_state.original_resume_text = st.session_state.resume_text
                            st.session_state.original_analysis = st.session_state.analysis_results

                        # Use aggressive transformation for low scores, extreme for high scores  
                        if current_score < 85:
                            rewritten_resume = openai_service.extreme_resume_transformation(
                                st.session_state.original_resume_text,
                                st.session_state.job_description,
                                st.session_state.original_analysis
                            )
                        else:
                            # For already high-scoring resumes, use extreme transformation too
                            rewritten_resume = openai_service.extreme_resume_transformation(
                                st.session_state.original_resume_text,
                                st.session_state.job_description,
                                st.session_state.original_analysis
                            )

                        if rewritten_resume:
                            st.session_state.rewritten_resume = rewritten_resume

                            # Analyze the rewritten resume
                            analyzer = ResumeAnalyzer()
                            new_results = analyzer.analyze_resume(
                                rewritten_resume,
                                st.session_state.job_description
                            )
                            st.session_state.rewritten_analysis = new_results

                            improvement = new_results['score'] - st.session_state.original_analysis['score']
                            if improvement > 10:
                                st.success(f"🎉 Dramatic improvement achieved! +{improvement:.1f}% increase!")
                            else:
                                st.success("Resume rewritten and analyzed!")
                        else:
                            st.error("Failed to rewrite resume.")
                    else:
                        st.error("OpenAI service not available.")

        with col3:
            if st.button("Generate Cover Letter", type="secondary"):
                with st.spinner("Creating cover letter draft..."):
                    openai_service = get_openai_service()
                    if openai_service:
                        cover_letter = openai_service.generate_cover_letter_draft(
                            st.session_state.resume_text,
                            st.session_state.job_description
                        )

                        if cover_letter:
                            st.session_state.cover_letter = cover_letter
                            st.success("Cover letter draft created!")
                        else:
                            st.error("Failed to generate cover letter.")
                    else:
                        st.error("OpenAI service not available.")

        # Reset button if there's a rewritten version
        if 'rewritten_resume' in st.session_state and st.session_state.rewritten_resume:
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("🔄 Reset to Original", type="secondary", use_container_width=True, help="Start fresh with your original resume"):
                    # Clear all AI-enhanced results
                    for key in ['original_resume_text', 'original_analysis', 'rewritten_resume', 'rewritten_analysis', 'ai_suggestions', 'cover_letter']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.success("Reset to original resume!")

        # Display rewritten resume and comparison
        if 'rewritten_resume' in st.session_state and st.session_state.rewritten_resume:
            display_rewritten_resume_comparison(
                st.session_state.rewritten_resume,
                st.session_state.analysis_results,
                st.session_state.rewritten_analysis
            )

        # Display AI suggestions
        if 'ai_suggestions' in st.session_state and st.session_state.ai_suggestions:
            display_ai_suggestions(st.session_state.ai_suggestions)

        # Display cover letter
        if 'cover_letter' in st.session_state and st.session_state.cover_letter:
            display_cover_letter(st.session_state.cover_letter)

def display_results(results):
    """Display analysis results with modern UI"""

    # Modern header for results section
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #667eea; margin-bottom: 0.5rem;">📊 Resume Analysis Results</h2>
        <p style="color: #666;">Your compatibility score and optimization insights</p>
    </div>
    """, unsafe_allow_html=True)

    # Score display with modern styling and dynamic colors
    score = results['score']

    # Dynamic color based on score with better contrast
    if score >= 85:
        score_color = "#27ae60"  # Green for excellent
        score_secondary = "#2ecc71"
    elif score >= 75:
        score_color = "#f39c12"  # Orange for good
        score_secondary = "#e67e22"
    elif score >= 50:
        score_color = "#3498db"  # Blue for moderate
        score_secondary = "#2980b9"
    else:
        score_color = "#e74c3c"  # Red for needs improvement
        score_secondary = "#c0392b"

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {score_color} 0%, {score_secondary} 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: none;
        cursor: default;
    ">
        <div style="font-size: 3rem; font-weight: 700; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
            {score:.0f}%
        </div>
        <div style="font-size: 1.1rem; opacity: 0.95; margin-top: 0.5rem; font-weight: 500;">
            Compatibility Score
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Interactive metric buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        content_score = results.get('similarity_score', 0)
        if st.button(f"📊 Content Similarity\n{content_score:.0f}%", key="content_btn", use_container_width=True):
            st.info(f"**Content Similarity: {content_score:.1f}%**\n\nThis measures how well your resume content matches the job description. A higher score means better alignment with the role requirements.")

    with col2:
        keyword_score = results.get('keyword_match_score', 0)
        if st.button(f"🔍 Keyword Match\n{keyword_score:.0f}%", key="keyword_btn", use_container_width=True):
            matched_keywords = len(results.get('matching_keywords', []))
            total_keywords = matched_keywords + len(results.get('missing_keywords', []))
            st.info(f"**Keyword Match: {keyword_score:.1f}%**\n\nFound {matched_keywords} out of {total_keywords} relevant keywords from the job posting in your resume.")

    with col3:
        skills_score = results.get('skills_match_score', 0)
        if st.button(f"🎯 Skills Match\n{skills_score:.0f}%", key="skills_btn", use_container_width=True):
            st.info(f"**Skills Match: {skills_score:.1f}%**\n\nThis shows how well your listed skills align with the job requirements. Consider highlighting missing skills if you have them.")

    # Suggestions section with modern styling
    if results['suggestions']:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 💡 Optimization Suggestions")

        for i, suggestion in enumerate(results['suggestions'], 1):
            st.markdown(f"""
            <div style="background: #f8f9ff; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #667eea;">
                <strong>Suggestion {i}:</strong><br>
                {suggestion}
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Keywords analysis in expandable sections
    col1, col2 = st.columns(2)

    with col1:
        if results.get('missing_keywords'):
            with st.expander("🔍 Missing Keywords", expanded=False):
                st.markdown("Add these relevant keywords to improve your score:")
                for keyword in results['missing_keywords'][:10]:
                    st.markdown(f"• **{keyword}**")

    with col2:
        if results.get('matching_keywords'):
            with st.expander("✅ Matching Keywords", expanded=False):
                st.markdown("These keywords were successfully found:")
                for keyword in results['matching_keywords'][:15]:
                    st.markdown(f"✓ {keyword}")

def display_ai_suggestions(ai_suggestions):
    """Display AI-powered suggestions"""
    st.subheader("🎯 AI Tailoring Recommendations")

    # Overall Assessment
    if ai_suggestions.get('overall_assessment'):
        st.info(ai_suggestions['overall_assessment'])

    # Key Improvements
    if ai_suggestions.get('key_improvements'):
        st.subheader("🔧 Key Improvements")
        for improvement in ai_suggestions['key_improvements']:
            st.write(f"• {improvement}")

    # Content in expandable sections
    col1, col2 = st.columns(2)

    with col1:
        # Missing Skills
        if ai_suggestions.get('missing_skills'):
            with st.expander("📚 Skills to Highlight"):
                for skill in ai_suggestions['missing_skills']:
                    st.write(f"• {skill}")

        # Keyword Optimization
        if ai_suggestions.get('keyword_optimization'):
            with st.expander("🔍 Keywords to Add"):
                for keyword in ai_suggestions['keyword_optimization']:
                    st.write(f"• {keyword}")

    with col2:
        # Content Restructuring
        if ai_suggestions.get('content_restructuring'):
            with st.expander("📋 Content Structure"):
                for suggestion in ai_suggestions['content_restructuring']:
                    st.write(f"• {suggestion}")

        # Achievement Enhancement
        if ai_suggestions.get('achievement_enhancement'):
            with st.expander("🏆 Achievement Tips"):
                for achievement in ai_suggestions['achievement_enhancement']:
                    st.write(f"• {achievement}")

def display_rewritten_resume_comparison(rewritten_resume, original_analysis, rewritten_analysis):
    """Display rewritten resume with before/after comparison"""

    # Modern header for AI rewrite section
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0 2rem 0;">
        <h2 style="color: #667eea; margin-bottom: 0.5rem;">🔥 AI-Rewritten Resume & Performance Comparison</h2>
        <p style="color: #666;">See how AI optimization transformed your resume</p>
    </div>
    """, unsafe_allow_html=True)

    # Use preserved original data for accurate comparison
    if 'original_analysis' in st.session_state:
        original_data = st.session_state.original_analysis
    else:
        original_data = original_analysis

    # Enhanced score comparison with modern cards
    score_improvement = rewritten_analysis['score'] - original_data['score']
    improvement_percentage = (score_improvement / original_data['score']) * 100 if original_data['score'] > 0 else 0

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <h3 style="color: #e74c3c; margin-bottom: 0.5rem;">Original Score</h3>
            <div style="font-size: 2.5rem; font-weight: 700; color: #e74c3c; margin: 1rem 0;">
                {original_data['score']:.0f}%
            </div>
            <p style="color: #666; margin: 0;">Your baseline compatibility</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <h3 style="color: #27ae60; margin-bottom: 0.5rem;">AI-Optimized Score</h3>
            <div style="font-size: 2.5rem; font-weight: 700; color: #27ae60; margin: 1rem 0;">
                {rewritten_analysis['score']:.0f}%
            </div>
            <p style="color: #666; margin: 0;">After AI optimization</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        improvement_color = "#27ae60" if score_improvement > 0 else "#e74c3c"
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <h3 style="color: {improvement_color}; margin-bottom: 0.5rem;">+{score_improvement:.1f}%</h3>
            <div style="font-size: 2rem; font-weight: 700; color: {improvement_color}; margin: 1rem 0;">
                Improvement
            </div>
            <p style="color: #666; margin: 0;">+{improvement_percentage:.1f}% better match</p>
        </div>
        """, unsafe_allow_html=True)

    # Performance breakdown comparison
    st.subheader("📊 Detailed Performance Breakdown")

    comparison_data = {
        "Metric": ["Overall Match", "Keyword Match", "Skills Match", "Content Similarity"],
        "Original Resume": [
            f"{original_data['score']:.1f}%",
            f"{original_data.get('keyword_match_score', 0):.1f}%",
            f"{original_data.get('skills_match_score', 0):.1f}%",
            f"{original_data.get('similarity_score', 0):.1f}%"
        ],
        "AI-Optimized Resume": [
            f"{rewritten_analysis['score']:.1f}%",
            f"{rewritten_analysis.get('keyword_match_score', 0):.1f}%",
            f"{rewritten_analysis.get('skills_match_score', 0):.1f}%",
            f"{rewritten_analysis.get('similarity_score', 0):.1f}%"
        ]
    }

    st.table(comparison_data)

    # Display the rewritten resume with modern styling
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📄 Your AI-Optimized Resume")
    st.markdown("*Ready to copy and use for your job application*")

    # Show rewritten resume in expandable text area
    with st.expander("View AI-Rewritten Resume", expanded=True):
        st.text_area(
            "AI-Optimized Resume",
            value=rewritten_resume,
            height=500,
            help="Copy this optimized resume for your job application",
            label_visibility="collapsed"
        )

    # Modern action buttons
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        st.download_button(
            label="📥 Download Optimized Resume",
            data=rewritten_resume,
            file_name="ai_optimized_resume.txt",
            mime="text/plain",
            type="primary",
            use_container_width=True
        )

    with col2:
        if st.button("💾 Save to History", type="secondary", use_container_width=True):
            save_analysis(
                st.session_state.user_session_id,
                "AI_optimized_resume.txt",
                rewritten_resume,
                st.session_state.job_description,
                rewritten_analysis
            )
            st.success("✅ Saved to your analysis history!")

    st.markdown('</div>', unsafe_allow_html=True)

def display_cover_letter(cover_letter):
    """Display generated cover letter"""
    st.subheader("📝 AI-Generated Cover Letter Draft")

    # Display cover letter in a text area for easy copying
    st.text_area(
        "Cover Letter Draft",
        value=cover_letter,
        height=400,
        help="You can copy this text and customize it further for your application."
    )

    # Download button
    st.download_button(
        label="Download Cover Letter",
        data=cover_letter,
        file_name="cover_letter_draft.txt",
        mime="text/plain"
    )

if __name__ == "__main__":
    main()