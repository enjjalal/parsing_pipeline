#!/usr/bin/env python3
"""
Test script for the first stage of the parsing pipeline.
Tests file detection and database operations.
"""

import sys
import os
import logging
from src.detector import FileTypeDetector
from src.database import DatabaseManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_file_detection():
    """Test file type detection with sample files."""
    print("=== Testing File Detection ===")
    
    detector = FileTypeDetector()
    sample_files = [
        "sample_files/sample_invoice.edi",
        "sample_files/sample_order.xml", 
        "sample_files/sample_shipment.edifact"
    ]
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            try:
                file_type, confidence = detector.detect_file_type(file_path)
                file_info = detector.get_file_info(file_path)
                
                print(f"\nFile: {file_path}")
                print(f"  Detected Type: {file_type}")
                print(f"  Confidence: {confidence:.2f}")
                print(f"  File Size: {file_info['file_size']} bytes")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        else:
            print(f"File not found: {file_path}")

def test_database_operations():
    """Test database operations."""
    print("\n=== Testing Database Operations ===")
    
    try:
        db = DatabaseManager()
        
        # Test file count
        count = db.get_file_count()
        print(f"Current file count: {count}")
        
        # Test getting all files
        files = db.get_all_files()
        print(f"Files in database: {len(files)}")
        
        print("Database operations successful!")
        
    except Exception as e:
        print(f"Database test failed: {e}")

def main():
    """Run all tests."""
    print("Parsing Pipeline - Stage 1 Test")
    print("=" * 40)
    
    test_file_detection()
    test_database_operations()
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 