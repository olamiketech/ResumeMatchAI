import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import streamlit as st

# Database configuration
# Use external Neon database URL
NEON_DATABASE_URL = "postgresql://neondb_owner:npg_CHkSwBIo0pX6@ep-damp-flower-a8jx8npk-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
DATABASE_URL = NEON_DATABASE_URL

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )
    # Test the connection
    with engine.connect() as conn:
        conn.execute("SELECT 1")
except Exception as e:
    print(f"Database connection failed: {str(e)}")
    # Create a fallback in-memory SQLite database
    engine = create_engine("sqlite:///./resumefit.db", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ResumeAnalysis(Base):
    """Model for storing resume analysis results"""
    __tablename__ = "resume_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)  # To track user sessions
    resume_filename = Column(String(255))
    resume_text = Column(Text)
    job_description = Column(Text)
    similarity_score = Column(Float)
    keyword_match_score = Column(Float)
    skills_match_score = Column(Float)
    final_score = Column(Float)
    missing_keywords = Column(Text)  # JSON string of missing keywords
    matching_keywords = Column(Text)  # JSON string of matching keywords
    suggestions = Column(Text)  # JSON string of suggestions
    created_at = Column(DateTime, default=datetime.utcnow)
    
class UserSession(Base):
    """Model for tracking user sessions"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)
    first_visit = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    total_analyses = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

def init_database():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")
        return False

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

def save_analysis(session_id, resume_filename, resume_text, job_description, results):
    """Save analysis results to database"""
    try:
        db = get_db()
        if not db:
            return False
            
        import json
        import numpy as np
        
        # Convert numpy types to Python native types
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        # Safely convert scores to float with error handling
        def safe_float_convert(value, default=0.0):
            try:
                converted = convert_numpy_types(value)
                return float(converted) if converted is not None else default
            except (ValueError, TypeError):
                return default
        
        similarity_score = safe_float_convert(results.get('similarity_score', 0))
        keyword_match_score = safe_float_convert(results.get('keyword_match_score', 0))
        skills_match_score = safe_float_convert(results.get('skills_match_score', 0))
        final_score = safe_float_convert(results.get('score', 0))
        
        analysis = ResumeAnalysis(
            session_id=session_id,
            resume_filename=resume_filename,
            resume_text=resume_text[:10000],  # Limit text length
            job_description=job_description[:10000],  # Limit text length
            similarity_score=similarity_score,
            keyword_match_score=keyword_match_score,
            skills_match_score=skills_match_score,
            final_score=final_score,
            missing_keywords=json.dumps(results.get('missing_keywords', [])),
            matching_keywords=json.dumps(results.get('matching_keywords', [])),
            suggestions=json.dumps(results.get('suggestions', []))
        )
        
        db.add(analysis)
        db.commit()
        db.close()
        return True
        
    except Exception as e:
        st.error(f"Error saving analysis: {str(e)}")
        return False

def get_user_history(session_id, limit=10):
    """Get user's analysis history"""
    try:
        db = get_db()
        if not db:
            return []
            
        analyses = db.query(ResumeAnalysis).filter(
            ResumeAnalysis.session_id == session_id
        ).order_by(ResumeAnalysis.created_at.desc()).limit(limit).all()
        
        db.close()
        return analyses
        
    except Exception as e:
        st.error(f"Error retrieving history: {str(e)}")
        return []

def update_user_session(session_id):
    """Update or create user session"""
    try:
        db = get_db()
        if not db:
            return
            
        session = db.query(UserSession).filter(
            UserSession.session_id == session_id
        ).first()
        
        if session:
            # Update existing session
            db.query(UserSession).filter(
                UserSession.session_id == session_id
            ).update({
                UserSession.last_activity: datetime.utcnow(),
                UserSession.total_analyses: UserSession.total_analyses + 1
            })
        else:
            # Create new session
            session = UserSession(
                session_id=session_id,
                total_analyses=1
            )
            db.add(session)
        
        db.commit()
        db.close()
        
    except Exception as e:
        st.error(f"Error updating session: {str(e)}")

def get_analytics_data():
    """Get basic analytics data"""
    try:
        db = get_db()
        if not db:
            return {}
            
        total_analyses = db.query(ResumeAnalysis).count()
        total_sessions = db.query(UserSession).count()
        
        # Average scores
        avg_score = db.query(ResumeAnalysis.final_score).all()
        if avg_score:
            avg_score = sum([score[0] for score in avg_score if score[0]]) / len(avg_score)
        else:
            avg_score = 0
        
        db.close()
        
        return {
            'total_analyses': total_analyses,
            'total_sessions': total_sessions,
            'average_score': round(avg_score, 1)
        }
        
    except Exception as e:
        st.error(f"Error getting analytics: {str(e)}")
        return {}