from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict
import logging
import time

# Import Pydantic models
from models.wikipedia_models import ProcessedPageData, ProcessingConfig, ProcessingSummary

logger = logging.getLogger(__name__)

class TextProcessor:
    """Text processor with Pydantic validation for Wikipedia content"""
    
    def __init__(self, config: ProcessingConfig = None):
        self.config = config or ProcessingConfig()
        
    def clean_html_content(self, html_content: str) -> str:
        """Clean HTML content and extract meaningful text"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements based on config
            for element_selector in self.config.remove_elements:
                for element in soup.select(element_selector):
                    element.decompose()
            
            # Extract text content
            text_content = soup.get_text()
            
            # Clean up text - minimal processing
            if self.config.preserve_structure:
                # Preserve some structure (paragraphs, etc.)
                text_content = re.sub(r'\n{3,}', '\n\n', text_content)
            else:
                # Minimal cleanup
                text_content = re.sub(r'\n+', '\n', text_content)
                
            text_content = re.sub(r'\s+', ' ', text_content)
            text_content = text_content.strip()
            
            return text_content
            
        except Exception as e:
            logger.error(f"Error cleaning HTML content: {str(e)}")
            raise
    
    def process_single_page(self, page_data: Dict) -> ProcessedPageData:
        """Process a single page with Pydantic validation"""
        try:
            # Clean HTML content
            clean_text = self.clean_html_content(page_data['html_content'])
            
            # Check minimum length requirement
            if len(clean_text) < self.config.min_text_length:
                logger.warning(f"Text too short for {page_data['title']}: {len(clean_text)} chars")
            
            # Create validated processed page using Pydantic
            processed_page = ProcessedPageData(
                source_type=page_data['source_type'],
                source_id=page_data['source_id'],
                page_title=page_data['title'],
                page_id=page_data['page_id'],
                revision_id=page_data['revision_id'],
                clean_text=clean_text,
                text_length=len(clean_text),
                source_url=page_data['source_url'],
                metadata={
                    'extracted_at': page_data['extracted_at'],
                    'original_html_length': len(page_data['html_content']),
                    'processing_config': self.config.model_dump(),
                    'text_reduction_ratio': 1 - (len(clean_text) / len(page_data['html_content']))
                }
            )
            
            return processed_page
            
        except Exception as e:
            logger.error(f"Error processing page {page_data.get('title', 'Unknown')}: {str(e)}")
            raise
    
    def process_multiple_pages(self, extracted_pages: List[Dict]) -> List[ProcessedPageData]:
        """Process multiple pages with validation and error handling"""
        processed_pages = []
        failed_pages = []
        start_time = time.time()
        
        for page_data in extracted_pages:
            try:
                logger.info(f"Processing: {page_data['title']}")
                processed_page = self.process_single_page(page_data)
                processed_pages.append(processed_page)
                logger.info(f"✓ Processed {page_data['title']} - {len(processed_page.clean_text)} characters")
                
            except Exception as e:
                failed_pages.append({
                    'title': page_data.get('title', 'Unknown'),
                    'error': str(e)
                })
                logger.error(f"✗ Failed to process {page_data.get('title', 'Unknown')}: {str(e)}")
                continue
        
        processing_time = time.time() - start_time
        
        # Log summary
        logger.info(f"Processing complete: {len(processed_pages)} successful, {len(failed_pages)} failed")
        logger.info(f"Total processing time: {processing_time:.2f} seconds")
        
        return processed_pages
    
    def get_processed_as_dict(self, extracted_pages: List[Dict]) -> List[Dict]:
        """Process pages and return as dictionaries for Airflow compatibility"""
        processed_pages = self.process_multiple_pages(extracted_pages)
        return [page.model_dump() for page in processed_pages]
    
    def get_processing_summary(self, extracted_pages: List[Dict]) -> ProcessingSummary:
        """Generate processing summary with validation"""
        start_time = time.time()
        processed_pages = self.process_multiple_pages(extracted_pages)
        processing_time = time.time() - start_time
        
        total_pages = len(extracted_pages)
        successful_pages = len(processed_pages)
        failed_pages = total_pages - successful_pages
        total_chars = sum(len(page.clean_text) for page in processed_pages)
        avg_length = total_chars / successful_pages if successful_pages > 0 else 0.0
        
        summary = ProcessingSummary(
            total_pages_processed=total_pages,
            successful_pages=successful_pages,
            failed_pages=failed_pages,
            total_characters_processed=total_chars,
            average_text_length=avg_length,
            processing_time_seconds=processing_time
        )
        
        return summary
    
    def update_config(self, new_config: Dict) -> None:
        """Update processing configuration with validation"""
        try:
            self.config = ProcessingConfig(**new_config)
            logger.info("Processing configuration updated successfully")
        except Exception as e:
            logger.error(f"Failed to update config: {str(e)}")
            raise
