import os
import re
from typing import Tuple, Dict, Any
import logging
from config import FILE_PATTERNS

logger = logging.getLogger(__name__)

class FileTypeDetector:
    """Detects file type based on extension and content patterns."""
    
    def __init__(self):
        self.patterns = FILE_PATTERNS
    
    def detect_file_type(self, file_path: str) -> Tuple[str, float]:
        """
        Detect file type and return type with confidence score.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Tuple of (file_type, confidence_score)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file extension
        _, ext = os.path.splitext(file_path.lower())
        
        # Read first few lines for content analysis
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2048)  # Read first 2KB
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                content = f.read(2048)
        
        # Analyze content patterns
        content_score = self._analyze_content_patterns(content)
        extension_score = self._analyze_extension(ext)
        
        # Combine scores and determine file type
        file_type, confidence = self._combine_scores(content_score, extension_score)
        
        logger.info(f"Detected file type: {file_type} with confidence: {confidence:.2f}")
        return file_type, confidence
    
    def _analyze_content_patterns(self, content: str) -> Dict[str, float]:
        """Analyze content patterns for each file type."""
        scores = {}
        
        for file_type, patterns in self.patterns.items():
            score = 0.0
            total_patterns = len(patterns["content_patterns"])
            
            for pattern in patterns["content_patterns"]:
                if pattern in content:
                    score += 1.0
            
            # Normalize score
            if total_patterns > 0:
                scores[file_type] = score / total_patterns
            else:
                scores[file_type] = 0.0
        
        return scores
    
    def _analyze_extension(self, extension: str) -> Dict[str, float]:
        """Analyze file extension for each file type."""
        scores = {}
        
        for file_type, patterns in self.patterns.items():
            if extension in patterns["extensions"]:
                scores[file_type] = 1.0
            else:
                scores[file_type] = 0.0
        
        return scores
    
    def _combine_scores(self, content_scores: Dict[str, float], 
                       extension_scores: Dict[str, float]) -> Tuple[str, float]:
        """Combine content and extension scores to determine file type."""
        combined_scores = {}
        
        for file_type in self.patterns.keys():
            content_score = content_scores.get(file_type, 0.0)
            extension_score = extension_scores.get(file_type, 0.0)
            
            # Weight content analysis more heavily than extension
            combined_score = (content_score * 0.7) + (extension_score * 0.3)
            combined_scores[file_type] = combined_score
        
        # Find the file type with highest score
        if combined_scores:
            best_type = max(combined_scores, key=combined_scores.get)
            confidence = combined_scores[best_type]
            
            # If confidence is too low, default to unknown
            if confidence < 0.3:
                return "UNKNOWN", confidence
            
            return best_type, confidence
        
        return "UNKNOWN", 0.0
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive file information."""
        file_type, confidence = self.detect_file_type(file_path)
        
        return {
            "file_path": file_path,
            "file_type": file_type,
            "confidence": confidence,
            "file_size": os.path.getsize(file_path),
            "filename": os.path.basename(file_path)
        } 