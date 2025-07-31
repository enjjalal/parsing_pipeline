#!/usr/bin/env python3
"""
Test script for Stage 4: Validation with basic schema checks.
Tests validation for EDI, XML, and Edifact files.
"""

import sys
import os
import logging
from src.detector import FileTypeDetector
from src.parser import ParserFactory
from src.validator import ValidatorFactory

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_validation():
    """Test validation for all file types."""
    print("=== Validation System Test ===")
    
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
                print(f"   Type: {file_type}")
                print(f"   Confidence: {confidence:.2f}")
                
                # Create parser and validator
                parser = ParserFactory.create_parser(file_type)
                validator = ValidatorFactory.create_validator(file_type)
                
                # Parse file
                parsed_data = parser.parse(file_path)
                print(f"   📊 Parsed fields: {len(parsed_data)}")
                
                # Validate file and data
                validation_result = validator.validate(file_path, parsed_data)
                
                print(f"   🔍 Validation: {'✅ Valid' if validation_result.is_valid else '❌ Invalid'}")
                
                if validation_result.errors:
                    print(f"   ❌ Errors ({len(validation_result.errors)}):")
                    for error in validation_result.errors[:3]:  # Show first 3 errors
                        print(f"      - {error}")
                
                if validation_result.warnings:
                    print(f"   ⚠️  Warnings ({len(validation_result.warnings)}):")
                    for warning in validation_result.warnings[:3]:  # Show first 3 warnings
                        print(f"      - {warning}")
                
                # Show detailed validation result
                print(f"\n   📋 Detailed Validation:")
                print(str(validation_result))
                
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
        else:
            print(f"❌ File not found: {file_path}")

def test_schema_validation():
    """Test schema validation specifically."""
    print("\n=== Schema Validation Test ===")
    
    detector = FileTypeDetector()
    sample_files = [
        "sample_files/sample_invoice.edi",
        "sample_files/sample_order.xml", 
        "sample_files/sample_shipment.edifact"
    ]
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            try:
                file_type, _ = detector.detect_file_type(file_path)
                validator = ValidatorFactory.create_validator(file_type)
                
                # Test schema validation only
                schema_result = validator.validate_schema(file_path)
                
                print(f"\n📁 {file_path}")
                print(f"   Type: {file_type}")
                print(f"   Schema: {'✅ Valid' if schema_result.is_valid else '❌ Invalid'}")
                
                if schema_result.errors:
                    print(f"   Schema Errors:")
                    for error in schema_result.errors:
                        print(f"      - {error}")
                
                if schema_result.warnings:
                    print(f"   Schema Warnings:")
                    for warning in schema_result.warnings:
                        print(f"      - {warning}")
                
            except Exception as e:
                print(f"❌ Schema validation failed for {file_path}: {e}")

def test_data_validation():
    """Test data validation specifically."""
    print("\n=== Data Validation Test ===")
    
    detector = FileTypeDetector()
    sample_files = [
        "sample_files/sample_invoice.edi",
        "sample_files/sample_order.xml", 
        "sample_files/sample_shipment.edifact"
    ]
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            try:
                file_type, _ = detector.detect_file_type(file_path)
                parser = ParserFactory.create_parser(file_type)
                validator = ValidatorFactory.create_validator(file_type)
                
                # Parse and validate data
                parsed_data = parser.parse(file_path)
                data_result = validator.validate_data(parsed_data)
                
                print(f"\n📁 {file_path}")
                print(f"   Type: {file_type}")
                print(f"   Data: {'✅ Valid' if data_result.is_valid else '❌ Invalid'}")
                print(f"   Fields: {len(parsed_data)}")
                
                if data_result.errors:
                    print(f"   Data Errors:")
                    for error in data_result.errors:
                        print(f"      - {error}")
                
                if data_result.warnings:
                    print(f"   Data Warnings:")
                    for warning in data_result.warnings:
                        print(f"      - {warning}")
                
            except Exception as e:
                print(f"❌ Data validation failed for {file_path}: {e}")

def test_validation_rules():
    """Test specific validation rules."""
    print("\n=== Validation Rules Test ===")
    
    # Test EDI validation rules
    edi_validator = ValidatorFactory.create_validator("EDI")
    print(f"📋 EDI Validation Rules:")
    print(f"   Required segments: {edi_validator.validation_rules['required_segments']}")
    print(f"   Required fields: {list(edi_validator.validation_rules['required_fields'].keys())}")
    
    # Test XML validation rules
    xml_validator = ValidatorFactory.create_validator("XML")
    print(f"\n📋 XML Validation Rules:")
    print(f"   Required elements: {xml_validator.validation_rules['required_elements']}")
    print(f"   Data types: {list(xml_validator.validation_rules['data_types'].keys())}")
    
    # Test Edifact validation rules
    edifact_validator = ValidatorFactory.create_validator("EDIFACT")
    print(f"\n📋 Edifact Validation Rules:")
    print(f"   Required segments: {edifact_validator.validation_rules['required_segments']}")
    print(f"   Required fields: {list(edifact_validator.validation_rules['required_fields'].keys())}")

def main():
    """Run all validation tests."""
    print("Validation System - Stage 4 Test")
    print("=" * 50)
    
    test_validation()
    test_schema_validation()
    test_data_validation()
    test_validation_rules()
    
    print("\n" + "=" * 50)
    print("✅ Stage 4 Validation Testing Complete!")

if __name__ == "__main__":
    main() 