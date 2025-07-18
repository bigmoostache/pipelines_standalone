import zipfile
import xml.etree.ElementTree as ET
import io
import re
import base64
import logging
from typing import Dict, List, Optional, Tuple, Any, Union


class ConversionError(Exception):
    """Custom exception for conversion errors."""
    pass


class DocxToHtmlConverter:
    def __init__(self, debug: bool = False):
        # Configure logging for better error tracking
        self.logger = logging.getLogger(__name__)
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        
        # DOCX XML namespaces - will be dynamically discovered and updated
        self.namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
            'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
            'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
            'v': 'urn:schemas-microsoft-com:vml'
        }
        
        # NEW: Namespace discovery and fallback system
        self.discovered_namespaces = {}
        self.namespace_mappings = {}
        
        # Known namespace patterns for different Office versions
        self.known_namespace_patterns = {
            'wordprocessing': [
                'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                'http://schemas.microsoft.com/office/word/2003/wordml',
                'http://purl.oclc.org/ooxml/wordprocessingml/main'
            ],
            'relationships': [
                'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
                'http://schemas.openxmlformats.org/package/2006/relationships',
                'http://purl.oclc.org/ooxml/officeDocument/relationships'
            ],
            'drawingml': [
                'http://schemas.openxmlformats.org/drawingml/2006/main',
                'http://purl.oclc.org/ooxml/drawingml/main'
            ],
            'wordprocessing_drawing': [
                'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
                'http://purl.oclc.org/ooxml/drawingml/wordprocessingDrawing'
            ],
            'picture': [
                'http://schemas.openxmlformats.org/drawingml/2006/picture',
                'http://purl.oclc.org/ooxml/drawingml/picture'
            ],
            'vml': [
                'urn:schemas-microsoft-com:vml',
                'http://www.w3.org/TR/NOTE-VML'
            ]
        }
        
        self.styles = {}
        self.numbering = {}
        self.relationships = {}
        self.theme_colors = {}
        self.fonts = {}  # Font definitions
        self.images = {}  # Store extracted images
        self.list_stack = []  # Track nested lists
        self.current_list_ids = {}  # Track current list IDs per level
        
        # Error tracking
        self.errors = []
        self.warnings = []
        
        # Common theme color mappings for Office documents
        self.default_theme_colors = {
            'dark1': '000000',
            'light1': 'FFFFFF', 
            'dark2': '44546A',
            'light2': 'E7E6E6',
            'accent1': '4472C4',
            'accent2': 'E7752F', 
            'accent3': 'A5A5A5',
            'accent4': 'FFC000',
            'accent5': '5B9BD5',
            'accent6': '70AD47',
            'hyperlink': '0563C1',
            'followedHyperlink': '954F72'
        }
        
        # Default font mappings for common Office fonts
        self.default_fonts = {
            'Calibri': 'Calibri, sans-serif',
            'Arial': 'Arial, sans-serif',
            'Times New Roman': 'Times New Roman, serif',
            'Helvetica': 'Helvetica, sans-serif',
            'Verdana': 'Verdana, sans-serif',
            'Georgia': 'Georgia, serif',
            'Courier New': 'Courier New, monospace'
        }

    # NEW: Dynamic namespace discovery methods
    def _discover_namespaces_from_xml(self, xml_content: str) -> Dict[str, str]:
        """Dynamically discover namespaces from XML content."""
        try:
            root = ET.fromstring(xml_content)
            namespaces = {}
            
            # Extract namespace declarations from the root element
            for attr_name, attr_value in root.attrib.items():
                if attr_name.startswith('xmlns'):
                    if attr_name == 'xmlns':
                        namespaces['default'] = attr_value
                    else:
                        ns_prefix = attr_name.split(':', 1)[1]
                        namespaces[ns_prefix] = attr_value
            
            # Also check the tag itself for namespace info
            if '}' in root.tag:
                default_ns = root.tag.split('}')[0][1:]
                if 'default' not in namespaces:
                    namespaces['default'] = default_ns
            
            return namespaces
            
        except Exception as e:
            self.warnings.append(f"Could not discover namespaces: {str(e)}")
            return {}

    def _update_namespace_mappings(self, discovered_ns: Dict[str, str]):
        """Update namespace mappings based on discovered namespaces."""
        try:
            # Map discovered namespaces to our expected prefixes
            for prefix, uri in discovered_ns.items():
                # Check which known pattern this URI matches
                for ns_type, patterns in self.known_namespace_patterns.items():
                    if any(pattern in uri or uri in pattern for pattern in patterns):
                        if ns_type == 'wordprocessing':
                            self.namespaces['w'] = uri
                        elif ns_type == 'relationships':
                            self.namespaces['r'] = uri
                        elif ns_type == 'drawingml':
                            self.namespaces['a'] = uri
                        elif ns_type == 'wordprocessing_drawing':
                            self.namespaces['wp'] = uri
                        elif ns_type == 'picture':
                            self.namespaces['pic'] = uri
                        elif ns_type == 'vml':
                            self.namespaces['v'] = uri
                        break
            
            self.logger.debug(f"Updated namespaces: {self.namespaces}")
            
        except Exception as e:
            self.warnings.append(f"Error updating namespace mappings: {str(e)}")

    def _robust_find(self, parent: ET.Element, xpath: str, namespaces: Dict[str, str] = None) -> List[ET.Element]:
        """Robust element finding that falls back to local name matching."""
        if namespaces is None:
            namespaces = self.namespaces
            
        try:
            # First try with provided namespaces
            elements = parent.findall(xpath, namespaces)
            if elements:
                return elements
        except Exception:
            pass
        
        # Fallback: extract local names and search by them
        try:
            # Parse the xpath to extract local names
            local_names = re.findall(r'([a-zA-Z_][a-zA-Z0-9_-]*):([a-zA-Z_][a-zA-Z0-9_-]*)', xpath)
            if local_names:
                # Search by local name
                target_local_name = local_names[-1][1]  # Get the last local name
                elements = []
                for elem in parent.iter():
                    elem_local_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                    if elem_local_name == target_local_name:
                        elements.append(elem)
                return elements
        except Exception:
            pass
            
        return []

    def _robust_find_one(self, parent: ET.Element, xpath: str, namespaces: Dict[str, str] = None) -> Optional[ET.Element]:
        """Robust single element finding."""
        elements = self._robust_find(parent, xpath, namespaces)
        return elements[0] if elements else None

    def _robust_get_attribute(self, element: ET.Element, attr_name: str, namespace_prefix: str = None) -> Optional[str]:
        """Robust attribute getting that handles namespace variations."""
        # Try direct attribute access first
        if attr_name in element.attrib:
            return element.attrib[attr_name]
        
        # Try with namespace
        if namespace_prefix and namespace_prefix in self.namespaces:
            namespaced_attr = f'{{{self.namespaces[namespace_prefix]}}}{attr_name}'
            if namespaced_attr in element.attrib:
                return element.attrib[namespaced_attr]
        
        # Fallback: search by local name
        for full_attr_name, attr_value in element.attrib.items():
            local_attr_name = full_attr_name.split('}')[-1] if '}' in full_attr_name else full_attr_name
            if local_attr_name == attr_name:
                return attr_value
        
        return None

    def convert_docx_to_html(self, docx_bytes: bytes) -> str:
        """
        Convert DOCX bytes to HTML string with preserved formatting.
        
        Args:
            docx_bytes (bytes): The DOCX file content as bytes
            
        Returns:
            str: HTML string with preserved formatting
            
        Raises:
            ConversionError: If conversion fails due to invalid DOCX structure
        """
        try:
            # Validate input
            if not docx_bytes or len(docx_bytes) == 0:
                raise ConversionError("Input DOCX bytes are empty")
            
            # Parse the DOCX file (which is a ZIP archive)
            try:
                docx_zip = zipfile.ZipFile(io.BytesIO(docx_bytes), 'r')
            except zipfile.BadZipFile as e:
                raise ConversionError(f"Invalid DOCX file: not a valid ZIP archive - {str(e)}")
            
            with docx_zip:
                # Validate DOCX structure
                self._validate_docx_structure(docx_zip)
                
                # NEW: Discover and update namespaces from the main document
                try:
                    document_xml = docx_zip.read('word/document.xml').decode('utf-8')
                    self.discovered_namespaces = self._discover_namespaces_from_xml(document_xml)
                    self._update_namespace_mappings(self.discovered_namespaces)
                    self.logger.info(f"Discovered and updated namespaces: {self.namespaces}")
                except Exception as e:
                    self.warnings.append(f"Could not discover namespaces from document: {str(e)}")
                
                # Extract and parse various XML components with error handling
                self._safe_parse_theme_colors(docx_zip)
                self._safe_parse_fonts(docx_zip)
                self._safe_parse_styles(docx_zip)
                self._safe_parse_numbering(docx_zip)
                self._safe_parse_relationships(docx_zip)
                self._safe_extract_images(docx_zip)
                
                # Parse and convert to HTML
                html_content = self._safe_parse_document(document_xml)
                
                # Close any remaining open lists
                html_content += self._close_all_lists()
                
                # Log summary
                self.logger.info(f"Conversion completed. Errors: {len(self.errors)}, Warnings: {len(self.warnings)}")
                
                # Wrap in basic HTML structure
                return self._wrap_html(html_content)
                
        except ConversionError:
            raise
        except Exception as e:
            raise ConversionError(f"Unexpected error during conversion: {str(e)}")
    
    def _validate_docx_structure(self, docx_zip: zipfile.ZipFile):
        """Validate that the ZIP file contains required DOCX components."""
        required_files = ['word/document.xml', '[Content_Types].xml']
        file_list = docx_zip.namelist()
        
        for required_file in required_files:
            if required_file not in file_list:
                raise ConversionError(f"Invalid DOCX structure: missing {required_file}")
        
        # Check for relationships
        if 'word/_rels/document.xml.rels' not in file_list:
            self.warnings.append("Missing document relationships file")
    
    def _safe_extract_images(self, docx_zip: zipfile.ZipFile):
        """Extract images with comprehensive error handling."""
        try:
            file_list = docx_zip.namelist()
            image_files = [f for f in file_list if f.startswith('word/media/') and 
                          any(f.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.emf', '.wmf'])]
            
            for image_file in image_files:
                try:
                    image_data = docx_zip.read(image_file)
                    
                    # Validate image data
                    if len(image_data) == 0:
                        self.warnings.append(f"Empty image file: {image_file}")
                        continue
                    
                    # Determine MIME type
                    ext = image_file.lower().split('.')[-1]
                    mime_type_map = {
                        'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                        'gif': 'image/gif', 'bmp': 'image/bmp', 'tiff': 'image/tiff',
                        'emf': 'image/x-emf', 'wmf': 'image/x-wmf'
                    }
                    mime_type = mime_type_map.get(ext, 'image/png')
                    
                    # Convert to base64 with size limit (10MB)
                    if len(image_data) > 10 * 1024 * 1024:
                        self.warnings.append(f"Large image skipped (>10MB): {image_file}")
                        continue
                    
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    data_url = f"data:{mime_type};base64,{base64_data}"
                    
                    image_filename = image_file.split('/')[-1]
                    self.images[image_filename] = data_url
                    
                except Exception as e:
                    self.warnings.append(f"Could not process image {image_file}: {str(e)}")
                    
        except Exception as e:
            self.warnings.append(f"Could not extract images: {str(e)}")
    
    def _safe_parse_fonts(self, docx_zip: zipfile.ZipFile):
        """Parse font definitions with error handling."""
        try:
            if 'word/fontTable.xml' not in docx_zip.namelist():
                self.logger.debug("No fontTable.xml found")
                return
                
            font_xml = docx_zip.read('word/fontTable.xml').decode('utf-8')
            root = ET.fromstring(font_xml)
            
            # Discover namespaces from font table
            font_namespaces = self._discover_namespaces_from_xml(font_xml)
            temp_namespaces = self.namespaces.copy()
            self._update_namespace_mappings(font_namespaces)
            
            for font in self._robust_find(root, './/w:font'):
                try:
                    font_name = self._robust_get_attribute(font, 'name', 'w')
                    if font_name:
                        # Extract font family information
                        font_info = {'name': font_name}
                        
                        # Get font family type
                        family = self._robust_find_one(font, './/w:family')
                        if family is not None:
                            font_info['family'] = self._robust_get_attribute(family, 'val', 'w')
                        
                        # Get font pitch
                        pitch = self._robust_find_one(font, './/w:pitch')
                        if pitch is not None:
                            font_info['pitch'] = self._robust_get_attribute(pitch, 'val', 'w')
                        
                        # Map to CSS font family
                        css_family = self._map_font_to_css(font_name, font_info.get('family'))
                        font_info['css_family'] = css_family
                        
                        self.fonts[font_name] = font_info
                        
                except Exception as e:
                    self.warnings.append(f"Error parsing font definition: {str(e)}")
                    
        except Exception as e:
            self.warnings.append(f"Could not parse fonts: {str(e)}")
    
    def _map_font_to_css(self, font_name: str, font_family: Optional[str] = None) -> str:
        """Map DOCX font to appropriate CSS font family."""
        # First check if we have a direct mapping
        if font_name in self.default_fonts:
            return self.default_fonts[font_name]
        
        # Map based on font family type
        if font_family:
            family_map = {
                'swiss': 'sans-serif',
                'roman': 'serif', 
                'modern': 'monospace',
                'script': 'cursive',
                'decorative': 'fantasy'
            }
            generic_family = family_map.get(font_family.lower(), 'sans-serif')
            return f'"{font_name}", {generic_family}'
        
        # Default fallback
        return f'"{font_name}", sans-serif'
    
    def _safe_parse_theme_colors(self, docx_zip: zipfile.ZipFile):
        """Parse theme colors with comprehensive error handling."""
        try:
            if 'word/theme/theme1.xml' not in docx_zip.namelist():
                self.theme_colors = self.default_theme_colors.copy()
                self.logger.debug("No theme file found, using defaults")
                return
                
            theme_xml = docx_zip.read('word/theme/theme1.xml').decode('utf-8')
            root = ET.fromstring(theme_xml)
            
            # Discover namespaces from theme
            theme_namespaces = self._discover_namespaces_from_xml(theme_xml)
            
            color_scheme = self._robust_find_one(root, './/a:clrScheme')
            if color_scheme is not None:
                for color_elem in color_scheme:
                    try:
                        color_name = color_elem.tag.split('}')[-1] if '}' in color_elem.tag else color_elem.tag
                        
                        srgb_color = self._robust_find_one(color_elem, './/a:srgbClr')
                        sys_color = self._robust_find_one(color_elem, './/a:sysClr')
                        
                        if srgb_color is not None:
                            color_val = self._robust_get_attribute(srgb_color, 'val')
                            if color_val and self._is_valid_hex_color(color_val):
                                self.theme_colors[color_name] = color_val.upper()
                        elif sys_color is not None:
                            sys_val = (self._robust_get_attribute(sys_color, 'val') or '').lower()
                            sys_color_map = {
                                'windowtext': '000000',
                                'window': 'FFFFFF'
                            }
                            mapped_color = sys_color_map.get(sys_val, self.default_theme_colors.get(color_name, '000000'))
                            self.theme_colors[color_name] = mapped_color
                    except Exception as e:
                        self.warnings.append(f"Error parsing theme color {color_name}: {str(e)}")
            
            # Fill in any missing colors with defaults
            for color_name, default_color in self.default_theme_colors.items():
                if color_name not in self.theme_colors:
                    self.theme_colors[color_name] = default_color
                    
        except Exception as e:
            self.theme_colors = self.default_theme_colors.copy()
            self.warnings.append(f"Could not parse theme colors, using defaults: {str(e)}")
    
    def _is_valid_hex_color(self, color: str) -> bool:
        """Validate hex color format."""
        return bool(re.match(r'^[0-9A-Fa-f]{6}$', color))
    
    def _safe_parse_styles(self, docx_zip: zipfile.ZipFile):
        """Parse styles with comprehensive error handling."""
        try:
            if 'word/styles.xml' not in docx_zip.namelist():
                self.logger.debug("No styles.xml found")
                return
                
            styles_xml = docx_zip.read('word/styles.xml').decode('utf-8')
            root = ET.fromstring(styles_xml)
            
            # Discover namespaces from styles
            styles_namespaces = self._discover_namespaces_from_xml(styles_xml)
            
            for style in self._robust_find(root, './/w:style'):
                try:
                    style_id = self._robust_get_attribute(style, 'styleId', 'w')
                    style_type = self._robust_get_attribute(style, 'type', 'w')
                    if style_id:
                        style_props = self._parse_style_properties(style)
                        if style_props:
                            style_props['type'] = style_type
                            self.styles[style_id] = style_props
                except Exception as e:
                    self.warnings.append(f"Error parsing style {style_id}: {str(e)}")
                        
        except Exception as e:
            self.warnings.append(f"Could not parse styles: {str(e)}")
    
    def _safe_parse_numbering(self, docx_zip: zipfile.ZipFile):
        """Parse numbering with error handling."""
        try:
            if 'word/numbering.xml' not in docx_zip.namelist():
                self.logger.debug("No numbering.xml found")
                return
                
            numbering_xml = docx_zip.read('word/numbering.xml').decode('utf-8')
            root = ET.fromstring(numbering_xml)
            
            # Parse abstract numbering definitions
            abstract_nums = {}
            for abstract_num in self._robust_find(root, './/w:abstractNum'):
                try:
                    abstract_num_id = self._robust_get_attribute(abstract_num, 'abstractNumId', 'w')
                    if abstract_num_id:
                        abstract_nums[abstract_num_id] = self._parse_numbering_properties(abstract_num)
                except Exception as e:
                    self.warnings.append(f"Error parsing abstract numbering {abstract_num_id}: {str(e)}")
            
            # Parse numbering instances
            for num in self._robust_find(root, './/w:num'):
                try:
                    num_id = self._robust_get_attribute(num, 'numId', 'w')
                    if num_id:
                        abstract_num_ref = self._robust_find_one(num, './/w:abstractNumId')
                        if abstract_num_ref is not None:
                            abstract_id = self._robust_get_attribute(abstract_num_ref, 'val', 'w')
                            if abstract_id in abstract_nums:
                                self.numbering[num_id] = abstract_nums[abstract_id]
                except Exception as e:
                    self.warnings.append(f"Error parsing numbering {num_id}: {str(e)}")
                            
        except Exception as e:
            self.warnings.append(f"Could not parse numbering: {str(e)}")
    
    def _safe_parse_relationships(self, docx_zip: zipfile.ZipFile):
        """Parse relationships with error handling."""
        try:
            if 'word/_rels/document.xml.rels' not in docx_zip.namelist():
                self.logger.debug("No document relationships found")
                return
                
            rels_xml = docx_zip.read('word/_rels/document.xml.rels').decode('utf-8')
            root = ET.fromstring(rels_xml)
            
            # Discover namespaces from relationships
            rels_namespaces = self._discover_namespaces_from_xml(rels_xml)
            
            for rel in self._robust_find(root, './/r:Relationship'):
                try:
                    rel_id = self._robust_get_attribute(rel, 'Id')
                    target = self._robust_get_attribute(rel, 'Target')
                    rel_type = self._robust_get_attribute(rel, 'Type')
                    if rel_id and target:
                        self.relationships[rel_id] = {'target': target, 'type': rel_type}
                except Exception as e:
                    self.warnings.append(f"Error parsing relationship {rel_id}: {str(e)}")
        except Exception as e:
            self.warnings.append(f"Could not parse relationships: {str(e)}")
    
    def _safe_parse_document(self, document_xml: str) -> str:
        """Parse document with comprehensive error handling."""
        try:
            root = ET.fromstring(document_xml)
            html_parts = []
            
            body = self._robust_find_one(root, './/w:body')
            if body is not None:
                for element in body:
                    try:
                        html_content = self._process_element(element)
                        if html_content:
                            html_parts.append(html_content)
                    except Exception as e:
                        self.warnings.append(f"Error processing element {element.tag}: {str(e)}")
                        # Continue processing other elements
            else:
                raise ConversionError("No document body found")
            
            return '\n'.join(html_parts)
            
        except ET.ParseError as e:
            raise ConversionError(f"Invalid XML in document: {str(e)}")
        except Exception as e:
            raise ConversionError(f"Error parsing document: {str(e)}")
    
    def _process_element(self, element: ET.Element) -> str:
        """Process a single document element and convert to HTML."""
        try:
            tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
            
            if tag == 'p':  # Paragraph
                return self._process_paragraph(element)
            elif tag == 'tbl':  # Table
                return self._process_table_enhanced(element)
            elif tag == 'sectPr':  # Section properties - ignore
                return ''
            else:
                # Process children for unknown elements
                html_parts = []
                for child in element:
                    html_content = self._process_element(child)
                    if html_content:
                        html_parts.append(html_content)
                return ''.join(html_parts)
        except Exception as e:
            self.warnings.append(f"Error processing element: {str(e)}")
            return ''
    
    def _process_table_enhanced(self, table: ET.Element) -> str:
        """Enhanced table processing with advanced formatting."""
        try:
            # Close any open lists before table
            list_closure = self._close_all_lists() if self.list_stack else ''
            
            html_parts = []
            if list_closure:
                html_parts.append(list_closure)
            
            # Parse table properties
            table_props = self._parse_table_properties(table)
            table_style = self._generate_table_style(table_props)
            
            html_parts.append(f'<table{table_style}>')
            
            # Process table grid for column information
            table_grid = self._robust_find_one(table, './/w:tblGrid')
            col_widths = self._parse_table_grid(table_grid) if table_grid is not None else []
            
            # Add column definitions if we have width information
            if col_widths:
                html_parts.append('<colgroup>')
                for width in col_widths:
                    if width:
                        html_parts.append(f'<col style="width: {width};" />')
                    else:
                        html_parts.append('<col />')
                html_parts.append('</colgroup>')
            
            # Process rows
            for row in self._robust_find(table, './/w:tr'):
                try:
                    row_html = self._process_table_row_enhanced(row)
                    if row_html:
                        html_parts.append(row_html)
                except Exception as e:
                    self.warnings.append(f"Error processing table row: {str(e)}")
            
            html_parts.append('</table>')
            return '\n'.join(html_parts)
            
        except Exception as e:
            self.warnings.append(f"Error processing table: {str(e)}")
            return '<p>[Table conversion error]</p>'
    
    def _parse_table_properties(self, table: ET.Element) -> Dict[str, Any]:
        """Parse table-level properties."""
        props = {}
        
        try:
            tbl_pr = self._robust_find_one(table, './/w:tblPr')
            if tbl_pr is not None:
                # Table borders
                borders = self._robust_find_one(tbl_pr, './/w:tblBorders')
                if borders is not None:
                    props['borders'] = self._parse_table_borders(borders)
                
                # Table width
                width = self._robust_find_one(tbl_pr, './/w:tblW')
                if width is not None:
                    w_type = self._robust_get_attribute(width, 'type', 'w')
                    w_val = self._robust_get_attribute(width, 'w', 'w')
                    if w_type and w_val:
                        props['width'] = {'type': w_type, 'value': w_val}
                
                # Table alignment
                jc = self._robust_find_one(tbl_pr, './/w:jc')
                if jc is not None:
                    props['alignment'] = self._robust_get_attribute(jc, 'val', 'w')
        
        except Exception as e:
            self.warnings.append(f"Error parsing table properties: {str(e)}")
        
        return props
    
    def _parse_table_borders(self, borders: ET.Element) -> Dict[str, str]:
        """Parse table border definitions."""
        border_props = {}
        
        border_sides = ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']
        for side in border_sides:
            border_elem = self._robust_find_one(borders, f'.//w:{side}')
            if border_elem is not None:
                border_val = self._robust_get_attribute(border_elem, 'val', 'w')
                border_sz = self._robust_get_attribute(border_elem, 'sz', 'w')
                border_color = self._robust_get_attribute(border_elem, 'color', 'w')
                
                if border_val and border_val != 'none':
                    css_side = {'insideH': 'horizontal', 'insideV': 'vertical'}.get(side, side)
                    border_width = f"{int(border_sz or '4') // 8}px" if border_sz else '1px'
                    border_style = 'solid' if border_val in ['single', 'thick'] else 'solid'
                    color = f"#{border_color}" if border_color and border_color != 'auto' else '#000000'
                    
                    border_props[css_side] = f"{border_width} {border_style} {color}"
        
        return border_props
    
    def _generate_table_style(self, table_props: Dict[str, Any]) -> str:
        """Generate CSS style for table from properties."""
        styles = ['border-collapse: collapse']
        
        # Width
        if 'width' in table_props:
            width_info = table_props['width']
            if width_info['type'] == 'pct':
                width_pct = int(width_info['value']) / 50  # DOCX uses 50ths of percent
                styles.append(f'width: {width_pct}%')
            elif width_info['type'] == 'dxa':
                width_px = int(width_info['value']) / 20  # Convert twentieths of a point to pixels
                styles.append(f'width: {width_px}px')
        
        # Alignment
        if 'alignment' in table_props:
            align_map = {'left': 'left', 'center': 'center', 'right': 'right'}
            alignment = align_map.get(table_props['alignment'], 'left')
            if alignment == 'center':
                styles.append('margin: 0 auto')
            elif alignment == 'right':
                styles.append('margin-left: auto')
        
        # Borders
        if 'borders' in table_props:
            borders = table_props['borders']
            for side, border_def in borders.items():
                if side in ['top', 'left', 'bottom', 'right']:
                    styles.append(f'border-{side}: {border_def}')
        
        return f' style="{"; ".join(styles)};"' if styles else ''
    
    def _parse_table_grid(self, grid: ET.Element) -> List[Optional[str]]:
        """Parse table grid for column widths."""
        widths = []
        
        try:
            for grid_col in self._robust_find(grid, './/w:gridCol'):
                width_attr = self._robust_get_attribute(grid_col, 'w', 'w')
                if width_attr:
                    # Convert twentieths of a point to pixels (rough approximation)
                    width_px = int(width_attr) / 20
                    widths.append(f'{width_px}px')
                else:
                    widths.append(None)
        except Exception as e:
            self.warnings.append(f"Error parsing table grid: {str(e)}")
        
        return widths
    
    def _process_table_row_enhanced(self, row: ET.Element) -> str:
        """Enhanced table row processing with cell properties."""
        try:
            html_parts = ['<tr>']
            
            for cell in self._robust_find(row, './/w:tc'):
                cell_html = self._process_table_cell_enhanced(cell)
                if cell_html:
                    html_parts.append(cell_html)
            
            html_parts.append('</tr>')
            return '\n'.join(html_parts)
            
        except Exception as e:
            self.warnings.append(f"Error processing table row: {str(e)}")
            return ''
    
    def _process_table_cell_enhanced(self, cell: ET.Element) -> str:
        """Enhanced table cell processing with spanning and alignment."""
        try:
            # Parse cell properties
            cell_props = self._parse_cell_properties(cell)
            
            # Generate cell attributes
            cell_attrs = []
            cell_styles = []
            
            # Handle cell spanning
            if 'gridSpan' in cell_props:
                cell_attrs.append(f'colspan="{cell_props["gridSpan"]}"')
            
            if 'vMerge' in cell_props and cell_props['vMerge'] != 'continue':
                # Note: rowspan calculation would require analyzing the entire table
                # For now, we'll just note that it's a merged cell
                pass
            
            # Handle cell alignment
            if 'textAlign' in cell_props:
                align_map = {'left': 'left', 'center': 'center', 'right': 'right'}
                alignment = align_map.get(cell_props['textAlign'], 'left')
                cell_styles.append(f'text-align: {alignment}')
            
            if 'verticalAlign' in cell_props:
                valign_map = {'top': 'top', 'center': 'middle', 'bottom': 'bottom'}
                valignment = valign_map.get(cell_props['verticalAlign'], 'top')
                cell_styles.append(f'vertical-align: {valignment}')
            
            # Handle cell borders
            if 'borders' in cell_props:
                for side, border_def in cell_props['borders'].items():
                    cell_styles.append(f'border-{side}: {border_def}')
            
            # Handle cell background
            if 'background' in cell_props:
                cell_styles.append(f'background-color: {cell_props["background"]}')
            
            # Cell padding
            cell_styles.append('padding: 8px')
            
            # Build cell tag
            if cell_styles:
                cell_attrs.append(f'style="{"; ".join(cell_styles)}"')
            
            cell_tag = f'<td {" ".join(cell_attrs)}>' if cell_attrs else '<td>'
            
            # Process cell content
            cell_content = []
            for paragraph in self._robust_find(cell, './/w:p'):
                try:
                    p_content = self._process_paragraph(paragraph)
                    if p_content:
                        # Remove paragraph tags for table cells but preserve inner formatting
                        p_content = re.sub(r'^<p>(.*)</p>$', r'\1', p_content)
                        # Preserve heading tags in table cells
                        cell_content.append(p_content)
                except Exception as e:
                    self.warnings.append(f"Error processing cell paragraph: {str(e)}")
            
            cell_text = '<br/>'.join(cell_content) if cell_content else '&nbsp;'
            
            return f'{cell_tag}{cell_text}</td>'
            
        except Exception as e:
            self.warnings.append(f"Error processing table cell: {str(e)}")
            return '<td>&nbsp;</td>'
    
    def _parse_cell_properties(self, cell: ET.Element) -> Dict[str, Any]:
        """Parse table cell properties."""
        props = {}
        
        try:
            tc_pr = self._robust_find_one(cell, './/w:tcPr')
            if tc_pr is not None:
                # Grid span (colspan)
                grid_span = self._robust_find_one(tc_pr, './/w:gridSpan')
                if grid_span is not None:
                    span_val = self._robust_get_attribute(grid_span, 'val', 'w')
                    if span_val:
                        props['gridSpan'] = int(span_val)
                
                # Vertical merge (rowspan)
                v_merge = self._robust_find_one(tc_pr, './/w:vMerge')
                if v_merge is not None:
                    merge_val = self._robust_get_attribute(v_merge, 'val', 'w')
                    props['vMerge'] = merge_val or 'continue'
                
                # Text alignment
                tc_w = self._robust_find_one(tc_pr, './/w:tcW')
                if tc_w is not None:
                    # Cell width - could be used for styling
                    pass
                
                # Vertical alignment
                v_align = self._robust_find_one(tc_pr, './/w:vAlign')
                if v_align is not None:
                    props['verticalAlign'] = self._robust_get_attribute(v_align, 'val', 'w')
                
                # Cell borders
                borders = self._robust_find_one(tc_pr, './/w:tcBorders')
                if borders is not None:
                    props['borders'] = self._parse_table_borders(borders)
                
                # Cell shading/background
                shd = self._robust_find_one(tc_pr, './/w:shd')
                if shd is not None:
                    fill_color = self._robust_get_attribute(shd, 'fill', 'w')
                    if fill_color and fill_color != 'auto':
                        props['background'] = f'#{fill_color}'
        
        except Exception as e:
            self.warnings.append(f"Error parsing cell properties: {str(e)}")
        
        return props
    
    def _detect_heading_level(self, paragraph: ET.Element, style_id: Optional[str] = None) -> Optional[int]:
        """Enhanced heading detection with error handling."""
        try:
            pPr = self._robust_find_one(paragraph, './/w:pPr')
            if pPr is None:
                return None
            
            # Method 1: Check outline level
            outlineLvl = self._robust_find_one(pPr, './/w:outlineLvl')
            if outlineLvl is not None:
                try:
                    outline_level = int(self._robust_get_attribute(outlineLvl, 'val', 'w') or '0')
                    if 0 <= outline_level <= 5:
                        return outline_level + 1
                except (ValueError, TypeError):
                    pass
            
            # Method 2: Style name matching
            if style_id:
                heading_level = self._detect_heading_from_style_name(style_id)
                if heading_level:
                    return heading_level
            
            # Method 3: Style properties
            if style_id and style_id in self.styles:
                style_props = self.styles[style_id]
                if style_props.get('type') == 'paragraph':
                    if style_props.get('bold') and style_props.get('font_size', 0) >= 14:
                        font_size = style_props.get('font_size', 12)
                        if font_size >= 20:
                            return 1
                        elif font_size >= 18:
                            return 2
                        elif font_size >= 16:
                            return 3
                        elif font_size >= 14:
                            return 4
            
            # Method 4: Direct formatting
            first_run = self._robust_find_one(paragraph, './/w:r')
            if first_run is not None:
                rPr = self._robust_find_one(first_run, './/w:rPr')
                if rPr is not None:
                    is_bold = self._robust_find_one(rPr, './/w:b') is not None
                    sz = self._robust_find_one(rPr, './/w:sz')
                    if sz is not None and is_bold:
                        try:
                            font_size = int(self._robust_get_attribute(sz, 'val', 'w') or '24') / 2
                            if font_size >= 18:
                                return 1
                            elif font_size >= 16:
                                return 2
                            elif font_size >= 14:
                                return 3
                        except (ValueError, TypeError):
                            pass
            
            return None
        except Exception as e:
            self.warnings.append(f"Error detecting heading level: {str(e)}")
            return None
    
    def _detect_heading_from_style_name(self, style_id: str) -> Optional[int]:
        """Detect heading level from style name with error handling."""
        try:
            if not style_id:
                return None
            
            style_lower = style_id.lower().replace(' ', '').replace('_', '').replace('-', '')
            
            heading_patterns = [
                (r'heading1|title1?$|h1', 1),
                (r'heading2|subtitle|h2', 2), 
                (r'heading3|h3', 3),
                (r'heading4|h4', 4),
                (r'heading5|h5', 5),
                (r'heading6|h6', 6),
                (r'heading(\d)', lambda m: min(int(m.group(1)), 6)),
                (r'titre(\d)', lambda m: min(int(m.group(1)), 6)),
                (r'überschrift(\d)', lambda m: min(int(m.group(1)), 6)),
                (r'encabezado(\d)', lambda m: min(int(m.group(1)), 6)),
                (r'intestazione(\d)', lambda m: min(int(m.group(1)), 6)),
                (r'(title|titre|titel|titulo|titolo)$', 1),
                (r'(subtitle|soustitre|untertitel|subtitulo|sottotitolo)', 2),
                (r'(chapter|chapitre|kapitel|capitulo|capitolo)', 1),
                (r'(section|abschnitt|seccion|sezione)', 2),
                (r'(subsection|unterabschnitt|subseccion|sottosezione)', 3),
                (r'toc(\d)', lambda m: min(int(m.group(1)), 6)),
                (r'outline(\d)', lambda m: min(int(m.group(1)), 6)),
            ]
            
            for pattern, level in heading_patterns:
                if callable(level):
                    match = re.search(pattern, style_lower)
                    if match:
                        return level(match)
                else:
                    if re.search(pattern, style_lower):
                        return level
            
            return None
        except Exception as e:
            self.warnings.append(f"Error in heading style detection: {str(e)}")
            return None
    
    def _close_all_lists(self) -> str:
        """Close all remaining open list elements."""
        html_parts = []
        while self.list_stack:
            list_info = self.list_stack.pop()
            html_parts.append(f"</{list_info['tag']}>")
        self.current_list_ids.clear()
        return '\n'.join(html_parts)
    
    def _manage_list_structure(self, num_id: str, ilvl: int) -> str:
        """Manage nested list structure with error handling."""
        try:
            html_parts = []
            
            # Determine list type
            list_type = 'ul'  # default
            if num_id in self.numbering and str(ilvl) in self.numbering[num_id]:
                num_fmt = self.numbering[num_id][str(ilvl)].get('format', 'bullet')
                if num_fmt in ['decimal', 'lowerRoman', 'upperRoman', 'lowerLetter', 'upperLetter']:
                    list_type = 'ol'
            
            # Close lists if we're at a higher level
            while len(self.list_stack) > ilvl + 1:
                list_info = self.list_stack.pop()
                html_parts.append(f"</{list_info['tag']}>")
            
            # Open new lists if needed
            while len(self.list_stack) <= ilvl:
                current_level = len(self.list_stack)
                
                if (current_level < len(self.list_stack) and 
                    self.list_stack[current_level]['tag'] != list_type):
                    list_info = self.list_stack.pop()
                    html_parts.append(f"</{list_info['tag']}>")
                
                html_parts.append(f"<{list_type}>")
                self.list_stack.append({
                    'tag': list_type,
                    'level': current_level,
                    'num_id': num_id
                })
            
            return '\n'.join(html_parts)
        except Exception as e:
            self.warnings.append(f"Error managing list structure: {str(e)}")
            return ''
    
    def _process_paragraph(self, paragraph: ET.Element) -> str:
        """Enhanced paragraph processing with font support and error handling."""
        try:
            # Check for paragraph properties
            pPr = self._robust_find_one(paragraph, './/w:pPr')
            style_id = None
            is_list_item = False
            list_level = 0
            num_id = None
            paragraph_color = None
            paragraph_highlight = None
            paragraph_font = None
            
            if pPr is not None:
                # Check for style
                pStyle = self._robust_find_one(pPr, './/w:pStyle')
                if pStyle is not None:
                    style_id = self._robust_get_attribute(pStyle, 'val', 'w')
                    
                    # Get properties from paragraph style
                    if style_id and style_id in self.styles:
                        style_props = self.styles[style_id]
                        paragraph_color = style_props.get('color')
                        paragraph_highlight = style_props.get('highlight')
                        paragraph_font = style_props.get('font_family')
                
                # Check for direct paragraph-level properties
                pPr_rPr = self._robust_find_one(pPr, './/w:rPr')
                if pPr_rPr is not None:
                    direct_color = self._extract_text_color(pPr_rPr)
                    direct_highlight = self._extract_highlight_color(pPr_rPr)
                    direct_font = self._extract_font_info(pPr_rPr)
                    
                    if direct_color:
                        paragraph_color = direct_color
                    if direct_highlight:
                        paragraph_highlight = direct_highlight
                    if direct_font:
                        paragraph_font = direct_font
                
                # Check for numbering (lists)
                numPr = self._robust_find_one(pPr, './/w:numPr')
                if numPr is not None:
                    is_list_item = True
                    ilvl_elem = self._robust_find_one(numPr, './/w:ilvl')
                    numId_elem = self._robust_find_one(numPr, './/w:numId')
                    
                    if ilvl_elem is not None:
                        list_level = int(self._robust_get_attribute(ilvl_elem, 'val', 'w') or '0')
                    if numId_elem is not None:
                        num_id = self._robust_get_attribute(numId_elem, 'val', 'w')
            
            # Process runs with enhanced font support
            content_parts = []
            for element in paragraph:
                try:
                    element_local_name = element.tag.split('}')[-1] if '}' in element.tag else element.tag
                    if element_local_name == 'r':  # Regular run
                        run_content = self._process_run_enhanced(element, paragraph_color, paragraph_highlight, paragraph_font)
                        if run_content:
                            content_parts.append(run_content)
                    elif element_local_name == 'hyperlink':  # Hyperlink element
                        hyperlink_content = self._process_hyperlink_enhanced(element, paragraph_color, paragraph_highlight, paragraph_font)
                        if hyperlink_content:
                            content_parts.append(hyperlink_content)
                except Exception as e:
                    self.warnings.append(f"Error processing paragraph element: {str(e)}")
            
            content = ''.join(content_parts).strip()
            
            if not content:
                if self.list_stack and not is_list_item:
                    return self._close_all_lists() + '\n<p>&nbsp;</p>'
                return '<p>&nbsp;</p>'
            
            # Enhanced heading detection
            heading_level = self._detect_heading_level(paragraph, style_id)
            if heading_level and 1 <= heading_level <= 6:
                list_closure = self._close_all_lists() if self.list_stack else ''
                return (list_closure + '\n' if list_closure else '') + f'<h{heading_level}>{content}</h{heading_level}>'
            
            # Check for quote/citation styles
            if style_id:
                style_lower = style_id.lower()
                if any(keyword in style_lower for keyword in ['quote', 'citation', 'blockquote', 'extract']):
                    list_closure = self._close_all_lists() if self.list_stack else ''
                    return (list_closure + '\n' if list_closure else '') + f'<blockquote>{content}</blockquote>'
            
            # Handle list items
            if is_list_item and num_id:
                list_structure = self._manage_list_structure(num_id, list_level)
                list_item = f'<li>{content}</li>'
                return (list_structure + '\n' if list_structure else '') + list_item
            
            # Regular paragraph
            if self.list_stack:
                list_closure = self._close_all_lists()
                return list_closure + f'\n<p>{content}</p>'
            
            return f'<p>{content}</p>'
            
        except Exception as e:
            self.warnings.append(f"Error processing paragraph: {str(e)}")
            return '<p>[Paragraph conversion error]</p>'
    
    def _process_hyperlink_enhanced(self, hyperlink: ET.Element, paragraph_color: Optional[str] = None, 
                                   paragraph_highlight: Optional[str] = None, paragraph_font: Optional[Dict] = None) -> str:
        """Enhanced hyperlink processing with font support."""
        try:
            # Get hyperlink relationship ID
            r_id = self._robust_get_attribute(hyperlink, 'id', 'r')
            anchor = self._robust_get_attribute(hyperlink, 'anchor', 'w')
            
            # Determine link target
            href = None
            if r_id and r_id in self.relationships:
                relationship = self.relationships[r_id]
                if relationship['type'].endswith('hyperlink'):
                    href = relationship['target']
            elif anchor:
                href = f"#{anchor}"
            
            # Process hyperlink content
            content_parts = []
            for run in self._robust_find(hyperlink, './/w:r'):
                run_content = self._process_run_enhanced(run, paragraph_color, paragraph_highlight, paragraph_font)
                if run_content:
                    content_parts.append(run_content)
            
            content = ''.join(content_parts)
            
            if not content:
                return ''
            
            # Create HTML anchor tag
            if href:
                if 'color:' not in content and 'style=' not in content:
                    hyperlink_color = self.theme_colors.get('hyperlink', '0563C1')
                    content = f'<span style="color: #{hyperlink_color};">{content}</span>'
                return f'<a href="{href}">{content}</a>'
            else:
                return content
                
        except Exception as e:
            self.warnings.append(f"Error processing hyperlink: {str(e)}")
            return '[Hyperlink error]'
    
    def _process_run_enhanced(self, run: ET.Element, paragraph_color: Optional[str] = None, 
                             paragraph_highlight: Optional[str] = None, paragraph_font: Optional[Dict] = None) -> str:
        """Enhanced run processing with comprehensive font and formatting support."""
        try:
            # Get run properties
            rPr = self._robust_find_one(run, './/w:rPr')
            
            # Extract formatting
            is_bold = False
            is_italic = False
            is_underline = False
            is_strikethrough = False
            text_color = None
            highlight_color = None
            font_info = None
            font_size = None
            
            if rPr is not None:
                is_bold = self._robust_find_one(rPr, './/w:b') is not None
                is_italic = self._robust_find_one(rPr, './/w:i') is not None
                is_underline = self._robust_find_one(rPr, './/w:u') is not None
                is_strikethrough = self._robust_find_one(rPr, './/w:strike') is not None
                
                # Enhanced color processing
                text_color = self._extract_text_color(rPr)
                highlight_color = self._extract_highlight_color(rPr)
                
                # Extract font information
                font_info = self._extract_font_info(rPr)
                font_size = self._extract_font_size(rPr)
                
                # Check for character style inheritance
                rStyle = self._robust_find_one(rPr, './/w:rStyle')
                if rStyle is not None:
                    style_id = self._robust_get_attribute(rStyle, 'val', 'w')
                    if style_id and style_id in self.styles:
                        style_props = self.styles[style_id]
                        if not text_color and 'color' in style_props:
                            text_color = style_props['color']
                        if not highlight_color and 'highlight' in style_props:
                            highlight_color = style_props['highlight']
                        if not font_info and 'font_family' in style_props:
                            font_info = style_props['font_family']
                        if not font_size and 'font_size' in style_props:
                            font_size = style_props['font_size']
            
            # Use paragraph-level properties as fallback
            if not text_color and paragraph_color:
                text_color = paragraph_color
            if not highlight_color and paragraph_highlight:
                highlight_color = paragraph_highlight
            if not font_info and paragraph_font:
                font_info = paragraph_font
            
            # Extract text content and other elements
            content_parts = []
            
            # Handle text elements
            for text_elem in self._robust_find(run, './/w:t'):
                if text_elem.text:
                    content_parts.append(text_elem.text)
            
            # Handle line breaks
            for br in self._robust_find(run, './/w:br'):
                content_parts.append('<br/>')
            
            # Handle tabs
            for tab in self._robust_find(run, './/w:tab'):
                content_parts.append('&nbsp;&nbsp;&nbsp;&nbsp;')
            
            # Handle images (drawings)
            for drawing in self._robust_find(run, './/w:drawing'):
                image_html = self._process_drawing(drawing)
                if image_html:
                    content_parts.append(image_html)
            
            # Handle embedded objects
            for obj in self._robust_find(run, './/w:object'):
                image_html = self._process_object(obj)
                if image_html:
                    content_parts.append(image_html)
            
            content = ''.join(content_parts)
            
            if not content:
                return ''
            
            # Apply formatting (skip for images)
            if not content.startswith('<img'):
                if is_bold:
                    content = f'<strong>{content}</strong>'
                if is_italic:
                    content = f'<em>{content}</em>'
                if is_underline:
                    content = f'<u>{content}</u>'
                if is_strikethrough:
                    content = f'<s>{content}</s>'
                
                # Apply comprehensive styling
                style_parts = []
                if text_color:
                    style_parts.append(f'color: #{text_color}')
                if highlight_color:
                    style_parts.append(f'background-color: #{highlight_color}')
                if font_info and 'css_family' in font_info:
                    style_parts.append(f'font-family: {font_info["css_family"]}')
                if font_size:
                    style_parts.append(f'font-size: {font_size}pt')
                
                if style_parts:
                    style_attr = '; '.join(style_parts)
                    content = f'<span style=\'{style_attr}\'>{content}</span>'
            
            return content
            
        except Exception as e:
            self.warnings.append(f"Error processing run: {str(e)}")
            return '[Run error]'
    
    def _extract_font_info(self, rPr: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract font information from run properties."""
        try:
            font_elem = self._robust_find_one(rPr, './/w:rFonts')
            if font_elem is not None:
                # Get font name (prefer ascii, then eastAsia, then default)
                font_name = (self._robust_get_attribute(font_elem, 'ascii', 'w') or
                            self._robust_get_attribute(font_elem, 'eastAsia', 'w') or
                            self._robust_get_attribute(font_elem, 'hAnsi', 'w'))
                
                if font_name:
                    # Look up font in our font table
                    if font_name in self.fonts:
                        return self.fonts[font_name]
                    else:
                        # Create basic font info
                        css_family = self._map_font_to_css(font_name)
                        return {
                            'name': font_name,
                            'css_family': css_family
                        }
            
            return None
        except Exception as e:
            self.warnings.append(f"Error extracting font info: {str(e)}")
            return None
    
    def _extract_font_size(self, rPr: ET.Element) -> Optional[float]:
        """Extract font size from run properties."""
        try:
            sz = self._robust_find_one(rPr, './/w:sz')
            if sz is not None:
                size_val = self._robust_get_attribute(sz, 'val', 'w')
                if size_val:
                    # Font size in half-points, convert to points
                    return float(size_val) / 2
            return None
        except Exception as e:
            self.warnings.append(f"Error extracting font size: {str(e)}")
            return None
    
    def _process_drawing(self, drawing: ET.Element) -> str:
        """Enhanced drawing processing with error handling."""
        try:
            blip_elements = self._robust_find(drawing, './/a:blip')
            
            for blip in blip_elements:
                r_embed = self._robust_get_attribute(blip, 'embed', 'r')
                if r_embed and r_embed in self.relationships:
                    image_path = self.relationships[r_embed]['target']
                    image_filename = image_path.split('/')[-1]
                    
                    if image_filename in self.images:
                        # Get image dimensions
                        width = None
                        height = None
                        
                        extent = self._robust_find_one(drawing, './/wp:extent')
                        if extent is not None:
                            cx = self._robust_get_attribute(extent, 'cx')
                            cy = self._robust_get_attribute(extent, 'cy')
                            if cx:
                                width = int(int(cx) / 914400 * 96)
                            if cy:
                                height = int(int(cy) / 914400 * 96)
                        
                        # Create image tag
                        img_attrs = [f'src="{self.images[image_filename]}"', 'alt="Image"']
                        if width:
                            img_attrs.append(f'width="{width}"')
                        if height:
                            img_attrs.append(f'height="{height}"')
                        
                        return f'<img {" ".join(img_attrs)} />'
        
        except Exception as e:
            self.warnings.append(f"Could not process drawing: {str(e)}")
        
        return ''
    
    def _process_object(self, obj: ET.Element) -> str:
        """Enhanced object processing with error handling."""
        try:
            shape_elements = self._robust_find(obj, './/v:shape')
            
            for shape in shape_elements:
                imagedata = self._robust_find_one(shape, './/v:imagedata')
                if imagedata is not None:
                    r_id = self._robust_get_attribute(imagedata, 'id', 'r')
                    if r_id and r_id in self.relationships:
                        image_path = self.relationships[r_id]['target']
                        image_filename = image_path.split('/')[-1]
                        
                        if image_filename in self.images:
                            return f'<img src="{self.images[image_filename]}" alt="Embedded Image" />'
        
        except Exception as e:
            self.warnings.append(f"Could not process object: {str(e)}")
        
        return ''
    
    def _extract_text_color(self, rPr: ET.Element) -> Optional[str]:
        """Enhanced text color extraction with validation."""
        try:
            color_elem = self._robust_find_one(rPr, './/w:color')
            if color_elem is None:
                return None
            
            # Direct color value
            color_val = self._robust_get_attribute(color_elem, 'val', 'w')
            if color_val and color_val.lower() != 'auto':
                if self._is_valid_hex_color(color_val):
                    return color_val.upper()
            
            # Theme color reference
            theme_color = self._robust_get_attribute(color_elem, 'themeColor', 'w')
            if theme_color:
                base_color = self.theme_colors.get(theme_color)
                if base_color:
                    theme_tint = self._robust_get_attribute(color_elem, 'themeTint', 'w')
                    theme_shade = self._robust_get_attribute(color_elem, 'themeShade', 'w')
                    
                    if theme_tint:
                        return self._apply_tint(base_color, theme_tint)
                    elif theme_shade:
                        return self._apply_shade(base_color, theme_shade)
                    else:
                        return base_color
            
            # Legacy color names
            if color_val and color_val.lower() in ['black', 'blue', 'cyan', 'green', 'magenta', 'red', 'yellow', 'white']:
                color_map = {
                    'black': '000000', 'blue': '0000FF', 'cyan': '00FFFF', 'green': '008000',
                    'magenta': 'FF00FF', 'red': 'FF0000', 'yellow': 'FFFF00', 'white': 'FFFFFF'
                }
                return color_map.get(color_val.lower())
            
            return None
        except Exception as e:
            self.warnings.append(f"Error extracting text color: {str(e)}")
            return None
    
    def _extract_highlight_color(self, rPr: ET.Element) -> Optional[str]:
        """Enhanced highlight color extraction with validation."""
        try:
            highlight_elem = self._robust_find_one(rPr, './/w:highlight')
            if highlight_elem is not None:
                highlight_val = self._robust_get_attribute(highlight_elem, 'val', 'w')
                if highlight_val and highlight_val.lower() != 'none':
                    highlight_map = {
                        'yellow': 'FFFF00', 'green': '00FF00', 'cyan': '00FFFF', 'magenta': 'FF00FF',
                        'blue': '0000FF', 'red': 'FF0000', 'darkBlue': '000080', 'darkCyan': '008080',
                        'darkGreen': '008000', 'darkMagenta': '800080', 'darkRed': '800000', 'darkYellow': '808000',
                        'darkGray': '808080', 'lightGray': 'C0C0C0', 'black': '000000', 'white': 'FFFFFF'
                    }
                    mapped_color = highlight_map.get(highlight_val.lower())
                    if mapped_color:
                        return mapped_color
                    elif self._is_valid_hex_color(highlight_val):
                        return highlight_val.upper()
            
            # Check for shading
            shd_elem = self._robust_find_one(rPr, './/w:shd')
            if shd_elem is not None:
                fill_color = self._robust_get_attribute(shd_elem, 'fill', 'w')
                if fill_color and fill_color.lower() != 'auto':
                    if self._is_valid_hex_color(fill_color):
                        return fill_color.upper()
            
            return None
        except Exception as e:
            self.warnings.append(f"Error extracting highlight color: {str(e)}")
            return None
    
    def _apply_tint(self, base_color: str, tint_val: str) -> str:
        """Apply tint with error handling."""
        try:
            tint = int(tint_val, 16) / 255.0 if len(tint_val) <= 2 else int(tint_val, 16) / 65535.0
            
            base_color = base_color.upper()
            r = int(base_color[0:2], 16)
            g = int(base_color[2:4], 16)
            b = int(base_color[4:6], 16)
            
            r = int(r + (255 - r) * tint)
            g = int(g + (255 - g) * tint)
            b = int(b + (255 - b) * tint)
            
            return f'{r:02X}{g:02X}{b:02X}'
        except Exception:
            return base_color
    
    def _apply_shade(self, base_color: str, shade_val: str) -> str:
        """Apply shade with error handling."""
        try:
            shade = int(shade_val, 16) / 255.0 if len(shade_val) <= 2 else int(shade_val, 16) / 65535.0
            
            base_color = base_color.upper()
            r = int(base_color[0:2], 16)
            g = int(base_color[2:4], 16)
            b = int(base_color[4:6], 16)
            
            r = int(r * (1 - shade))
            g = int(g * (1 - shade))
            b = int(b * (1 - shade))
            
            return f'{r:02X}{g:02X}{b:02X}'
        except Exception:
            return base_color
    
    def _parse_style_properties(self, style_element: ET.Element) -> Dict[str, Any]:
        """Enhanced style properties parsing with font support."""
        properties = {}
        
        try:
            # Parse run properties (character formatting)
            rPr = self._robust_find_one(style_element, './/w:rPr')
            if rPr is not None:
                properties['bold'] = self._robust_find_one(rPr, './/w:b') is not None
                properties['italic'] = self._robust_find_one(rPr, './/w:i') is not None
                
                # Extract font size
                sz = self._robust_find_one(rPr, './/w:sz')
                if sz is not None:
                    try:
                        font_size = int(self._robust_get_attribute(sz, 'val', 'w') or '24') / 2
                        properties['font_size'] = font_size
                    except (ValueError, TypeError):
                        pass
                
                # Extract color information
                text_color = self._extract_text_color(rPr)
                if text_color:
                    properties['color'] = text_color
                    
                highlight_color = self._extract_highlight_color(rPr)  
                if highlight_color:
                    properties['highlight'] = highlight_color
                
                # Extract font information
                font_info = self._extract_font_info(rPr)
                if font_info:
                    properties['font_family'] = font_info
        
        except Exception as e:
            self.warnings.append(f"Error parsing style properties: {str(e)}")
        
        return properties
    
    def _parse_numbering_properties(self, abstract_num: ET.Element) -> Dict[str, Any]:
        """Enhanced numbering properties parsing with error handling."""
        properties = {}
        
        try:
            for lvl in self._robust_find(abstract_num, './/w:lvl'):
                ilvl = self._robust_get_attribute(lvl, 'ilvl', 'w')
                if ilvl:
                    numFmt = self._robust_find_one(lvl, './/w:numFmt')
                    fmt_val = 'bullet'
                    if numFmt is not None:
                        fmt_val = self._robust_get_attribute(numFmt, 'val', 'w') or 'bullet'
                    
                    lvlText = self._robust_find_one(lvl, './/w:lvlText')
                    level_text = ''
                    if lvlText is not None:
                        level_text = self._robust_get_attribute(lvlText, 'val', 'w') or ''
                    
                    properties[ilvl] = {
                        'format': fmt_val,
                        'levelText': level_text
                    }
        except Exception as e:
            self.warnings.append(f"Error parsing numbering properties: {str(e)}")
        
        return properties
    
    def _wrap_html(self, content: str) -> str:
        """Enhanced HTML wrapper with better styling."""
        error_summary = ""
        if self.errors or self.warnings:
            error_summary = f"<!-- Conversion Summary: {len(self.errors)} errors, {len(self.warnings)} warnings -->\n"
        
        return f"""{error_summary}<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Converted Document</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            margin: 40px;
            max-width: 900px;
        }}
        table {{
            width: 100%;
            margin: 10px 0;
            border-collapse: collapse;
        }}
        td, th {{
            padding: 8px;
            vertical-align: top;
            border: 1px solid #ddd;
        }}
        blockquote {{
            margin: 20px 0;
            padding: 10px 20px;
            border-left: 4px solid #ccc;
            background-color: #f9f9f9;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 20px;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        h1 {{ font-size: 24pt; }}
        h2 {{ font-size: 18pt; }}
        h3 {{ font-size: 14pt; }}
        h4 {{ font-size: 12pt; }}
        h5 {{ font-size: 10pt; }}
        h6 {{ font-size: 9pt; }}
        ul, ol {{
            margin: 10px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 5px 0;
        }}
        a {{
            text-decoration: underline;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 10px 0;
        }}
        /* Enhanced table styling */
        table.enhanced {{
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .error-message {{
            background-color: #ffe6e6;
            border: 1px solid #ff9999;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            color: #cc0000;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""

    def get_conversion_summary(self) -> Dict[str, Any]:
        """Get summary of conversion process including errors and warnings."""
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'images_extracted': len(self.images),
            'fonts_found': len(self.fonts),
            'styles_parsed': len(self.styles),
            'relationships_found': len(self.relationships),
            'discovered_namespaces': self.discovered_namespaces
        }


def convert_docx_to_html(docx_bytes: bytes, debug: bool = False) -> str:
    converter = DocxToHtmlConverter(debug=debug)
    return converter.convert_docx_to_html(docx_bytes)


def convert_docx_file_to_html(input_path: str, output_path: Optional[str] = None, debug: bool = False) -> Tuple[str, Dict[str, Any]]:
    try:
        with open(input_path, 'rb') as f:
            docx_bytes = f.read()
    except IOError as e:
        raise ConversionError(f"Cannot read input file {input_path}: {str(e)}")
    
    converter = DocxToHtmlConverter(debug=debug)
    html_content = converter.convert_docx_to_html(docx_bytes)
    
    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"HTML saved to: {output_path}")
        except IOError as e:
            raise ConversionError(f"Cannot write output file {output_path}: {str(e)}")
    
    return html_content, converter.get_conversion_summary()

from custom_types.DOCX.type import DOCX
from custom_types.HTML.type import HTML

class Pipeline:
    def __init__(self):
        pass        
    def __call__(self, docx: DOCX) -> HTML:
        converter = DocxToHtmlConverter(debug=False)
        html_content = converter.convert_docx_to_html(docx.file_as_bytes)
        return HTML(html=html_content)