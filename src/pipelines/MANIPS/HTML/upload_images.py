from bs4 import BeautifulSoup
import base64
import re
from datetime import datetime
from pipelines.CONNECTORS.DEEPDOCS.file_easy_upload import Pipeline as UploadPipeline
from custom_types.HTML.type import HTML

class Pipeline:
    def __init__(self, upload_directory: str = '/Uploads/'):
        """
        Initialize the pipeline with upload settings.
        
        Args:
            upload_directory: Directory where images will be uploaded
        """
        self.upload_pipeline = UploadPipeline(directory=upload_directory)
    
    def _extract_base64_data(self, src_value):
        """
        Extract base64 data and file extension from data URI.
        
        Args:
            src_value: The src attribute value (e.g., "data:image/png;base64,...")
            
        Returns:
            tuple: (decoded_bytes, file_extension) or (None, None) if not base64
        """
        # Check if it's a data URI with base64
        data_uri_pattern = r'^data:image/(\w+);base64,(.+)$'
        match = re.match(data_uri_pattern, src_value)
        
        if not match:
            return None, None
            
        file_extension = match.group(1)
        base64_data = match.group(2)
        
        try:
            decoded_bytes = base64.b64decode(base64_data)
            return decoded_bytes, file_extension
        except Exception as e:
            print(f"Error decoding base64 data: {e}")
            return None, None
    
    def _generate_filename(self, index, file_extension):
        """
        Generate a unique filename for the uploaded image.
        
        Args:
            index: Index of the image in the document
            file_extension: File extension (png, jpg, gif, etc.)
            
        Returns:
            str: Generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"image_{timestamp}_{index}.{file_extension}"
    
    def __call__(self, html: HTML) -> HTML:
        """
        Process HTML to upload base64 images and replace with URLs.
        
        Args:
            html: HTML object containing the HTML string
            
        Returns:
            HTML: Modified HTML with uploaded image URLs
        """
        soup = BeautifulSoup(html.html, 'html.parser')
        
        # Find all img tags with base64 data
        img_tags = soup.find_all('img')
        base64_images = []
        
        for img_tag in img_tags:
            src = img_tag.get('src', '')
            if src.startswith('data:image/'):
                base64_images.append(img_tag)
        
        # Process each base64 image
        for index, img_tag in enumerate(base64_images):
            src_value = img_tag.get('src', '')
            
            # Extract base64 data
            decoded_bytes, file_extension = self._extract_base64_data(src_value)
            
            if decoded_bytes is None:
                print(f"Skipping image {index}: Could not decode base64 data")
                # Remove the image if decoding fails - no hard-coded images should remain
                img_tag.decompose()
                continue
            
            try:
                # Generate filename
                filename = self._generate_filename(index, file_extension)
                
                # Upload the image
                url2 = self.upload_pipeline(decoded_bytes, filename)
                
                # Replace the src attribute with the uploaded URL
                img_tag['src'] = url2.url
                
                # Keep all other attributes (including alt) intact
                print(f"Successfully uploaded and replaced image {index}: {filename}")
                
            except Exception as e:
                print(f"Error processing image {index}: {e}")
                # Remove the image if upload fails - no hard-coded images should remain
                img_tag.decompose()
                continue
        
        return HTML(html=str(soup))