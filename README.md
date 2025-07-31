# Automated Parsing Pipeline - Stage 1

A Python-based parser that automatically identifies file type, extracts relevant data fields, validates schema, and stores data in SQLite database.

## Current Stage: File Detection & Database Setup

### Features Implemented:
- ✅ **Smart File Detection** - Analyzes file content patterns to identify EDI, XML, and Edifact files
- ✅ **SQLite Database** - Store parsed data with relationships
- ✅ **Error Handling** - Graceful failures
- ✅ **Logging** - Basic logging

### Project Structure:
```
parsing_pipeline/
├── src/
│   ├── detector.py      # File type detection
│   ├── database.py      # SQLite operations
│   └── __init__.py
├── sample_files/        # Test files
├── config.py           # Configuration
├── requirements.txt    # Dependencies
├── test_detection.py  # Test script
└── README.md
```

### Installation:
```bash
pip install -r requirements.txt
```

### Testing:
```bash
python test_detection.py
```

### Sample Files:
- `sample_invoice.edi` - EDI X12 invoice
- `sample_order.xml` - XML order document  
- `sample_shipment.edifact` - EDIFACT shipment

### Database Schema:
```sql
-- Files table
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'processed',
    error_message TEXT
);

-- Parsed data table
CREATE TABLE parsed_data (
    id INTEGER PRIMARY KEY,
    file_id INTEGER,
    field_name TEXT NOT NULL,
    field_value TEXT,
    segment_type TEXT,
    position INTEGER,
    confidence REAL DEFAULT 1.0,
    FOREIGN KEY (file_id) REFERENCES files (id)
);
```

### Next Stages:
- Three parsers - EDI, XML, Edifact with proper field extraction
- Validation - Basic schema checks
- CLI - Simple command interface

## Usage Example:
```python
from src.detector import FileTypeDetector
from src.database import DatabaseManager

# Detect file type
detector = FileTypeDetector()
file_type, confidence = detector.detect_file_type("sample_invoice.edi")
print(f"File type: {file_type}, Confidence: {confidence}")

# Database operations
db = DatabaseManager()
file_count = db.get_file_count()
print(f"Files in database: {file_count}")
``` 