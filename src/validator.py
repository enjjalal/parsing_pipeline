import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from lxml import etree
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class ValidationResult:
    """Container for validation results."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Add a validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a validation warning."""
        self.warnings.append(warning)
    
    def __str__(self):
        status = "✅ Valid" if self.is_valid else "❌ Invalid"
        result = [f"Validation Result: {status}"]
        
        if self.errors:
            result.append(f"Errors ({len(self.errors)}):")
            for error in self.errors:
                result.append(f"  - {error}")
        
        if self.warnings:
            result.append(f"Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                result.append(f"  - {warning}")
        
        return "\n".join(result)

class BaseValidator:
    """Base class for all validators."""
    
    def __init__(self):
        self.validation_rules = {}
    
    def validate(self, file_path: str, parsed_data: List[Dict[str, Any]]) -> ValidationResult:
        """Validate file and parsed data."""
        raise NotImplementedError
    
    def validate_schema(self, file_path: str) -> ValidationResult:
        """Validate file schema/structure."""
        raise NotImplementedError
    
    def validate_data(self, parsed_data: List[Dict[str, Any]]) -> ValidationResult:
        """Validate parsed data integrity."""
        raise NotImplementedError

class EDIValidator(BaseValidator):
    """Validator for EDI X12 files."""
    
    def __init__(self):
        super().__init__()
        self.validation_rules = {
            'required_segments': ['ISA', 'GS', 'ST', 'SE', 'GE', 'IEA'],
            'segment_patterns': {
                'ISA': r'^ISA\*[^*]{35}\*[^*]{35}\*[^*]{2,3}\*[^*]{2,3}\*[^*]{6}\*[^*]{4}\*[^*]{1}\*[^*]{2}\*[^*]{1}\*[^*]{1}\*[^*]{1}\*[^*]{1}\*[^*]{9}\*[^*]{1}\*[^*]{1}\*[^*]{1}\*[^*]{1}\*~$',
                'GS': r'^GS\*[^*]{2}\*[^*]{2,15}\*[^*]{2,15}\*[^*]{8}\*[^*]{8}\*[^*]{1,9}\*[^*]{1,2}\*[^*]{2}\*[^*]{1,12}\*~$',
                'ST': r'^ST\*[^*]{3}\*[^*]{4,9}\*~$',
                'SE': r'^SE\*[^*]{1,6}\*[^*]{4,9}\*~$',
                'GE': r'^GE\*[^*]{1,6}\*[^*]{1,9}\*~$',
                'IEA': r'^IEA\*[^*]{1,5}\*[^*]{9,15}\*~$'
            },
            'required_fields': {
                'ISA': ['interchange_sender_id', 'interchange_receiver_id', 'interchange_date'],
                'GS': ['functional_identifier_code', 'application_sender_code', 'application_receiver_code'],
                'ST': ['transaction_set_identifier_code', 'transaction_set_control_number']
            }
        }
    
    def validate(self, file_path: str, parsed_data: List[Dict[str, Any]]) -> ValidationResult:
        """Validate EDI file and parsed data."""
        result = ValidationResult(True)
        
        # Validate schema
        schema_result = self.validate_schema(file_path)
        if not schema_result.is_valid:
            result.errors.extend(schema_result.errors)
            result.is_valid = False
        
        # Validate data
        data_result = self.validate_data(parsed_data)
        if not data_result.is_valid:
            result.errors.extend(data_result.errors)
            result.is_valid = False
        
        result.warnings.extend(schema_result.warnings)
        result.warnings.extend(data_result.warnings)
        
        return result
    
    def validate_schema(self, file_path: str) -> ValidationResult:
        """Validate EDI file schema."""
        result = ValidationResult(True)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for required segments
            segments = content.split('~')
            found_segments = []
            
            for segment in segments:
                if segment.strip():
                    segment_type = segment.split('*')[0] if '*' in segment else ''
                    if segment_type:
                        found_segments.append(segment_type)
            
            # Validate required segments
            for required_segment in self.validation_rules['required_segments']:
                if required_segment not in found_segments:
                    result.add_error(f"Missing required segment: {required_segment}")
            
            # Validate segment patterns
            for segment in segments:
                if segment.strip():
                    segment_type = segment.split('*')[0] if '*' in segment else ''
                    if segment_type in self.validation_rules['segment_patterns']:
                        pattern = self.validation_rules['segment_patterns'][segment_type]
                        if not re.match(pattern, segment + '~'):
                            result.add_warning(f"Segment {segment_type} may not follow standard format")
            
            # Check for proper delimiters
            if '~' not in content:
                result.add_error("Missing segment terminator (~)")
            
            if '*' not in content:
                result.add_error("Missing element separator (*)")
            
            logger.info(f"EDI schema validation completed: {len(result.errors)} errors, {len(result.warnings)} warnings")
            
        except Exception as e:
            result.add_error(f"Schema validation failed: {e}")
        
        return result
    
    def validate_data(self, parsed_data: List[Dict[str, Any]]) -> ValidationResult:
        """Validate parsed EDI data integrity."""
        result = ValidationResult(True)
        
        if not parsed_data:
            result.add_error("No parsed data found")
            return result
        
        # Group data by segment type
        segment_data = {}
        for item in parsed_data:
            segment_type = item.get('segment_type', '')
            if segment_type not in segment_data:
                segment_data[segment_type] = []
            segment_data[segment_type].append(item)
        
        # Validate required fields for each segment
        for segment_type, required_fields in self.validation_rules['required_fields'].items():
            if segment_type in segment_data:
                found_fields = [item['field_name'] for item in segment_data[segment_type]]
                for required_field in required_fields:
                    if required_field not in found_fields:
                        result.add_warning(f"Missing required field '{required_field}' in segment {segment_type}")
        
        # Validate data types and formats
        for item in parsed_data:
            field_name = item.get('field_name', '')
            field_value = item.get('field_value', '')
            
            # Validate date fields
            if 'date' in field_name.lower():
                if not self._validate_date_format(field_value):
                    result.add_warning(f"Date field '{field_name}' may have invalid format: {field_value}")
            
            # Validate numeric fields
            if any(keyword in field_name.lower() for keyword in ['amount', 'price', 'quantity', 'number']):
                if not self._validate_numeric_format(field_value):
                    result.add_warning(f"Numeric field '{field_name}' may have invalid format: {field_value}")
        
        logger.info(f"EDI data validation completed: {len(result.errors)} errors, {len(result.warnings)} warnings")
        
        return result
    
    def _validate_date_format(self, value: str) -> bool:
        """Validate date format (YYMMDD or CCYYMMDD)."""
        if not value:
            return False
        
        # Check for YYMMDD or CCYYMMDD format
        if len(value) == 6:  # YYMMDD
            return re.match(r'^\d{6}$', value) is not None
        elif len(value) == 8:  # CCYYMMDD
            return re.match(r'^\d{8}$', value) is not None
        
        return False
    
    def _validate_numeric_format(self, value: str) -> bool:
        """Validate numeric format."""
        if not value:
            return False
        
        # Allow decimal numbers and integers
        return re.match(r'^\d+(\.\d+)?$', value) is not None

class XMLValidator(BaseValidator):
    """Validator for XML files."""
    
    def __init__(self):
        super().__init__()
        self.validation_rules = {
            'required_elements': ['order_id', 'order_date', 'customer_name'],
            'data_types': {
                'order_id': 'string',
                'order_date': 'date',
                'quantity': 'integer',
                'unit_price': 'decimal',
                'total': 'decimal'
            }
        }
    
    def validate(self, file_path: str, parsed_data: List[Dict[str, Any]]) -> ValidationResult:
        """Validate XML file and parsed data."""
        result = ValidationResult(True)
        
        # Validate schema
        schema_result = self.validate_schema(file_path)
        if not schema_result.is_valid:
            result.errors.extend(schema_result.errors)
            result.is_valid = False
        
        # Validate data
        data_result = self.validate_data(parsed_data)
        if not data_result.is_valid:
            result.errors.extend(data_result.errors)
            result.is_valid = False
        
        result.warnings.extend(schema_result.warnings)
        result.warnings.extend(data_result.warnings)
        
        return result
    
    def validate_schema(self, file_path: str) -> ValidationResult:
        """Validate XML file schema."""
        result = ValidationResult(True)
        
        try:
            # Parse XML to check well-formedness
            tree = etree.parse(file_path)
            root = tree.getroot()
            
            # Check for root element
            if root is None:
                result.add_error("No root element found")
            
            # Check for required elements
            found_elements = []
            for elem in root.iter():
                found_elements.append(elem.tag)
            
            for required_element in self.validation_rules['required_elements']:
                if required_element not in found_elements:
                    result.add_warning(f"Missing recommended element: {required_element}")
            
            # Check for proper XML structure
            if len(root) == 0:
                result.add_warning("XML file appears to be empty or has no child elements")
            
            logger.info(f"XML schema validation completed: {len(result.errors)} errors, {len(result.warnings)} warnings")
            
        except etree.XMLSyntaxError as e:
            result.add_error(f"XML syntax error: {e}")
        except Exception as e:
            result.add_error(f"Schema validation failed: {e}")
        
        return result
    
    def validate_data(self, parsed_data: List[Dict[str, Any]]) -> ValidationResult:
        """Validate parsed XML data integrity."""
        result = ValidationResult(True)
        
        if not parsed_data:
            result.add_error("No parsed data found")
            return result
        
        # Check for required elements
        found_fields = [item['field_name'] for item in parsed_data]
        for required_element in self.validation_rules['required_elements']:
            if required_element not in found_fields:
                result.add_warning(f"Missing recommended element: {required_element}")
        
        # Validate data types
        for item in parsed_data:
            field_name = item.get('field_name', '')
            field_value = item.get('field_value', '')
            
            if field_name in self.validation_rules['data_types']:
                expected_type = self.validation_rules['data_types'][field_name]
                if not self._validate_data_type(field_value, expected_type):
                    result.add_warning(f"Field '{field_name}' may have incorrect data type. Expected: {expected_type}, Value: {field_value}")
        
        logger.info(f"XML data validation completed: {len(result.errors)} errors, {len(result.warnings)} warnings")
        
        return result
    
    def _validate_data_type(self, value: str, expected_type: str) -> bool:
        """Validate data type."""
        if not value:
            return False
        
        if expected_type == 'string':
            return True
        elif expected_type == 'integer':
            return re.match(r'^\d+$', value) is not None
        elif expected_type == 'decimal':
            return re.match(r'^\d+(\.\d+)?$', value) is not None
        elif expected_type == 'date':
            return re.match(r'^\d{4}-\d{2}-\d{2}$', value) is not None
        
        return True

class EdifactValidator(BaseValidator):
    """Validator for EDIFACT files."""
    
    def __init__(self):
        super().__init__()
        self.validation_rules = {
            'required_segments': ['UNB', 'UNG', 'UNH', 'UNT', 'UNE', 'UNZ'],
            'segment_patterns': {
                'UNB': r'^UNB\+[^+]+',
                'UNG': r'^UNG\+[^+]+',
                'UNH': r'^UNH\+[^+]+',
                'UNT': r'^UNT\+[^+]+',
                'UNE': r'^UNE\+[^+]+',
                'UNZ': r'^UNZ\+[^+]+'
            },
            'required_fields': {
                'UNB': ['syntax_identifier', 'sender_identification', 'receiver_identification'],
                'UNH': ['message_reference_number', 'message_identifier']
            }
        }
    
    def validate(self, file_path: str, parsed_data: List[Dict[str, Any]]) -> ValidationResult:
        """Validate EDIFACT file and parsed data."""
        result = ValidationResult(True)
        
        # Validate schema
        schema_result = self.validate_schema(file_path)
        if not schema_result.is_valid:
            result.errors.extend(schema_result.errors)
            result.is_valid = False
        
        # Validate data
        data_result = self.validate_data(parsed_data)
        if not data_result.is_valid:
            result.errors.extend(data_result.errors)
            result.is_valid = False
        
        result.warnings.extend(schema_result.warnings)
        result.warnings.extend(data_result.warnings)
        
        return result
    
    def validate_schema(self, file_path: str) -> ValidationResult:
        """Validate EDIFACT file schema."""
        result = ValidationResult(True)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for required segments
            segments = content.split("'")
            found_segments = []
            
            for segment in segments:
                if segment.strip():
                    segment_type = segment.split('+')[0] if '+' in segment else ''
                    if segment_type:
                        found_segments.append(segment_type)
            
            # Validate required segments
            for required_segment in self.validation_rules['required_segments']:
                if required_segment not in found_segments:
                    result.add_error(f"Missing required segment: {required_segment}")
            
            # Validate segment patterns
            for segment in segments:
                if segment.strip():
                    segment_type = segment.split('+')[0] if '+' in segment else ''
                    if segment_type in self.validation_rules['segment_patterns']:
                        pattern = self.validation_rules['segment_patterns'][segment_type]
                        if not re.match(pattern, segment):
                            result.add_warning(f"Segment {segment_type} may not follow standard format")
            
            # Check for proper delimiters
            if "'" not in content:
                result.add_error("Missing segment terminator (')")
            
            if '+' not in content:
                result.add_error("Missing element separator (+)")
            
            logger.info(f"EDIFACT schema validation completed: {len(result.errors)} errors, {len(result.warnings)} warnings")
            
        except Exception as e:
            result.add_error(f"Schema validation failed: {e}")
        
        return result
    
    def validate_data(self, parsed_data: List[Dict[str, Any]]) -> ValidationResult:
        """Validate parsed EDIFACT data integrity."""
        result = ValidationResult(True)
        
        if not parsed_data:
            result.add_error("No parsed data found")
            return result
        
        # Group data by segment type
        segment_data = {}
        for item in parsed_data:
            segment_type = item.get('segment_type', '')
            if segment_type not in segment_data:
                segment_data[segment_type] = []
            segment_data[segment_type].append(item)
        
        # Validate required fields for each segment
        for segment_type, required_fields in self.validation_rules['required_fields'].items():
            if segment_type in segment_data:
                found_fields = [item['field_name'] for item in segment_data[segment_type]]
                for required_field in required_fields:
                    if required_field not in found_fields:
                        result.add_warning(f"Missing required field '{required_field}' in segment {segment_type}")
        
        # Validate data types and formats
        for item in parsed_data:
            field_name = item.get('field_name', '')
            field_value = item.get('field_value', '')
            
            # Validate date fields
            if 'date' in field_name.lower() or 'time' in field_name.lower():
                if not self._validate_date_format(field_value):
                    result.add_warning(f"Date/time field '{field_name}' may have invalid format: {field_value}")
            
            # Validate numeric fields
            if any(keyword in field_name.lower() for keyword in ['quantity', 'price', 'amount', 'number']):
                if not self._validate_numeric_format(field_value):
                    result.add_warning(f"Numeric field '{field_name}' may have invalid format: {field_value}")
        
        logger.info(f"EDIFACT data validation completed: {len(result.errors)} errors, {len(result.warnings)} warnings")
        
        return result
    
    def _validate_date_format(self, value: str) -> bool:
        """Validate date format (YYMMDDHHMM)."""
        if not value:
            return False
        
        # Check for YYMMDDHHMM format
        if len(value) == 10:
            return re.match(r'^\d{10}$', value) is not None
        elif len(value) == 6:  # YYMMDD
            return re.match(r'^\d{6}$', value) is not None
        
        return False
    
    def _validate_numeric_format(self, value: str) -> bool:
        """Validate numeric format."""
        if not value:
            return False
        
        # Allow decimal numbers and integers
        return re.match(r'^\d+(\.\d+)?$', value) is not None

class ValidatorFactory:
    """Factory class to create appropriate validator based on file type."""
    
    @staticmethod
    def create_validator(file_type: str) -> BaseValidator:
        """Create validator instance based on file type."""
        if file_type == "EDI":
            return EDIValidator()
        elif file_type == "XML":
            return XMLValidator()
        elif file_type == "EDIFACT":
            return EdifactValidator()
        else:
            raise ValueError(f"Unsupported file type for validation: {file_type}") 