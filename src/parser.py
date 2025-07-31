import re
import logging
from typing import Dict, List, Any, Optional
from lxml import etree
from config import FILE_PATTERNS

logger = logging.getLogger(__name__)

class BaseParser:
    """Base class for all parsers."""
    
    def __init__(self):
        self.extracted_data = []
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse file and return extracted data."""
        raise NotImplementedError
    
    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """Validate parsed data."""
        return len(data) > 0
    
    def extract_fields(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract specific fields from parsed data."""
        return data

class EDIParser(BaseParser):
    """Parser for EDI X12 files."""
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse EDI X12 file and extract segments and elements."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Split into segments
            segments = content.split('~')
            extracted_data = []
            position = 0
            
            for segment in segments:
                if not segment.strip():
                    continue
                
                # Split segment into elements
                elements = segment.split('*')
                if len(elements) < 2:
                    continue
                
                segment_type = elements[0]
                
                # Extract specific fields based on segment type
                if segment_type == 'ISA':
                    extracted_data.extend(self._parse_isa_segment(elements, position))
                elif segment_type == 'GS':
                    extracted_data.extend(self._parse_gs_segment(elements, position))
                elif segment_type == 'ST':
                    extracted_data.extend(self._parse_st_segment(elements, position))
                elif segment_type == 'BIG':
                    extracted_data.extend(self._parse_big_segment(elements, position))
                elif segment_type == 'N1':
                    extracted_data.extend(self._parse_n1_segment(elements, position))
                elif segment_type == 'IT1':
                    extracted_data.extend(self._parse_it1_segment(elements, position))
                elif segment_type == 'TDS':
                    extracted_data.extend(self._parse_tds_segment(elements, position))
                else:
                    # Generic segment parsing
                    for i, element in enumerate(elements[1:], 1):
                        if element.strip():
                            extracted_data.append({
                                'field_name': f'{segment_type}_element_{i}',
                                'field_value': element.strip(),
                                'segment_type': segment_type,
                                'position': position,
                                'confidence': 0.8
                            })
                
                position += 1
            
            logger.info(f"EDI parsing completed: {len(extracted_data)} fields extracted")
            return extracted_data
            
        except Exception as e:
            logger.error(f"EDI parsing failed: {e}")
            raise
    
    def _parse_isa_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse ISA (Interchange Control Header) segment."""
        fields = []
        field_mappings = {
            1: 'authorization_info_qualifier',
            2: 'authorization_info',
            3: 'security_info_qualifier', 
            4: 'security_info',
            5: 'interchange_sender_id_qualifier',
            6: 'interchange_sender_id',
            7: 'interchange_receiver_id_qualifier',
            8: 'interchange_receiver_id',
            9: 'interchange_date',
            10: 'interchange_time',
            11: 'repetition_separator',
            12: 'interchange_control_version_number',
            13: 'interchange_control_number',
            14: 'acknowledgment_requested',
            15: 'usage_indicator'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'ISA',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields
    
    def _parse_gs_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse GS (Functional Group Header) segment."""
        fields = []
        field_mappings = {
            1: 'functional_identifier_code',
            2: 'application_sender_code',
            3: 'application_receiver_code',
            4: 'date',
            5: 'time',
            6: 'group_control_number',
            7: 'responsible_agency_code',
            8: 'version_identifier_code'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'GS',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields
    
    def _parse_st_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse ST (Transaction Set Header) segment."""
        fields = []
        field_mappings = {
            1: 'transaction_set_identifier_code',
            2: 'transaction_set_control_number'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'ST',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields
    
    def _parse_big_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse BIG (Beginning Segment for Invoice) segment."""
        fields = []
        field_mappings = {
            1: 'invoice_date',
            2: 'invoice_number',
            3: 'purchase_order_date',
            4: 'purchase_order_number'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'BIG',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields
    
    def _parse_n1_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse N1 (Name) segment."""
        fields = []
        field_mappings = {
            1: 'entity_identifier_code',
            2: 'name'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'N1',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields
    
    def _parse_it1_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse IT1 (Baseline Item Data) segment."""
        fields = []
        field_mappings = {
            1: 'assigned_identification',
            2: 'quantity_invoiced',
            3: 'unit_of_measurement_code',
            4: 'unit_price',
            5: 'basis_of_unit_price_code',
            6: 'product_service_id_qualifier',
            7: 'product_service_id',
            8: 'product_service_description'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'IT1',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields
    
    def _parse_tds_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse TDS (Total Monetary Value Summary) segment."""
        fields = []
        field_mappings = {
            1: 'total_amount'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'TDS',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields

class XMLParser(BaseParser):
    """Parser for XML files."""
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse XML file and extract elements."""
        try:
            tree = etree.parse(file_path)
            root = tree.getroot()
            
            extracted_data = []
            position = 0
            
            # Extract all elements recursively
            for element in root.iter():
                if element.text and element.text.strip():
                    extracted_data.append({
                        'field_name': element.tag,
                        'field_value': element.text.strip(),
                        'segment_type': 'XML_ELEMENT',
                        'position': position,
                        'confidence': 0.9
                    })
                    position += 1
                
                # Extract attributes
                for attr_name, attr_value in element.attrib.items():
                    extracted_data.append({
                        'field_name': f"{element.tag}_{attr_name}",
                        'field_value': attr_value,
                        'segment_type': 'XML_ATTRIBUTE',
                        'position': position,
                        'confidence': 0.9
                    })
                    position += 1
            
            logger.info(f"XML parsing completed: {len(extracted_data)} fields extracted")
            return extracted_data
            
        except Exception as e:
            logger.error(f"XML parsing failed: {e}")
            raise
    
    def extract_fields(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract specific business fields from XML data."""
        business_fields = []
        
        for item in data:
            field_name = item['field_name']
            field_value = item['field_value']
            
            # Map common business fields
            if field_name in ['order_id', 'order_date', 'customer_id', 'customer_name']:
                business_fields.append(item)
            elif field_name in ['product_id', 'description', 'quantity', 'unit_price', 'total_price']:
                business_fields.append(item)
            elif field_name in ['subtotal', 'tax', 'shipping', 'total']:
                business_fields.append(item)
            elif 'street' in field_name or 'city' in field_name or 'state' in field_name or 'zip' in field_name:
                business_fields.append(item)
        
        return business_fields

class EdifactParser(BaseParser):
    """Parser for EDIFACT files."""
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse EDIFACT file and extract segments and elements."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Split into segments
            segments = content.split("'")
            extracted_data = []
            position = 0
            
            for segment in segments:
                if not segment.strip():
                    continue
                
                # Split segment into elements
                elements = segment.split('+')
                if len(elements) < 1:
                    continue
                
                segment_type = elements[0]
                
                # Extract specific fields based on segment type
                if segment_type == 'UNB':
                    extracted_data.extend(self._parse_unb_segment(elements, position))
                elif segment_type == 'UNG':
                    extracted_data.extend(self._parse_ung_segment(elements, position))
                elif segment_type == 'UNH':
                    extracted_data.extend(self._parse_unh_segment(elements, position))
                elif segment_type == 'BGM':
                    extracted_data.extend(self._parse_bgm_segment(elements, position))
                elif segment_type == 'DTM':
                    extracted_data.extend(self._parse_dtm_segment(elements, position))
                elif segment_type == 'NAD':
                    extracted_data.extend(self._parse_nad_segment(elements, position))
                elif segment_type == 'LIN':
                    extracted_data.extend(self._parse_lin_segment(elements, position))
                elif segment_type == 'QTY':
                    extracted_data.extend(self._parse_qty_segment(elements, position))
                elif segment_type == 'PRI':
                    extracted_data.extend(self._parse_pri_segment(elements, position))
                else:
                    # Generic segment parsing
                    for i, element in enumerate(elements[1:], 1):
                        if element.strip():
                            extracted_data.append({
                                'field_name': f'{segment_type}_element_{i}',
                                'field_value': element.strip(),
                                'segment_type': segment_type,
                                'position': position,
                                'confidence': 0.8
                            })
                
                position += 1
            
            logger.info(f"EDIFACT parsing completed: {len(extracted_data)} fields extracted")
            return extracted_data
            
        except Exception as e:
            logger.error(f"EDIFACT parsing failed: {e}")
            raise
    
    def _parse_unb_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse UNB (Interchange Header) segment."""
        fields = []
        field_mappings = {
            1: 'syntax_identifier',
            2: 'syntax_version_number',
            3: 'sender_identification',
            4: 'receiver_identification',
            5: 'date_time',
            6: 'interchange_reference_number'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'UNB',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields
    
    def _parse_ung_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse UNG (Functional Group Header) segment."""
        fields = []
        field_mappings = {
            1: 'functional_group_identifier',
            2: 'application_sender_identification',
            3: 'application_receiver_identification',
            4: 'date_time',
            5: 'group_reference_number',
            6: 'controlling_agency',
            7: 'message_version_number'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'UNG',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields
    
    def _parse_unh_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse UNH (Message Header) segment."""
        fields = []
        field_mappings = {
            1: 'message_reference_number',
            2: 'message_identifier'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'UNH',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields
    
    def _parse_bgm_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse BGM (Beginning of Message) segment."""
        fields = []
        field_mappings = {
            1: 'document_message_name_code',
            2: 'document_identifier',
            3: 'message_function_code'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'BGM',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields
    
    def _parse_dtm_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse DTM (Date/Time/Period) segment."""
        fields = []
        field_mappings = {
            1: 'date_time_period_qualifier',
            2: 'date_time_period'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'DTM',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields
    
    def _parse_nad_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse NAD (Name and Address) segment."""
        fields = []
        field_mappings = {
            1: 'party_function_code_qualifier',
            2: 'party_identification_details',
            3: 'name_and_address'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'NAD',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields
    
    def _parse_lin_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse LIN (Line Item) segment."""
        fields = []
        field_mappings = {
            1: 'line_item_identifier',
            2: 'item_number_identification'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'LIN',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields
    
    def _parse_qty_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse QTY (Quantity) segment."""
        fields = []
        field_mappings = {
            1: 'quantity_qualifier',
            2: 'quantity',
            3: 'measure_unit_qualifier'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'QTY',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields
    
    def _parse_pri_segment(self, elements: List[str], position: int) -> List[Dict[str, Any]]:
        """Parse PRI (Price Details) segment."""
        fields = []
        field_mappings = {
            1: 'price_qualifier',
            2: 'price',
            3: 'price_type_qualifier'
        }
        
        for i, element in enumerate(elements[1:], 1):
            if i in field_mappings and element.strip():
                fields.append({
                    'field_name': field_mappings[i],
                    'field_value': element.strip(),
                    'segment_type': 'PRI',
                    'position': position,
                    'confidence': 0.9
                })
        
        return fields

class ParserFactory:
    """Factory class to create appropriate parser based on file type."""
    
    @staticmethod
    def create_parser(file_type: str) -> BaseParser:
        """Create parser instance based on file type."""
        if file_type == "EDI":
            return EDIParser()
        elif file_type == "XML":
            return XMLParser()
        elif file_type == "EDIFACT":
            return EdifactParser()
        else:
            raise ValueError(f"Unsupported file type: {file_type}") 