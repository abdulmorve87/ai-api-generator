"""
Scraper Script Generator - Main orchestration component.

This module provides the main ScraperScriptGenerator class that coordinates
all components to generate executable BeautifulSoup scraper scripts from form inputs.
"""

import time
import re
from datetime import datetime
from typing import Dict, Any, List
import logging

from ai_layer.deepseek_client import DeepSeekClient
from ai_layer.script_prompt_builder import ScriptPromptBuilder
from ai_layer.script_validator import ScriptValidator
from ai_layer.input_processor import InputProcessor
from ai_layer.script_models import (
    GeneratedScript, ScriptMetadata, ScriptValidationResult,
    ScriptGenerationError, ScriptValidationError
)
from ai_layer.exceptions import ValidationError
from scraping_layer.config import ScrapingConfig


class ScraperScriptGenerator:
    """Orchestrates the generation of scraper scripts from form inputs."""
    
    def __init__(
        self,
        deepseek_client: DeepSeekClient,
        scraping_config: ScrapingConfig,
        logger: logging.Logger = None
    ):
        """
        Initialize the Scraper Script Generator.
        
        Args:
            deepseek_client: Configured DeepSeek API client
            scraping_config: Scraping layer configuration
            logger: Optional logger instance
        """
        self.client = deepseek_client
        self.scraping_config = scraping_config
        self.prompt_builder = ScriptPromptBuilder(scraping_config)
        self.validator = ScriptValidator(logger)
        self.logger = logger or logging.getLogger(__name__)
    
    def generate_script(
        self,
        form_input: Dict[str, Any],
        model: str = "deepseek-chat",
        temperature: float = 0.3,  # Lower for more deterministic code generation
        max_tokens: int = 8000,  # Increased to handle complex scripts without truncation
        max_retries: int = 2
    ) -> GeneratedScript:
        """
        Generate a BeautifulSoup scraper script from form inputs.
        
        Args:
            form_input: Dictionary containing:
                - data_description: str (required)
                - data_source: str (required - target URL)
                - desired_fields: str (optional, newline-separated)
                - response_structure: str (optional, JSON string)
                - update_frequency: str (required)
            model: DeepSeek model to use (default: "deepseek-chat")
            temperature: Sampling temperature (default: 0.3 for code)
            max_tokens: Maximum tokens in response (default: 8000)
            max_retries: Maximum generation retries on validation failure
            
        Returns:
            GeneratedScript object with Python code and metadata
            
        Raises:
            ValidationError: When form inputs are invalid
            ScriptGenerationError: When AI generation fails
            ScriptValidationError: When generated script fails validation after retries
        """
        # Extract and validate form fields
        try:
            fields = self._extract_form_fields(form_input)
        except ValidationError as e:
            raise ScriptGenerationError(f"Invalid form input: {str(e)}", form_input)
        
        # Note: data_source is now optional - AI will suggest URLs if not provided
        
        # Attempt generation with retries
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                self.logger.info(f"Generating script (attempt {attempt + 1}/{max_retries + 1})")
                
                # Step 1: Build prompt
                messages = self._build_script_prompt(form_input)
                
                # Step 2: Call DeepSeek API
                start_time = time.time()
                ai_output = self.client.generate_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                generation_time_ms = int((time.time() - start_time) * 1000)
                
                # Step 3: Extract Python code from AI output
                script_code = self._extract_code(ai_output)
                
                # Step 4: Validate script
                validation_result = self._validate_script(script_code)
                
                # Step 5: Create metadata
                metadata = ScriptMetadata(
                    timestamp=datetime.utcnow(),
                    model=model,
                    tokens_used=self._estimate_tokens(ai_output),
                    generation_time_ms=generation_time_ms,
                    target_url=fields.get('data_source', 'AI will suggest URLs'),
                    required_fields=InputProcessor.parse_fields(fields.get('desired_fields', ''))
                )
                
                # Step 6: Create and return GeneratedScript
                generated_script = GeneratedScript(
                    script_code=script_code,
                    metadata=metadata,
                    validation_result=validation_result,
                    raw_output=ai_output
                )
                
                if validation_result.is_valid:
                    self.logger.info("Script generation successful")
                    return generated_script
                else:
                    # Validation failed, will retry if attempts remain
                    last_error = ScriptValidationError(
                        f"Generated script failed validation: {validation_result.errors}",
                        validation_result
                    )
                    self.logger.warning(f"Validation failed on attempt {attempt + 1}: {validation_result.errors}")
                    
                    if attempt < max_retries:
                        # Adjust temperature for retry (make it more deterministic)
                        temperature = max(0.1, temperature - 0.1)
                        continue
                    else:
                        # Return the script even if validation failed (let caller decide)
                        self.logger.error("Max retries reached, returning invalid script")
                        return generated_script
                        
            except Exception as e:
                last_error = e
                self.logger.error(f"Error during script generation (attempt {attempt + 1}): {str(e)}")
                
                if attempt < max_retries:
                    continue
                else:
                    raise ScriptGenerationError(
                        f"Failed to generate script after {max_retries + 1} attempts: {str(e)}",
                        form_input
                    )
        
        # Should not reach here, but just in case
        if last_error:
            raise last_error
        raise ScriptGenerationError("Script generation failed for unknown reason", form_input)
    
    def _extract_form_fields(self, form_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all form fields from input dictionary.
        
        Args:
            form_input: Dictionary containing form data
            
        Returns:
            Dictionary with extracted fields
            
        Raises:
            ValidationError: If required fields are missing
        """
        return InputProcessor.extract_form_fields(form_input)
    
    def _build_script_prompt(self, form_input: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Construct prompt messages for script generation.
        
        Args:
            form_input: Dictionary containing form data
            
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        return self.prompt_builder.build_script_prompt(form_input)
    
    def _extract_code(self, ai_output: str) -> str:
        """
        Extract Python code from AI output.
        
        Handles cases where AI wraps code in markdown code blocks.
        
        Args:
            ai_output: Raw output from AI
            
        Returns:
            Extracted Python code
        """
        # Try to extract code from markdown code blocks
        code_block_pattern = r'```(?:python)?\n(.*?)\n```'
        matches = re.findall(code_block_pattern, ai_output, re.DOTALL)
        
        if matches:
            # Use the first code block found
            code = matches[0].strip()
            self.logger.debug("Extracted code from markdown block")
            return code
        
        # If no code blocks, assume entire output is code
        code = ai_output.strip()
        
        # Remove any leading/trailing markdown artifacts
        if code.startswith('```'):
            code = code[3:].strip()
        if code.endswith('```'):
            code = code[:-3].strip()
        
        # Remove language identifier if present
        if code.startswith('python\n'):
            code = code[7:].strip()
        
        return code
    
    def _validate_script(self, script_code: str) -> ScriptValidationResult:
        """
        Validate generated Python script.
        
        Args:
            script_code: Python code to validate
            
        Returns:
            ScriptValidationResult with validation status
        """
        return self.validator.validate_script(script_code)
    
    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """
        Estimate token count for text.
        
        This is a rough approximation. For accurate counts, use tiktoken library.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 characters per token for English text
        return len(text) // 4
