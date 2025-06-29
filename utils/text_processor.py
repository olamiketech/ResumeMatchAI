import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string

# Download required NLTK data with better error handling
def download_nltk_data():
    """Download NLTK data with fallback handling"""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
        except Exception as e:
            print(f"Failed to download punkt: {e}")

    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        try:
            nltk.download('punkt_tab', quiet=True)
        except Exception as e:
            print(f"Failed to download punkt_tab: {e}")

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        try:
            nltk.download('stopwords', quiet=True)
        except Exception as e:
            print(f"Failed to download stopwords: {e}")

# Initialize NLTK data
download_nltk_data()

class TextProcessor:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        # Add common resume/job description stop words
        additional_stop_words = {
            'experience', 'work', 'years', 'year', 'job', 'position', 
            'role', 'responsibilities', 'skills', 'ability', 'strong',
            'excellent', 'good', 'knowledge', 'working', 'including'
        }
        self.stop_words.update(additional_stop_words)
    
    def clean_text(self, text):
        """
        Clean and normalize text
        
        Args:
            text (str): Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep letters, numbers, and some punctuation
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, text, min_length=2, max_length=25):
        """
        Extract meaningful keywords from text with enhanced keyword detection
        
        Args:
            text (str): Text to extract keywords from
            min_length (int): Minimum keyword length
            max_length (int): Maximum keyword length
            
        Returns:
            list: List of extracted keywords
        """
        if not text:
            return []
        
        # Clean text but preserve important technical terms
        cleaned_text = self.clean_text(text)
        
        # Tokenize
        tokens = word_tokenize(cleaned_text)
        
        # Enhanced keyword extraction
        keywords = []
        
        # Single word keywords
        for token in tokens:
            if (len(token) >= min_length and 
                len(token) <= max_length and 
                token not in self.stop_words and
                not token.isdigit() and
                token not in string.punctuation):
                keywords.append(token)
        
        # Extract multi-word phrases (bigrams and trigrams)
        words = [token for token in tokens if len(token) >= 2 and token not in string.punctuation]
        
        # Bigrams
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            if len(bigram) <= max_length and not any(word in self.stop_words for word in words[i:i+2]):
                keywords.append(bigram)
        
        # Trigrams for technical terms
        for i in range(len(words) - 2):
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            if len(trigram) <= max_length and not any(word in self.stop_words for word in words[i:i+3]):
                keywords.append(trigram)
        
        # Remove duplicates while preserving order
        unique_keywords = []
        seen = set()
        for keyword in keywords:
            if keyword.lower() not in seen:
                unique_keywords.append(keyword)
                seen.add(keyword.lower())
        
        return unique_keywords
    
    def extract_skills(self, text):
        """
        Extract technical skills and competencies from text
        
        Args:
            text (str): Text to extract skills from
            
        Returns:
            list: List of identified skills
        """
        # Common technical skills and tools
        technical_skills = {
            'python', 'java', 'javascript', 'html', 'css', 'sql', 'r', 'c++', 'c#',
            'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'jenkins',
            'tableau', 'powerbi', 'excel', 'photoshop', 'illustrator',
            'machine learning', 'data science', 'artificial intelligence',
            'project management', 'agile', 'scrum', 'devops', 'ci/cd'
        }
        
        # Soft skills
        soft_skills = {
            'leadership', 'communication', 'teamwork', 'problem solving',
            'analytical', 'creative', 'detail oriented', 'time management',
            'adaptability', 'collaboration', 'customer service', 'presentations'
        }
        
        all_skills = technical_skills.union(soft_skills)
        
        # Clean text for matching
        cleaned_text = self.clean_text(text)
        
        # Find matching skills
        found_skills = []
        for skill in all_skills:
            if skill in cleaned_text:
                found_skills.append(skill)
        
        return found_skills
    
    def preprocess_for_similarity(self, text):
        """
        Preprocess text for similarity calculation
        
        Args:
            text (str): Text to preprocess
            
        Returns:
            str: Preprocessed text
        """
        if not text or not text.strip():
            return ""
            
        # Clean text but preserve more content for similarity
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation but keep spaces
        text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
        
        # Tokenize with fallback
        try:
            tokens = word_tokenize(text)
        except Exception as e:
            print(f"NLTK tokenization failed: {e}, using simple split")
            # Fallback to simple split if nltk fails
            tokens = text.split()
        
        processed_tokens = []
        
        # Keep more words for better similarity calculation
        basic_stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        
        for token in tokens:
            # Keep meaningful tokens for similarity
            if (len(token) > 1 and 
                not token.isdigit() and
                token not in basic_stop_words):
                processed_tokens.append(token)
        
        result = ' '.join(processed_tokens)
        
        # Debug output
        print(f"Text preprocessing - Input length: {len(text)}, Output length: {len(result)}, Tokens: {len(processed_tokens)}")
        
        return result

def preprocess_text(text):
    """
    Convenience function for text preprocessing
    
    Args:
        text (str): Text to preprocess
        
    Returns:
        str: Preprocessed text
    """
    processor = TextProcessor()
    return processor.preprocess_for_similarity(text)
