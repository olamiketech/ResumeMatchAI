# ResumeFit - AI Resume Optimizer

## Overview

ResumeFit is a Streamlit-based web application that analyzes and optimizes resumes against job descriptions using AI-powered text analysis. The application extracts text from uploaded resume files (PDF, TXT, DOCX), compares it with job descriptions, and provides matching scores and optimization suggestions.

## System Architecture

**Frontend Framework**: Streamlit - chosen for rapid prototyping and built-in UI components for file uploads and data visualization
**Backend Logic**: Python-based modular architecture with utility classes
**Text Processing**: NLTK for natural language processing tasks
**Machine Learning**: Scikit-learn for TF-IDF vectorization and cosine similarity calculations
**File Processing**: PyPDF2 for PDF text extraction

## Key Components

### 1. Main Application (`app.py`)
- **Purpose**: Entry point and UI orchestration
- **Architecture**: Session state management for user data persistence
- **Features**: Two-column layout for resume upload and job description input
- **File Support**: PDF, TXT, and DOCX formats

### 2. PDF Text Extraction (`utils/pdf_extractor.py`)
- **Purpose**: Extract readable text from PDF files
- **Implementation**: PyPDF2-based extraction with error handling
- **Features**: PDF validation and multi-page text extraction
- **Error Handling**: Graceful failure with user feedback

### 3. Text Processing (`utils/text_processor.py`)
- **Purpose**: Natural language processing and text normalization
- **Implementation**: NLTK-based processing with custom stopwords
- **Features**: 
  - Text cleaning and normalization
  - Keyword extraction
  - Skills identification
  - Stemming and tokenization
- **Customization**: Extended stopwords list for resume-specific terms

### 4. Resume Analysis (`utils/resume_analyzer.py`)
- **Purpose**: Core matching algorithm between resume and job description
- **Implementation**: TF-IDF vectorization with cosine similarity
- **Features**:
  - Similarity score calculation
  - Keyword matching analysis
  - Skills gap identification
  - Optimization suggestions
- **Algorithm**: Uses n-gram range (1,2) for better context understanding

### 5. Database Layer (`utils/database.py`)
- **Purpose**: Persistent storage and analytics
- **Implementation**: SQLAlchemy ORM with PostgreSQL
- **Features**:
  - Resume analysis history storage
  - User session tracking
  - Analytics and metrics
  - Analysis results persistence
- **Models**: ResumeAnalysis, UserSession tables

### 6. AI Enhancement Service (`utils/openai_service.py`)
- **Purpose**: AI-powered resume optimization and tailoring
- **Implementation**: OpenAI GPT-4o API integration
- **Features**:
  - Intelligent resume tailoring suggestions
  - Automated cover letter generation
  - Keyword optimization recommendations
  - Content restructuring advice
  - Achievement enhancement tips
- **Model**: Uses GPT-4o for comprehensive analysis and suggestions

## Data Flow

1. **File Upload**: User uploads resume file through Streamlit interface
2. **Text Extraction**: PDF/document content extracted to plain text
3. **Text Preprocessing**: Both resume and job description texts are cleaned and normalized
4. **Feature Extraction**: TF-IDF vectorization converts texts to numerical representations
5. **Similarity Analysis**: Cosine similarity calculation between resume and job description vectors
6. **Keyword Analysis**: Extraction and comparison of key terms and skills
7. **Results Generation**: Matching score, keyword gaps, and optimization suggestions
8. **UI Display**: Results presented through Streamlit components

## External Dependencies

### Core Libraries
- **Streamlit (≥1.46.1)**: Web application framework
- **NLTK (≥3.9.1)**: Natural language processing
- **Scikit-learn (≥1.7.0)**: Machine learning algorithms
- **PyPDF2 (≥3.0.1)**: PDF text extraction
- **NumPy (≥2.3.1)**: Numerical computations

### NLTK Data Requirements
- **punkt**: Sentence tokenization
- **stopwords**: English stopwords corpus
- **Automatic Download**: Implemented with fallback downloading

## Deployment Strategy

**Platform**: Replit with autoscale deployment target
**Runtime**: Python 3.11 with Nix package management
**Port Configuration**: Application runs on port 5000
**Process Management**: Streamlit server with headless configuration
**Scalability**: Autoscale deployment for handling variable traffic

### Configuration Files
- **.replit**: Deployment and workflow configuration
- **pyproject.toml**: Python project dependencies
- **.streamlit/config.toml**: Streamlit server settings

## Architecture Decisions

### 1. Modular Utility Structure
- **Problem**: Separation of concerns for maintainability
- **Solution**: Utils package with specialized modules
- **Benefits**: Easy testing, code reusability, clear responsibilities

### 2. TF-IDF + Cosine Similarity
- **Problem**: Semantic matching between resume and job description
- **Solution**: TF-IDF vectorization with cosine similarity
- **Rationale**: Balances accuracy with computational efficiency
- **Alternative**: Could use more advanced NLP models (BERT, etc.) but chosen approach provides good results with lower resource requirements

### 3. Session State Management
- **Problem**: Maintaining user data across Streamlit interactions
- **Solution**: Streamlit session state for data persistence
- **Benefits**: Smooth user experience without data loss on interactions

### 4. Error Handling Strategy
- **Problem**: Graceful handling of file processing errors
- **Solution**: Try-catch blocks with user-friendly error messages
- **Implementation**: Validation functions and fallback mechanisms

## Recent Changes

```
- June 27, 2025: Major UI/UX Enhancement
  - Modern card-based design with gradient themes
  - Fully responsive layout for mobile, tablet, and desktop
  - Enhanced color scheme with purple gradient accents
  - Improved button styling with hover effects
  - Mobile-optimized typography and spacing
  - Dark mode support and accessibility improvements
- June 27, 2025: Enhanced AI Algorithm Performance
  - Aggressive keyword optimization for 80%+ match scores
  - Improved partial keyword matching and phrase detection
  - Enhanced TF-IDF analysis with trigram support
  - Keyword bonus scoring system (+20% potential boost)
  - Optimized AI prompts for better resume rewriting
- June 27, 2025: Added AI Resume Rewriting Feature
  - Complete resume rewriting using GPT-4o to match job descriptions
  - Before/after performance comparison with detailed metrics
  - Score improvement tracking and analysis
  - Download and save optimized resumes
- June 27, 2025: Added OpenAI GPT-4o integration
  - AI-powered resume tailoring suggestions
  - Automated cover letter generation
  - Intelligent keyword optimization recommendations
  - Content restructuring and achievement enhancement tips
- June 27, 2025: Added PostgreSQL database integration
  - User session tracking and analysis history
  - Analytics dashboard with metrics
  - Persistent storage of resume analysis results
  - SQLAlchemy ORM for database operations
- June 27, 2025: Added DOCX file support  
  - python-docx library integration
  - Support for PDF, TXT, and DOCX resume uploads
- June 27, 2025: Fixed NLTK compatibility issues
  - Updated punkt tokenizer downloads
  - Improved error handling
- June 27, 2025: Initial setup completed
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```