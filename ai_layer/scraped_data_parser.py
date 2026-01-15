"""
Scraped Data Parser - Main orchestration component.

This module provides the main ScrapedDataParser class that coordinates
all components to transform scraped data into structured JSON responses
based on user requirements.
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from ai_layer.deepseek_client import DeepSeekClient
from ai_layer.data_extractor import DataExtractor
from ai_layer.parsing_prompt_builder import ParsingPromptBuilder
from ai_layer.parsing_validator import ParsingValidator
from ai_layer.parsing_models import (
    ParsedDataResponse,
    ParsingMetadata,
    EmptyDataError,
    ParsingError,
    DataExtractionError
)


class ScrapedDataParser:
    """Orchestrates the transformation of scraped data into structured JSON."""
    
    # Configuration
    MAX_PARSING_RETRIES = 2
    DEFAULT_TEMPERATURE = 0.3  # Lower for more consistent parsing
    DEFAULT_MAX_TOKENS = 8000  # Increased for large datasets
    
    def __init__(self, deepseek_client: DeepSeekClient):
        """
        Initialize the Scraped Data Parser.
        
        Args:
            deepseek_client: Configured DeepSeek API client
        """
        self.client = deepseek_client
        self.extractor = DataExtractor()
        self.prompt_builder = ParsingPromptBuilder()
        self.validator = ParsingValidator()
    
    def parse_scraped_data(
        self,
        scraping_result: Any,
        user_requirements: Dict[str, Any],
        model: str = "deepseek-chat",
        temperature: float = None,
        max_tokens: int = None
    ) -> ParsedDataResponse:
        """
        Parse scraped data into structured JSON based on user requirements.
        
        Args:
            scraping_result: Result from scraping layer (ScrapingResult or dict)
            user_requirements: Dictionary containing:
                - data_description: str (required)
                - data_source: str (optional)
                - desired_fields: str (optional, newline-separated)
                - response_structure: str (optional, JSON string)
                - update_frequency: str (required)
            model: DeepSeek model to use (default: "deepseek-chat")
            temperature: Sampling temperature (default: 0.3)
            max_tokens: Maximum tokens in response (default: 8000)
            
        Returns:
            ParsedDataResponse with structured JSON and metadata
            
        Raises:
            EmptyDataError: When scraping_result contains no data
            ParsingError: When AI fails to parse the data
            DataExtractionError: When text extraction fails
        """
        if temperature is None:
            temperature = self.DEFAULT_TEMPERATURE
        if max_tokens is None:
            max_tokens = self.DEFAULT_MAX_TOKENS
        
        # Step 1: Validate scraping result is not empty
        self._validate_scraping_result(scraping_result)
        
        # Step 2: Extract text from scraped data
        try:
            scraped_text = self.extractor.extract_from_scraping_result(scraping_result)
        except (EmptyDataError, DataExtractionError):
            raise
        except Exception as e:
            raise DataExtractionError(f"Failed to extract text: {str(e)}")
        
        # Step 3: Truncate if needed
        scraped_text = self.extractor.truncate_if_needed(scraped_text)
        
        # Step 4: Build parsing prompt
        messages = self.prompt_builder.build_parsing_prompt(
            scraped_text=scraped_text,
            user_requirements=user_requirements
        )
        
        # Step 5: Call DeepSeek API with retry logic
        start_time = time.time()
        parsed_data = None
        last_error = None
        ai_output = ""
        
        for attempt in range(self.MAX_PARSING_RETRIES + 1):
            try:
                ai_output = self.client.generate_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Step 6: Validate and parse response
                parsed_data = self.validator.validate_parsed_response(
                    ai_output=ai_output,
                    user_requirements=user_requirements
                )
                break  # Success, exit retry loop
                
            except ParsingError as e:
                last_error = e
                if attempt < self.MAX_PARSING_RETRIES:
                    # Retry with slightly higher temperature
                    temperature = min(temperature + 0.1, 0.7)
                    continue
                else:
                    error_msg = self.validator.generate_error_message(ai_output, e)
                    raise ParsingError(error_msg, details=str(e))
            except Exception as e:
                # Don't retry on API errors
                raise
        
        if parsed_data is None:
            raise ParsingError(
                "Failed to parse data after multiple attempts",
                details=str(last_error) if last_error else None
            )
        
        parsing_time_ms = int((time.time() - start_time) * 1000)
        
        # Step 7: Create response with metadata
        metadata = self._create_metadata(
            scraping_result=scraping_result,
            user_requirements=user_requirements,
            parsed_data=parsed_data,
            model=model,
            ai_output=ai_output,
            parsing_time_ms=parsing_time_ms
        )
        
        # Get source metadata if available
        source_metadata = self._extract_source_metadata(scraping_result)
        
        return ParsedDataResponse(
            data=parsed_data,
            metadata=metadata,
            raw_ai_output=ai_output,
            source_metadata=source_metadata
        )
    
    def _validate_scraping_result(self, scraping_result: Any) -> None:
        """
        Validate that scraping result contains data.
        
        Args:
            scraping_result: Result to validate
            
        Raises:
            EmptyDataError: When result contains no data
        """
        # Check for success flag
        if hasattr(scraping_result, 'success') and not scraping_result.success:
            errors = getattr(scraping_result, 'errors', [])
            error_msg = "; ".join(str(e) for e in errors) if errors else "Unknown error"
            raise EmptyDataError(
                f"Scraping failed: {error_msg}. Please verify the data source URL."
            )
        
        # Check for data
        data = None
        if hasattr(scraping_result, 'data'):
            data = scraping_result.data
        elif isinstance(scraping_result, dict):
            data = scraping_result.get('data')
        elif isinstance(scraping_result, list):
            data = scraping_result
        
        if not data:
            raise EmptyDataError(
                "No data was found in the scraped results. "
                "Please verify the data source URL and try again."
            )
    
    def _create_metadata(
        self,
        scraping_result: Any,
        user_requirements: Dict[str, Any],
        parsed_data: Dict[str, Any],
        model: str,
        ai_output: str,
        parsing_time_ms: int
    ) -> ParsingMetadata:
        """
        Create metadata for the parsed response.
        
        Args:
            scraping_result: Original scraping result
            user_requirements: User's requirements
            parsed_data: Parsed data dictionary
            model: Model used for parsing
            ai_output: Raw AI output
            parsing_time_ms: Time taken to parse
            
        Returns:
            ParsingMetadata object
        """
        # Count records
        records_parsed = self._count_records(parsed_data)
        
        # Extract field names from parsed data
        fields_extracted = self.extractor.extract_field_names(parsed_data)
        
        # Get data sources
        data_sources = self._get_data_sources(scraping_result, user_requirements)
        
        # Estimate tokens
        tokens_used = len(ai_output) // 4  # Rough estimate
        
        return ParsingMetadata(
            timestamp=datetime.utcnow(),
            model=model,
            tokens_used=tokens_used,
            parsing_time_ms=parsing_time_ms,
            records_parsed=records_parsed,
            fields_extracted=fields_extracted,
            data_sources=data_sources
        )
    
    def _count_records(self, data: Dict[str, Any]) -> int:
        """
        Count the number of records in parsed data.
        
        Args:
            data: Parsed data dictionary
            
        Returns:
            Number of records
        """
        if 'data' in data and isinstance(data['data'], list):
            return len(data['data'])
        elif isinstance(data, list):
            return len(data)
        return 1
    
    def _get_data_sources(
        self,
        scraping_result: Any,
        user_requirements: Dict[str, Any]
    ) -> List[str]:
        """
        Get list of data source URLs.
        
        Args:
            scraping_result: Scraping result
            user_requirements: User requirements
            
        Returns:
            List of source URLs
        """
        sources = []
        
        # From scraping result metadata
        if hasattr(scraping_result, 'metadata'):
            metadata = scraping_result.metadata
            if hasattr(metadata, 'final_url') and metadata.final_url:
                sources.append(metadata.final_url)
        
        # From scraping result source_results
        if hasattr(scraping_result, 'source_results'):
            for sr in scraping_result.source_results:
                if hasattr(sr, 'source_url') and sr.source_url:
                    if sr.source_url not in sources:
                        sources.append(sr.source_url)
        
        # From user requirements
        user_source = user_requirements.get('data_source', '')
        if user_source and user_source not in sources:
            sources.append(user_source)
        
        return sources if sources else ['Unknown']
    
    def _extract_source_metadata(self, scraping_result: Any) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from the scraping result.
        
        Args:
            scraping_result: Scraping result
            
        Returns:
            Dictionary with source metadata or None
        """
        if hasattr(scraping_result, 'metadata'):
            metadata = scraping_result.metadata
            return {
                'strategy_used': str(getattr(metadata, 'strategy_used', 'unknown')),
                'final_url': getattr(metadata, 'final_url', None),
                'response_status': getattr(metadata, 'response_status', None),
                'timestamp': str(getattr(metadata, 'timestamp', datetime.utcnow()))
            }
        return None
    
    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        return len(text) // 4
