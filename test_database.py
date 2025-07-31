#!/usr/bin/env python3
"""
Test script to demonstrate database functionality and relationships.
"""

import logging
from src.database import DatabaseManager
from src.detector import FileTypeDetector
from src.parser import ParserFactory

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_database_relationships():
    """Test database relationships and data storage."""
    print("=== Database Relationships Test ===")
    
    db = DatabaseManager()
    
    # Get current stats
    file_count = db.get_file_count()
    print(f"📊 Current files in database: {file_count}")
    
    # Show all files with their relationships
    files = db.get_all_files()
    print(f"\n📁 Files in database:")
    for file in files:
        print(f"  - ID: {file['id']}")
        print(f"    Filename: {file['filename']}")
        print(f"    Type: {file['file_type']}")
        print(f"    Size: {file['file_size']} bytes")
        print(f"    Status: {file['status']}")
        print(f"    Processed: {file['processed_at']}")
        
        # Get related parsed data
        parsed_data = db.get_parsed_data_by_file_id(file['id'])
        print(f"    📋 Parsed fields: {len(parsed_data)}")
        
        # Show some key fields
        key_fields = [f for f in parsed_data if any(keyword in f['field_name'].lower() 
                   for keyword in ['date', 'id', 'number', 'amount', 'price', 'name'])]
        
        if key_fields:
            print(f"    🔑 Key fields:")
            for field in key_fields[:3]:
                print(f"      - {field['field_name']}: {field['field_value']}")
        
        print()

def test_data_export():
    """Test data export functionality."""
    print("=== Data Export Test ===")
    
    db = DatabaseManager()
    files = db.get_all_files()
    
    if files:
        file_id = files[0]['id']
        print(f"📤 Exporting data for file ID: {file_id}")
        
        # Export as JSON structure
        exported_data = db.export_data_to_json(file_id)
        
        if exported_data:
            file_info = exported_data['file_info']
            parsed_data = exported_data['parsed_data']
            
            print(f"✅ Export successful:")
            print(f"   File: {file_info['filename']}")
            print(f"   Type: {file_info['file_type']}")
            print(f"   Fields: {len(parsed_data)}")
            
            # Show sample exported data
            print(f"   📋 Sample exported fields:")
            for field in parsed_data[:5]:
                print(f"      - {field['field_name']}: {field['field_value']}")
        else:
            print("❌ Export failed")
    else:
        print("❌ No files to export")

def test_database_operations():
    """Test all database operations."""
    print("=== Database Operations Test ===")
    
    db = DatabaseManager()
    
    # Test file insertion
    print("📝 Testing file insertion...")
    test_file_info = {
        "filename": "test_file.edi",
        "file_type": "EDI",
        "file_size": 1024,
        "status": "processed"
    }
    
    try:
        file_id = db.insert_file_record(test_file_info)
        print(f"✅ File inserted with ID: {file_id}")
        
        # Test parsed data insertion
        print("📝 Testing parsed data insertion...")
        test_parsed_data = [
            {
                "field_name": "test_field_1",
                "field_value": "test_value_1",
                "segment_type": "TEST",
                "position": 1,
                "confidence": 0.9
            },
            {
                "field_name": "test_field_2", 
                "field_value": "test_value_2",
                "segment_type": "TEST",
                "position": 2,
                "confidence": 0.9
            }
        ]
        
        db.insert_parsed_data(file_id, test_parsed_data)
        print(f"✅ Parsed data inserted: {len(test_parsed_data)} fields")
        
        # Test retrieval
        print("📖 Testing data retrieval...")
        retrieved_data = db.get_parsed_data_by_file_id(file_id)
        print(f"✅ Retrieved {len(retrieved_data)} fields")
        
        # Test status update
        print("📝 Testing status update...")
        db.update_file_status(file_id, "completed", "Test completed successfully")
        print("✅ Status updated")
        
        # Verify relationships
        file_info = db.get_file_by_id(file_id)
        if file_info:
            print(f"✅ File relationship verified: {file_info['filename']}")
        
    except Exception as e:
        print(f"❌ Database operation failed: {e}")

def main():
    """Run all database tests."""
    print("Database Functionality Test")
    print("=" * 40)
    
    test_database_relationships()
    test_data_export()
    test_database_operations()
    
    print("=" * 40)
    print("✅ Database functionality complete!")

if __name__ == "__main__":
    main() 