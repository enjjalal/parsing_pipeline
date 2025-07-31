#!/usr/bin/env python3
"""
Test script for Stage 2: Three parsers with proper field extraction.
Tests EDI, XML, and Edifact parsers.
"""

import sys
import os
import logging
from src.detector import FileTypeDetector
from src.parser import ParserFactory
from src.database import DatabaseManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_parsers():
    """Test all three parsers with sample files."""
    print("=== Testing Parsers ===")
    
    detector = FileTypeDetector()
    sample_files = [
        "sample_files/sample_invoice.edi",
        "sample_files/sample_order.xml", 
        "sample_files/sample_shipment.edifact"
    ]
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            try:
                # Detect file type
                file_type, confidence = detector.detect_file_type(file_path)
                print(f"\n📁 File: {file_path}")
                print(f"   Detected Type: {file_type}")
                print(f"   Confidence: {confidence:.2f}")
                
                # Create appropriate parser
                parser = ParserFactory.create_parser(file_type)
                
                # Parse file
                parsed_data = parser.parse(file_path)
                
                print(f"   ✅ Parsed successfully")
                print(f"   📊 Extracted {len(parsed_data)} fields")
                
                # Show some key fields
                key_fields = []
                for item in parsed_data:
                    field_name = item['field_name']
                    if any(keyword in field_name.lower() for keyword in ['date', 'id', 'number', 'amount', 'price', 'quantity', 'name']):
                        key_fields.append(item)
                
                print(f"   🔑 Key fields found: {len(key_fields)}")
                for field in key_fields[:5]:  # Show first 5 key fields
                    print(f"      - {field['field_name']}: {field['field_value']}")
                
                if len(key_fields) > 5:
                    print(f"      ... and {len(key_fields) - 5} more fields")
                
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
        else:
            print(f"❌ File not found: {file_path}")

def test_database_integration():
    """Test parser integration with database."""
    print("\n=== Testing Database Integration ===")
    
    try:
        db = DatabaseManager()
        
        # Test with EDI file
        file_path = "sample_files/sample_invoice.edi"
        if os.path.exists(file_path):
            # Get file info
            detector = FileTypeDetector()
            file_info = detector.get_file_info(file_path)
            
            # Insert file record
            file_id = db.insert_file_record(file_info)
            print(f"✅ File record inserted with ID: {file_id}")
            
            # Parse and insert data
            parser = ParserFactory.create_parser(file_info['file_type'])
            parsed_data = parser.parse(file_path)
            
            # Insert parsed data
            db.insert_parsed_data(file_id, parsed_data)
            print(f"✅ Inserted {len(parsed_data)} parsed fields")
            
            # Retrieve and display data
            retrieved_data = db.get_parsed_data_by_file_id(file_id)
            print(f"✅ Retrieved {len(retrieved_data)} fields from database")
            
            # Show some retrieved fields
            print("📋 Sample retrieved fields:")
            for field in retrieved_data[:3]:
                print(f"   - {field['field_name']}: {field['field_value']}")
            
        else:
            print("❌ Sample file not found for database test")
            
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")

def test_parser_validation():
    """Test parser validation."""
    print("\n=== Testing Parser Validation ===")
    
    sample_files = [
        "sample_files/sample_invoice.edi",
        "sample_files/sample_order.xml", 
        "sample_files/sample_shipment.edifact"
    ]
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            try:
                detector = FileTypeDetector()
                file_type, _ = detector.detect_file_type(file_path)
                parser = ParserFactory.create_parser(file_type)
                
                # Parse file
                parsed_data = parser.parse(file_path)
                
                # Validate parsed data
                is_valid = parser.validate(parsed_data)
                
                print(f"📁 {file_path}")
                print(f"   Type: {file_type}")
                print(f"   Valid: {'✅ Yes' if is_valid else '❌ No'}")
                print(f"   Fields: {len(parsed_data)}")
                
            except Exception as e:
                print(f"❌ Validation failed for {file_path}: {e}")

def main():
    """Run all parser tests."""
    print("Parsing Pipeline - Stage 2 Test")
    print("=" * 50)
    
    test_parsers()
    test_database_integration()
    test_parser_validation()
    
    print("\n" + "=" * 50)
    print("✅ Stage 2 Testing Complete!")

if __name__ == "__main__":
    main() 