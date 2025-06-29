import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .text_processor import TextProcessor
import re

class ResumeAnalyzer:
    def __init__(self):
        self.text_processor = TextProcessor()
        # Simplified TF-IDF vectorizer for better reliability
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.9,
            sublinear_tf=True
        )

    def analyze_resume(self, resume_text, job_description):
        """
        Analyze resume against job description with improved accuracy

        Args:
            resume_text (str): Resume text
            job_description (str): Job description text

        Returns:
            dict: Analysis results including score and suggestions
        """
        # Preprocess texts
        resume_processed = self.text_processor.preprocess_for_similarity(resume_text)
        job_processed = self.text_processor.preprocess_for_similarity(job_description)

        # Calculate similarity score with error handling
        similarity_score = self._calculate_similarity(resume_processed, job_processed)

        # Extract keywords with improved matching
        resume_keywords = set([kw.lower().strip() for kw in self.text_processor.extract_keywords(resume_text) if len(kw.strip()) > 2])
        job_keywords = set([kw.lower().strip() for kw in self.text_processor.extract_keywords(job_description) if len(kw.strip()) > 2])

        # Improved keyword matching
        matching_keywords = self._find_matching_keywords(resume_keywords, job_keywords)

        # Calculate keyword match score
        if job_keywords:
            keyword_match_score = min(100, (len(matching_keywords) / len(job_keywords)) * 100)
        else:
            keyword_match_score = 0

        missing_keywords = job_keywords - matching_keywords

        # Extract and match skills with enhanced detection
        resume_skills = set([skill.lower().strip() for skill in self.text_processor.extract_skills(resume_text)])
        job_skills = set([skill.lower().strip() for skill in self.text_processor.extract_skills(job_description)])
        
        # Enhanced skills matching with partial matching
        matching_skills = self._find_matching_skills(resume_skills, job_skills)

        # Calculate skills match score with bonus for comprehensive skill coverage
        if job_skills:
            base_skills_score = (len(matching_skills) / len(job_skills)) * 100
            
            # Bonus for having more skills than required
            if len(resume_skills) > len(job_skills):
                skill_abundance_bonus = min(10, (len(resume_skills) - len(job_skills)) * 2)
                base_skills_score += skill_abundance_bonus
            
            skills_match_score = min(100, base_skills_score)
        else:
            skills_match_score = 0

        # Calculate final score with balanced weighting
        final_score = self._calculate_final_score(
            similarity_score, 
            keyword_match_score, 
            skills_match_score,
            len(matching_keywords),
            len(job_keywords)
        )

        # Generate suggestions
        suggestions = self._generate_suggestions(
            resume_text, job_description, missing_keywords, 
            job_skills - resume_skills, final_score
        )

        return {
            'score': round(final_score, 1),
            'similarity_score': round(similarity_score, 1),
            'keyword_match_score': round(keyword_match_score, 1),
            'skills_match_score': round(skills_match_score, 1),
            'matching_keywords': list(matching_keywords),
            'missing_keywords': list(missing_keywords)[:15],
            'suggestions': suggestions
        }

    def _find_matching_skills(self, resume_skills, job_skills):
        """Enhanced skills matching with partial matching and synonyms"""
        matching = set()
        
        # Skill synonyms and variations
        skill_synonyms = {
            'javascript': ['js', 'node.js', 'nodejs', 'react', 'vue', 'angular'],
            'python': ['django', 'flask', 'pandas', 'numpy', 'pytorch'],
            'java': ['spring', 'hibernate', 'maven', 'gradle'],
            'sql': ['mysql', 'postgresql', 'sqlite', 'oracle', 'mongodb'],
            'aws': ['amazon web services', 'ec2', 's3', 'lambda', 'cloudformation'],
            'machine learning': ['ml', 'ai', 'deep learning', 'neural networks'],
            'data analysis': ['analytics', 'data science', 'statistics', 'visualization'],
        }
        
        # Direct matching
        for job_skill in job_skills:
            for resume_skill in resume_skills:
                # Exact match
                if job_skill == resume_skill:
                    matching.add(job_skill)
                    continue
                
                # Substring matching
                if job_skill in resume_skill or resume_skill in job_skill:
                    matching.add(job_skill)
                    continue
                
                # Synonym matching
                for base_skill, synonyms in skill_synonyms.items():
                    if (job_skill == base_skill and resume_skill in synonyms) or \
                       (resume_skill == base_skill and job_skill in synonyms) or \
                       (job_skill in synonyms and resume_skill in synonyms):
                        matching.add(job_skill)
                        continue
        
        return matching
    
    def _find_matching_keywords(self, resume_keywords, job_keywords):
        """Find matching keywords with enhanced detection logic"""
        matching = set()

        # Convert to lowercase for comparison
        resume_lower = {kw.lower() for kw in resume_keywords}
        job_lower = {kw.lower() for kw in job_keywords}

        # Exact matches (case insensitive)
        for job_kw in job_keywords:
            if job_kw.lower() in resume_lower:
                matching.add(job_kw.lower())

        # Enhanced partial matching
        for job_kw in job_keywords:
            job_kw_lower = job_kw.lower()
            
            for resume_kw in resume_keywords:
                resume_kw_lower = resume_kw.lower()
                
                # Skip very short keywords for partial matching
                if len(job_kw_lower) < 3 or len(resume_kw_lower) < 3:
                    continue
                
                # Substring matching for technical terms
                if job_kw_lower in resume_kw_lower or resume_kw_lower in job_kw_lower:
                    matching.add(job_kw_lower)
                    continue
                
                # Word-level matching for multi-word terms
                job_words = set(job_kw_lower.split())
                resume_words = set(resume_kw_lower.split())
                
                if len(job_words) > 1 and len(resume_words) > 1:
                    overlap = len(job_words.intersection(resume_words))
                    # Lower threshold for better matching
                    if overlap >= len(job_words) * 0.7:
                        matching.add(job_kw_lower)
                        continue
                
                # Fuzzy matching for similar terms (e.g., "analyze" vs "analysis")
                if len(job_kw_lower) >= 5 and len(resume_kw_lower) >= 5:
                    # Check if words share significant character overlap
                    shorter = min(job_kw_lower, resume_kw_lower, key=len)
                    longer = max(job_kw_lower, resume_kw_lower, key=len)
                    
                    # Calculate character overlap ratio
                    common_chars = sum(1 for char in shorter if char in longer)
                    overlap_ratio = common_chars / len(shorter)
                    
                    if overlap_ratio >= 0.8:  # 80% character overlap
                        matching.add(job_kw_lower)

        return matching

    def _calculate_similarity(self, text1, text2):
        """Calculate cosine similarity with improved error handling"""
        try:
            if not text1 or not text2 or not text1.strip() or not text2.strip():
                return 0.0

            # Clean and prepare texts
            words1 = text1.split()
            words2 = text2.split()
            
            # If texts are too short, use simple word overlap
            if len(words1) < 10 or len(words2) < 10:
                return self._calculate_word_overlap(text1, text2)

            # Use optimized vectorizer for better similarity detection
            vectorizer = TfidfVectorizer(
                max_features=3000,
                stop_words='english',  # Remove stop words for better content analysis
                ngram_range=(1, 2),    # Reduced to 1-2 grams for better performance
                min_df=1,
                max_df=0.8,
                lowercase=True,
                token_pattern=r'\b[a-zA-Z]{3,}\b',  # Only words with 3+ characters
                sublinear_tf=True,
                use_idf=True
            )

            # Create TF-IDF vectors
            try:
                documents = [text1, text2]
                tfidf_matrix = vectorizer.fit_transform(documents)
                
                # Calculate cosine similarity
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                
                # Boost similarity if very low due to different document lengths
                if similarity < 0.1:
                    # Try with different parameters for short documents
                    alt_vectorizer = TfidfVectorizer(
                        max_features=1000,
                        stop_words=None,
                        ngram_range=(1, 1),
                        min_df=1,
                        lowercase=True
                    )
                    alt_matrix = alt_vectorizer.fit_transform(documents)
                    alt_similarity = cosine_similarity(alt_matrix[0:1], alt_matrix[1:2])[0][0]
                    similarity = max(similarity, alt_similarity)
                
            except (ValueError, IndexError) as e:
                print(f"TF-IDF failed: {e}, using word overlap fallback")
                similarity = self._calculate_word_overlap(text1, text2) / 100

            # Convert to percentage and ensure realistic range (30-90% typical)
            similarity_percentage = max(5, min(90, similarity * 100))
            
            # Apply realistic scaling - improved algorithm for better content similarity
            if similarity_percentage > 80:
                # Cap very high similarities but allow for well-optimized resumes
                similarity_percentage = 65 + (similarity_percentage - 80) * 0.5
            elif similarity_percentage > 60:
                # Moderate scaling for good similarities
                similarity_percentage = 45 + (similarity_percentage - 60) * 1.0
            elif similarity_percentage < 15:
                # Boost very low similarities to realistic minimum
                similarity_percentage = 15 + similarity_percentage * 0.8
            
            print(f"Content similarity - Text1: {len(words1)} words, Text2: {len(words2)} words, Similarity: {similarity_percentage:.1f}%")
            
            return similarity_percentage
        except Exception as e:
            print(f"Similarity calculation error: {e}")
            return self._calculate_word_overlap(text1, text2)

    def _calculate_word_overlap(self, text1, text2):
        """Calculate word overlap as fallback similarity measure"""
        try:
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            # Jaccard similarity
            overlap = (len(intersection) / len(union)) * 100 if union else 0
            
            print(f"Word overlap fallback - Intersection: {len(intersection)}, Union: {len(union)}, Overlap: {overlap:.2f}%")
            
            return min(overlap, 100)
        except Exception as e:
            print(f"Word overlap calculation error: {e}")
            return 0.0

    def _calculate_final_score(self, similarity_score, keyword_score, skills_score, matching_count, total_keywords):
        """Calculate final score with balanced and realistic weighting"""

        # Ensure all scores are valid numbers
        similarity_score = max(0, similarity_score) if similarity_score is not None else 0
        keyword_score = max(0, keyword_score) if keyword_score is not None else 0
        skills_score = max(0, skills_score) if skills_score is not None else 0

        # Improved scoring weights for better optimization rewards
        base_score = (
            similarity_score * 0.35 +   # Content similarity importance
            keyword_score * 0.45 +      # Higher weight for keyword optimization
            skills_score * 0.20         # Skills contribution
        )

        # Enhanced keyword bonuses for optimization rewards
        if total_keywords > 0 and matching_count > 0:
            keyword_ratio = matching_count / total_keywords
            
            # Progressive reward system for keyword optimization
            if keyword_ratio >= 0.98:   # 98%+ keywords matched - exceptional
                base_score *= 1.20      # 20% bonus for outstanding optimization
            elif keyword_ratio >= 0.95:  # 95%+ keywords matched
                base_score *= 1.15      # 15% bonus for excellent optimization
            elif keyword_ratio >= 0.90:  # 90%+ keywords matched
                base_score *= 1.10      # 10% bonus for strong optimization
            elif keyword_ratio >= 0.85:  # 85%+ keywords matched
                base_score *= 1.05      # 5% bonus for good optimization

        # Improved similarity reward system
        if similarity_score >= 65:
            base_score *= 1.12          # 12% bonus for high content similarity
        elif similarity_score >= 55:
            base_score *= 1.08          # 8% bonus for good content similarity
        elif similarity_score >= 45:
            base_score *= 1.03          # 3% bonus for moderate content similarity
        elif similarity_score < 25:
            base_score *= 0.85          # 15% penalty for low content similarity
        elif similarity_score < 15:
            base_score *= 0.75          # 25% penalty for very low content similarity

        # Skills gap penalty for realistic assessment
        if skills_score < 50:
            base_score *= 0.9           # 10% penalty for significant skills gap

        # Allow higher scores for excellent optimization
        if base_score > 95:
            # Cap extremely high scores but allow for outstanding performance
            base_score = 90 + (base_score - 95) * 0.3
        elif base_score > 90:
            # Moderate scaling for very high scores
            base_score = 85 + (base_score - 90) * 0.6
        elif base_score > 85:
            # Gentle scaling for high scores
            base_score = 80 + (base_score - 85) * 0.8

        # Ensure score is within realistic range (typically 20-95% for optimized resumes)
        final_score = max(15, min(95, base_score))
        
        # Debug output
        keyword_ratio = matching_count / total_keywords if total_keywords > 0 else 0
        print(f"Balanced Score Calculation:")
        print(f"  Component scores - Content: {similarity_score:.1f}%, Keywords: {keyword_score:.1f}%, Skills: {skills_score:.1f}%")
        print(f"  Keyword metrics - Matched: {matching_count}/{total_keywords} ({keyword_ratio:.1%})")
        print(f"  Realistic final score: {final_score:.1f}%")
        
        return final_score

    def _generate_suggestions(self, resume_text, job_description, missing_keywords, missing_skills, score):
        """Generate improvement suggestions"""
        suggestions = []

        # Score-based suggestions
        if score < 40:
            suggestions.append(
                "Your resume has a low compatibility score. Consider restructuring to better match the job requirements."
            )
        elif score < 65:
            suggestions.append(
                "Your resume shows moderate compatibility. Focus on incorporating more relevant keywords and skills."
            )
        elif score < 80:
            suggestions.append(
                "Good compatibility! Fine-tune by adding missing keywords and emphasizing relevant experience."
            )
        else:
            suggestions.append(
                "Excellent compatibility! Your resume aligns well with the job requirements."
            )

        # Keyword suggestions
        if missing_keywords:
            top_missing = list(missing_keywords)[:5]
            suggestions.append(
                f"Consider adding these important keywords: {', '.join(top_missing)}"
            )

        # Skills suggestions
        if missing_skills:
            top_missing_skills = list(missing_skills)[:3]
            suggestions.append(
                f"Highlight these skills if you have them: {', '.join(top_missing_skills)}"
            )

        # Structure suggestions
        if not self._has_quantified_achievements(resume_text):
            suggestions.append(
                "Add quantifiable achievements with numbers and percentages to make your impact more concrete."
            )

        if not self._has_strong_action_verbs(resume_text):
            suggestions.append(
                "Use stronger action verbs like 'implemented', 'optimized', 'achieved', or 'led' to describe your experience."
            )

        return suggestions[:5]  # Limit to 5 suggestions

    def _has_quantified_achievements(self, text):
        """Check if text contains quantified achievements"""
        patterns = [
            r'\d+%',  # percentages
            r'\$\d+',  # dollar amounts
            r'\d+\+',  # numbers with plus
            r'\d+\s*(years?|months?)',  # time periods
            r'\d+\s*(people|employees|team|staff)',  # team sizes
        ]

        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _has_strong_action_verbs(self, text):
        """Check if text uses strong action verbs"""
        strong_verbs = {
            'achieved', 'implemented', 'developed', 'created', 'designed',
            'optimized', 'improved', 'increased', 'reduced', 'managed',
            'led', 'directed', 'coordinated', 'executed', 'delivered',
            'established', 'initiated', 'streamlined', 'enhanced'
        }

        text_lower = text.lower()
        found_verbs = sum(1 for verb in strong_verbs if verb in text_lower)

        return found_verbs >= 2