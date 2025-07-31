import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from config import DATABASE_PATH, DATABASE_SCHEMA

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for the parsing pipeline."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database and create tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(DATABASE_SCHEMA)
                logger.info(f"Database initialized: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def insert_file_record(self, file_info: Dict[str, Any]) -> int:
        """
        Insert a file record and return the file ID.
        
        Args:
            file_info: Dictionary containing file information
            
        Returns:
            File ID (integer)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO files (filename, file_type, file_size, status)
                    VALUES (?, ?, ?, ?)
                """, (
                    file_info["filename"],
                    file_info["file_type"],
                    file_info["file_size"],
                    "processed"
                ))
                file_id = cursor.lastrowid
                conn.commit()
                logger.info(f"File record inserted with ID: {file_id}")
                return file_id
        except sqlite3.Error as e:
            logger.error(f"Failed to insert file record: {e}")
            raise
    
    def insert_parsed_data(self, file_id: int, parsed_data: List[Dict[str, Any]]):
        """
        Insert parsed data for a file.
        
        Args:
            file_id: ID of the file record
            parsed_data: List of dictionaries containing parsed field data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for data in parsed_data:
                    cursor.execute("""
                        INSERT INTO parsed_data 
                        (file_id, field_name, field_value, segment_type, position, confidence)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        file_id,
                        data.get("field_name", ""),
                        data.get("field_value", ""),
                        data.get("segment_type", ""),
                        data.get("position", 0),
                        data.get("confidence", 1.0)
                    ))
                
                conn.commit()
                logger.info(f"Inserted {len(parsed_data)} parsed data records for file {file_id}")
        except sqlite3.Error as e:
            logger.error(f"Failed to insert parsed data: {e}")
            raise
    
    def update_file_status(self, file_id: int, status: str, error_message: str = None):
        """Update file processing status."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE files 
                    SET status = ?, error_message = ?
                    WHERE id = ?
                """, (status, error_message, file_id))
                conn.commit()
                logger.info(f"Updated file {file_id} status to: {status}")
        except sqlite3.Error as e:
            logger.error(f"Failed to update file status: {e}")
            raise
    
    def get_file_by_id(self, file_id: int) -> Optional[Dict[str, Any]]:
        """Get file information by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, filename, file_type, file_size, processed_at, status, error_message
                    FROM files WHERE id = ?
                """, (file_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "filename": row[1],
                        "file_type": row[2],
                        "file_size": row[3],
                        "processed_at": row[4],
                        "status": row[5],
                        "error_message": row[6]
                    }
                return None
        except sqlite3.Error as e:
            logger.error(f"Failed to get file by ID: {e}")
            raise
    
    def get_parsed_data_by_file_id(self, file_id: int) -> List[Dict[str, Any]]:
        """Get all parsed data for a specific file."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT field_name, field_value, segment_type, position, confidence
                    FROM parsed_data 
                    WHERE file_id = ?
                    ORDER BY position, field_name
                """, (file_id,))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "field_name": row[0],
                        "field_value": row[1],
                        "segment_type": row[2],
                        "position": row[3],
                        "confidence": row[4]
                    })
                
                return results
        except sqlite3.Error as e:
            logger.error(f"Failed to get parsed data: {e}")
            raise
    
    def get_all_files(self) -> List[Dict[str, Any]]:
        """Get all processed files."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, filename, file_type, file_size, processed_at, status
                    FROM files 
                    ORDER BY processed_at DESC
                """)
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "id": row[0],
                        "filename": row[1],
                        "file_type": row[2],
                        "file_size": row[3],
                        "processed_at": row[4],
                        "status": row[5]
                    })
                
                return results
        except sqlite3.Error as e:
            logger.error(f"Failed to get all files: {e}")
            raise
    
    def get_file_count(self) -> int:
        """Get total number of processed files."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM files")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Failed to get file count: {e}")
            raise
    
    def export_data_to_json(self, file_id: int) -> Dict[str, Any]:
        """Export file and parsed data as JSON structure."""
        file_info = self.get_file_by_id(file_id)
        if not file_info:
            return {}
        
        parsed_data = self.get_parsed_data_by_file_id(file_id)
        
        return {
            "file_info": file_info,
            "parsed_data": parsed_data
        } 