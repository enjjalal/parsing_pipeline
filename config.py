import os
from pathlib import Path

# Database configuration
DATABASE_PATH = "parsing_pipeline.db"

# File type patterns for detection
FILE_PATTERNS = {
    "EDI": {
        "extensions": [".edi", ".x12", ".edifact"],
        "content_patterns": [
            "ISA*", "GS*", "ST*", "SE*", "GE*", "IEA*",  # X12 patterns
            "UNB*", "UNG*", "UNH*", "UNT*", "UNE*", "UNZ*"  # EDIFACT patterns
        ]
    },
    "XML": {
        "extensions": [".xml"],
        "content_patterns": ["<?xml", "<root", "<document"]
    },
    "EDIFACT": {
        "extensions": [".edi", ".edifact"],
        "content_patterns": ["UNB*", "UNG*", "UNH*", "UNT*", "UNE*", "UNZ*"]
    }
}

# Database schema
DATABASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'processed',
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS parsed_data (
    id INTEGER PRIMARY KEY,
    file_id INTEGER,
    field_name TEXT NOT NULL,
    field_value TEXT,
    segment_type TEXT,
    position INTEGER,
    confidence REAL DEFAULT 1.0,
    FOREIGN KEY (file_id) REFERENCES files (id)
);
"""

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 