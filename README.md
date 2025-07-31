# Automated Parsing Pipeline - Stage 4 Complete

A Python-based parser that automatically identifies file type, extracts relevant data fields, validates schema, and stores data in SQLite database.

## Current Stage: Validation with Basic Schema Checks

### Features Implemented:
- ✅ **Smart File Detection** - Analyzes file content patterns to identify EDI, XML, and Edifact files
- ✅ **Three Parsers** - EDI, XML, Edifact with proper field extraction
- ✅ **SQLite Database** - Store parsed data with relationships
- ✅ **Validation** - Basic schema checks
- ✅ **Error Handling** - Graceful failures
- ✅ **Logging** - Basic logging

### Project Structure:
```
parsing_pipeline/
├── src/
│   ├── detector.py      # File type detection
│   ├── parser.py        # Three parsers (EDI, XML, Edifact)
│   ├── validator.py     # Validation system
│   ├── database.py      # SQLite operations
│   └── __init__.py
├── sample_files/        # Test files
├── config.py           # Configuration
├── requirements.txt    # Dependencies
├── test_detection.py  # Stage 1 test
├── test_parsers.py    # Stage 2 test
├── test_database.py   # Stage 3 test
├── test_validation.py # Stage 4 test
└── README.md
```

### Installation:
```bash
pip install -r requirements.txt
```

### Testing:
```bash
# Test Stage 1 (File Detection)
python test_detection.py

# Test Stage 2 (Parsers)
python test_parsers.py

# Test Stage 3 (Database)
python test_database.py

# Test Stage 4 (Validation)
python test_validation.py
```

### Sample Files:
- `sample_invoice.edi` - EDI X12 invoice
- `sample_order.xml` - XML order document  
- `sample_shipment.edifact` - EDIFACT shipment

### Validation System:

#### **EDI Validator:**
- **Schema Validation**: Required segments (ISA, GS, ST, SE, GE, IEA)
- **Pattern Validation**: Segment format patterns
- **Data Validation**: Date formats, numeric fields
- **Required Fields**: Sender ID, receiver ID, dates

#### **XML Validator:**
- **Schema Validation**: Well-formed XML structure
- **Element Validation**: Required business elements
- **Data Type Validation**: String, integer, decimal, date
- **Structure Validation**: Root element, child elements

#### **Edifact Validator:**
- **Schema Validation**: Required segments (UNB, UNG, UNH, UNT, UNE, UNZ)
- **Pattern Validation**: Segment format patterns
- **Data Validation**: Date/time formats, numeric fields
- **Required Fields**: Syntax identifier, sender/receiver IDs

### Validation Results:
- **EDI**: Schema validation with segment requirements
- **XML**: ✅ Valid structure and data types
- **Edifact**: Schema validation with warnings for data formats

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

### Test Results:
- **EDI Parser**: ✅ 61 fields extracted from invoice
- **XML Parser**: ✅ 22 fields extracted from order
- **Edifact Parser**: ✅ 43 fields extracted from shipment
- **Database Integration**: ✅ Full CRUD operations working
- **Validation**: ✅ Schema and data validation working

### Next Stages:
- CLI - Simple command interface

## Usage Example:
```python
from src.detector import FileTypeDetector
from src.parser import ParserFactory
from src.validator import ValidatorFactory
from src.database import DatabaseManager

# Detect, parse, and validate file
detector = FileTypeDetector()
file_type, confidence = detector.detect_file_type("invoice.edi")

# Create parser and validator
parser = ParserFactory.create_parser(file_type)
validator = ValidatorFactory.create_validator(file_type)

# Parse and validate
parsed_data = parser.parse("invoice.edi")
validation_result = validator.validate("invoice.edi", parsed_data)

print(f"Valid: {validation_result.is_valid}")
print(f"Errors: {len(validation_result.errors)}")
print(f"Warnings: {len(validation_result.warnings)}")

# Store in database if valid
if validation_result.is_valid:
    db = DatabaseManager()
    file_id = db.insert_file_record(file_info)
    db.insert_parsed_data(file_id, parsed_data)
``` 