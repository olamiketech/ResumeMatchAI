import os
import json
from openai import OpenAI
import streamlit as st

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize OpenAI client safely; avoid crashing during import if API key is absent
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as _e:
    openai_client = None  # Will attempt lazy initialization later
    # Log warning instead of raising to keep the app running without OpenAI features
    print(f"Warning: OpenAI client not initialized at import time: {_e}")

class OpenAIService:
    def __init__(self):
        global openai_client
        # Lazy initialize the OpenAI client if it wasn't created during import
        if openai_client is None:
            try:
                from openai import OpenAI as _OpenAI
                openai_client = _OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            except Exception as _e:
                st.error(f"OpenAI client initialization error: {_e}")
        self.client = openai_client
        
    def generate_tailored_suggestions(self, resume_text, job_description, analysis_results):
        """
        Generate AI-powered tailored suggestions for resume improvement
        
        Args:
            resume_text (str): Original resume text
            job_description (str): Job description text
            analysis_results (dict): Results from the basic analysis
            
        Returns:
            dict: AI-generated suggestions and improvements
        """
        try:
            prompt = f"""
            You are an expert resume coach and career advisor. Analyze the following resume and job description to provide specific, actionable improvements.

            RESUME:
            {resume_text[:3000]}

            JOB DESCRIPTION:
            {job_description[:2000]}

            CURRENT ANALYSIS SCORE: {analysis_results.get('score', 0):.1f}%

            Please provide a comprehensive analysis with specific recommendations in JSON format:
            {{
                "overall_assessment": "Brief overall assessment of the resume-job fit",
                "key_improvements": [
                    "Specific improvement 1",
                    "Specific improvement 2",
                    "Specific improvement 3"
                ],
                "missing_skills": [
                    "Technical skill 1",
                    "Technical skill 2"
                ],
                "keyword_optimization": [
                    "Important keyword 1 to add",
                    "Important keyword 2 to add"
                ],
                "content_restructuring": [
                    "Restructuring suggestion 1",
                    "Restructuring suggestion 2"
                ],
                "achievement_enhancement": [
                    "How to better quantify achievement 1",
                    "How to better quantify achievement 2"
                ]
            }}

            Focus on:
            1. Specific keywords and phrases from the job description
            2. Skills gaps that need to be addressed
            3. How to reframe existing experience to match job requirements
            4. Quantifiable achievements that should be highlighted
            5. Industry-specific language and terminology
            """

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume coach. Provide specific, actionable advice in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                return result
            return None
            
        except Exception as e:
            st.error(f"Error generating AI suggestions: {str(e)}")
            return None
    
    def rewrite_bullet_points(self, bullet_points, job_description):
        """
        Rewrite resume bullet points to better match job requirements
        
        Args:
            bullet_points (list): List of original bullet points
            job_description (str): Job description text
            
        Returns:
            list: Improved bullet points
        """
        try:
            bullet_text = "\n".join([f"• {point}" for point in bullet_points])
            
            prompt = f"""
            Rewrite these resume bullet points to better align with the job requirements while maintaining truthfulness.
            
            ORIGINAL BULLET POINTS:
            {bullet_text}
            
            JOB DESCRIPTION:
            {job_description[:1500]}
            
            Please rewrite each bullet point to:
            1. Use stronger action verbs
            2. Include relevant keywords from the job description
            3. Add quantifiable metrics where possible
            4. Match the tone and language of the job posting
            5. Maintain accuracy and truthfulness
            
            Return as a JSON array of improved bullet points:
            {{
                "improved_bullets": [
                    "Improved bullet point 1",
                    "Improved bullet point 2"
                ]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume writer. Improve bullet points while maintaining truthfulness."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000,
                temperature=0.6
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                return result.get('improved_bullets', bullet_points)
            return bullet_points
            
        except Exception as e:
            st.error(f"Error rewriting bullet points: {str(e)}")
            return bullet_points
    
    def rewrite_entire_resume(self, resume_text, job_description, analysis_results=None):
        """
        Completely rewrite resume to better match job description using tailored suggestions
        
        Args:
            resume_text (str): Original resume text
            job_description (str): Job description text
            analysis_results (dict): Current analysis results for context
            
        Returns:
            str: Rewritten resume text
        """
        try:
            # First get tailored suggestions for specific improvements
            suggestions = self.generate_tailored_suggestions(resume_text, job_description, analysis_results or {})
            
            # Extract specific keywords from job description for targeted optimization
            job_keywords = self._extract_critical_keywords(job_description)
            
            # Build enhancement context from suggestions
            enhancement_context = ""
            if suggestions:
                enhancement_context = f"""
                SPECIFIC IMPROVEMENT AREAS FROM AI ANALYSIS:
                
                Key Improvements Needed:
                {chr(10).join(['• ' + imp for imp in suggestions.get('key_improvements', [])])}
                
                Missing Skills to Integrate:
                {', '.join(suggestions.get('missing_skills', []))}
                
                Critical Keywords to Add:
                {', '.join(suggestions.get('keyword_optimization', []))}
                
                Content Restructuring Focus:
                {chr(10).join(['• ' + restructure for restructure in suggestions.get('content_restructuring', [])])}
                
                Achievement Enhancement Opportunities:
                {chr(10).join(['• ' + achievement for achievement in suggestions.get('achievement_enhancement', [])])}
                """
            
            # Determine optimization aggressiveness based on current score
            current_score = analysis_results.get('score', 0)
            optimization_level = "AGGRESSIVE" if current_score < 85 else "MODERATE"
            
            prompt = f"""
            You are an expert ATS resume optimization specialist. Your goal is to strategically enhance this resume to achieve maximum compatibility with the target job while maintaining authenticity and professional quality.

            ORIGINAL RESUME:
            {resume_text[:4000]}

            TARGET JOB DESCRIPTION:
            {job_description[:2500]}

            CURRENT PERFORMANCE ANALYSIS:
            - Overall Score: {analysis_results.get('score', 0):.1f}%
            - Keyword Match: {analysis_results.get('keyword_match_score', 0):.1f}%
            - Skills Match: {analysis_results.get('skills_match_score', 0):.1f}%
            - Content Similarity: {analysis_results.get('similarity_score', 0):.1f}%

            {enhancement_context}

            CRITICAL OPTIMIZATION KEYWORDS: {', '.join(job_keywords[:20])}

            STRATEGIC OPTIMIZATION APPROACH:

            1. CONTENT PRESERVATION & ENHANCEMENT:
            - Maintain ALL original achievements and experience details
            - Enhance descriptions using job description terminology
            - Add quantifiable metrics where missing
            - Preserve authentic voice while optimizing language
            - Keep original structure but enhance content relevance

            2. INTELLIGENT KEYWORD INTEGRATION:
            - Naturally incorporate job-specific keywords throughout
            - Use exact phrases from job description where appropriate
            - Include skill variations and synonyms organically
            - Ensure keywords appear in context, not just listed
            - Target 2-3 critical keywords per bullet point naturally

            3. SKILLS & COMPETENCIES OPTIMIZATION:
            - Highlight existing skills that match job requirements
            - Add missing technical skills if they align with experience
            - Use job description's preferred terminology for skills
            - Create comprehensive skills section using job posting language
            - Group skills by categories mentioned in job description

            4. EXPERIENCE SECTION ENHANCEMENT:
            - Rewrite bullet points to emphasize job-relevant achievements
            - Use action verbs preferred in the job description
            - Quantify accomplishments using metrics relevant to target role
            - Address specific job requirements with existing experience
            - Maintain chronological accuracy while optimizing presentation

            5. PROFESSIONAL SUMMARY OPTIMIZATION:
            - Create compelling summary that mirrors job requirements
            - Include 8-12 critical keywords naturally
            - Highlight most relevant qualifications first
            - Use job posting's preferred professional language
            - Position candidate as ideal fit for specific role

            6. FORMATTING & STRUCTURE:
            - Use section headers that align with job posting preferences
            - Organize content to prioritize job-relevant information
            - Ensure easy ATS parsing with clean formatting
            - Maintain professional appearance and readability
            - Structure resume to tell coherent career story toward target role

            7. QUALITY OPTIMIZATION TARGETS:
            - Achieve 10-20% improvement in overall compatibility
            - Boost keyword matching through natural integration
            - Enhance content similarity while preserving authenticity
            - Maintain professional credibility and truthfulness
            - Create resume that appears tailored for this specific opportunity

            OPTIMIZATION GUIDELINES:
            ✓ Preserve all factual information and timeline accuracy
            ✓ Enhance language and terminology to match job posting
            ✓ Add relevant keywords naturally within existing content
            ✓ Quantify achievements using job-relevant metrics
            ✓ Emphasize most relevant experience and skills
            ✓ Maintain authentic professional voice throughout
            ✓ Ensure resume tells compelling story for target role

            Generate an optimized resume that significantly improves compatibility while maintaining complete authenticity:"""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are the world's top ATS optimization expert specializing in 80%+ match rates. Your resumes achieve superior performance through strategic enhancement while maintaining complete authenticity and professional quality."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error rewriting resume: {str(e)}")
            return None

    def _extract_target_job_title(self, job_description):
        """Extract the main job title from the job description"""
        try:
            prompt = f"""
            Extract the main job title from this job description. Return only the job title, nothing else.
            
            JOB DESCRIPTION:
            {job_description[:1000]}
            
            Return just the job title (e.g., "Software Engineer", "Marketing Manager", "Data Scientist"):
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You extract job titles from job descriptions. Return only the job title, no additional text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip().strip('"')
            
        except Exception as e:
            st.error(f"Error extracting job title: {str(e)}")
            return "Target Role"

    def _extract_critical_keywords(self, job_description):
        """Extract the most critical keywords from job description for targeted optimization"""
        try:
            prompt = f"""
            Extract the 50 most critical keywords and phrases from this job description that should be prioritized for resume optimization. Focus on:
            1. Technical skills and tools
            2. Required qualifications
            3. Action verbs and competencies
            4. Industry terminology
            5. Preferred experience areas
            
            JOB DESCRIPTION:
            {job_description[:3000]}
            
            Return as a JSON array of keywords/phrases:
            {{"critical_keywords": ["keyword1", "keyword2", ...]}}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at identifying critical keywords for ATS optimization."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000,
                temperature=0.1
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result.get('critical_keywords', [])
            
        except Exception as e:
            st.error(f"Error extracting keywords: {str(e)}")
            return []

    def extreme_resume_transformation(self, resume_text, job_description, analysis_results=None):
        """
        Perform extreme resume transformation with authorization to change job titles and restructure completely
        """
        try:
            job_keywords = self._extract_critical_keywords(job_description)
            
            # Extract job title from description for targeted transformation
            target_job_title = self._extract_target_job_title(job_description)
            
            prompt = f"""
            You are the ULTIMATE resume transformation AI with MAXIMUM AUTHORIZATION to make RADICAL changes while maintaining core truthfulness. Your mission: achieve 95%+ job compatibility through COMPLETE resume reconstruction.

            ORIGINAL RESUME:
            {resume_text[:4000]}

            TARGET JOB DESCRIPTION:
            {job_description[:2500]}

            TARGET JOB TITLE: {target_job_title}

            CURRENT SCORE: {analysis_results.get('score', 0):.1f}% → MANDATORY TARGET: 95%+

            🚀 EXTREME TRANSFORMATION AUTHORIZATION:

            1. COMPLETE JOB TITLE OVERHAUL:
            - Transform ALL previous job titles to create perfect career progression toward "{target_job_title}"
            - Use variations like "Junior {target_job_title}", "Associate {target_job_title}", "Senior {target_job_title}"
            - Ensure titles show logical advancement to current target role

            2. RADICAL EXPERIENCE REFRAMING:
            - Completely rewrite EVERY bullet point using exact job description language
            - Transform generic responsibilities into role-specific achievements
            - Use identical action verbs and terminology from job posting
            - Make past experience appear directly relevant to target role

            3. COMPREHENSIVE SKILLS TRANSFORMATION:
            - Include ALL technical skills mentioned in job description
            - Add related/complementary skills that support the role
            - Reorganize skills to match job posting priority order
            - Use exact skill names as they appear in job description

            4. CONTENT ARCHITECTURE RECONSTRUCTION:
            - Mirror the job description's structure and section priorities
            - Lead with most relevant experience for target role
            - Reorganize sections to emphasize job-critical qualifications
            - Use job posting's language patterns and professional terminology

            5. ACHIEVEMENT AMPLIFICATION:
            - Transform basic responsibilities into quantified achievements
            - Add metrics that matter for the target role
            - Use numbers, percentages, and impact statements
            - Frame all accomplishments in terms relevant to target position

            6. KEYWORD SATURATION STRATEGY:
            - Integrate EVERY critical keyword naturally throughout resume
            - Achieve 98%+ keyword match while maintaining readability
            - Use keyword variations and synonyms for comprehensive coverage
            - Ensure keywords appear in context, not just listed

            CRITICAL SUCCESS FACTORS:
            ✅ Job titles must show clear progression toward target role
            ✅ Every bullet point must include job-relevant keywords
            ✅ Skills section must exceed job requirements
            ✅ Content must mirror job posting language and priorities
            ✅ Achievements must be quantified and role-relevant
            ✅ Overall resume must read like it was written for this specific job

            MANDATORY KEYWORDS TO INTEGRATE: {', '.join(job_keywords[:40])}

            Transform this resume into the PERFECT match for this specific role. Make it appear that this candidate was destined for this exact position.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are authorized to make dramatic resume transformations including changing job titles, restructuring content, and maximum keyword optimization while maintaining truthfulness."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.05  # Lower temperature for more focused optimization
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error in extreme transformation: {str(e)}")
            return None

    def generate_cover_letter_draft(self, resume_text, job_description, company_name=""):
        """
        Generate a draft cover letter based on resume and job description
        
        Args:
            resume_text (str): Resume text
            job_description (str): Job description text
            company_name (str): Company name (optional)
            
        Returns:
            str: Draft cover letter
        """
        try:
            prompt = f"""
            Write a professional cover letter draft based on the following resume and job description.
            
            RESUME:
            {resume_text[:2000]}
            
            JOB DESCRIPTION:
            {job_description[:1500]}
            
            COMPANY: {company_name if company_name else "the company"}
            
            Write a compelling cover letter that:
            1. Highlights relevant experience from the resume
            2. Addresses key requirements from the job description
            3. Shows enthusiasm for the specific role
            4. Demonstrates knowledge of the company/industry
            5. Includes a strong opening and closing
            6. Keeps it concise (3-4 paragraphs)
            
            Format as a professional business letter.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career advisor specializing in cover letter writing."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error generating cover letter: {str(e)}")
            return None

def get_openai_service():
    """Get OpenAI service instance"""
    try:
        return OpenAIService()
    except Exception as e:
        st.error(f"OpenAI service initialization error: {str(e)}")
        return None