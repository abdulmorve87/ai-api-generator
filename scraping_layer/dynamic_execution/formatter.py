"""
Console Output Formatter - Formats and displays scraping results.

This module provides the ConsoleOutputFormatter class that formats
ExecutionResult objects for clear, readable console display.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .models import ExecutionResult, SourceResult


class ConsoleOutputFormatter:
    """Formats scraping results for console display."""
    
    # ANSI color codes for terminal output
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'gray': '\033[90m'
    }
    
    def __init__(
        self,
        max_records_display: int = 10,
        show_full_data: bool = True,
        use_colors: bool = True,
        indent: int = 2
    ):
        """
        Initialize the formatter.
        
        Args:
            max_records_display: Maximum number of records to display
            show_full_data: Whether to show all record fields (default: True)
            use_colors: Whether to use ANSI colors in output
            indent: Indentation level for nested data
        """
        self.max_records_display = max_records_display
        self.show_full_data = show_full_data
        self.use_colors = use_colors
        self.indent = indent
    
    def _color(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled."""
        if self.use_colors and color in self.COLORS:
            return f"{self.COLORS[color]}{text}{self.COLORS['reset']}"
        return text
    
    def format_result(self, result: ExecutionResult) -> str:
        """
        Format execution result for console display.
        
        Args:
            result: ExecutionResult from script execution
            
        Returns:
            Formatted string for console output
        """
        lines = []
        
        # Header
        lines.append(self._format_header(result))
        lines.append("")
        
        # Metadata/Statistics
        lines.append(self._format_metadata(result))
        lines.append("")
        
        # Source results (if multi-source)
        if result.source_results and len(result.source_results) > 1:
            lines.append(self._format_source_results(result.source_results))
            lines.append("")
        
        # Data records
        if result.data:
            lines.append(self._format_data_records(result.data, result.source_results))
        else:
            lines.append(self._color("No data extracted.", 'yellow'))
        
        # Errors
        if result.errors:
            lines.append("")
            lines.append(self._format_errors(result.errors))
        
        # Footer
        lines.append("")
        lines.append(self._format_footer(result))
        
        return "\n".join(lines)
    
    def print_result(self, result: ExecutionResult) -> None:
        """Print formatted result to console."""
        print(self.format_result(result))
    
    def _format_header(self, result: ExecutionResult) -> str:
        """Format summary header."""
        separator = "=" * 80
        
        status = self._color("SUCCESS", 'green') if result.success else self._color("FAILED", 'red')
        if result.partial_success:
            status = self._color("PARTIAL SUCCESS", 'yellow')
        
        header_lines = [
            separator,
            self._color("SCRAPING EXECUTION RESULT", 'bold'),
            separator,
            f"Status: {status}",
            f"Total Records: {self._color(str(len(result.data)), 'cyan')}",
            f"Execution Time: {self._color(f'{result.execution_time_ms}ms', 'cyan')}",
            f"Scraped At: {result.scraped_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        ]
        
        return "\n".join(header_lines)
    
    def _format_metadata(self, result: ExecutionResult) -> str:
        """Format execution metadata."""
        meta = result.metadata
        lines = [self._color("METADATA:", 'bold')]
        
        if meta.target_urls:
            if len(meta.target_urls) == 1:
                lines.append(f"  Source URL: {meta.target_urls[0]}")
            else:
                lines.append(f"  Source URLs: {len(meta.target_urls)} sources")
        
        lines.append(f"  Total Count: {meta.total_count}")
        
        if meta.filtered_count > 0:
            lines.append(f"  Filtered: {meta.filtered_count}")
        
        if meta.duplicate_count > 0:
            lines.append(f"  Duplicates Removed: {meta.duplicate_count}")
        
        if meta.scraping_method != 'unknown':
            lines.append(f"  Scraping Method: {meta.scraping_method}")
            lines.append(f"  Confidence: {meta.confidence}")
        
        if meta.generation_time_ms:
            lines.append(f"  AI Generation Time: {meta.generation_time_ms}ms")
        
        if meta.model_used:
            lines.append(f"  AI Model: {meta.model_used}")
        
        if meta.update_frequency:
            lines.append(f"  Update Frequency: {meta.update_frequency}")
        
        return "\n".join(lines)
    
    def _format_source_results(self, source_results: List[SourceResult]) -> str:
        """Format per-source results."""
        lines = [self._color("SOURCE RESULTS:", 'bold')]
        
        for idx, sr in enumerate(source_results, 1):
            status_icon = self._color("✓", 'green') if sr.success else self._color("✗", 'red')
            lines.append(f"  {status_icon} Source {idx}: {sr.source_url}")
            lines.append(f"      Records: {sr.record_count}, Time: {sr.execution_time_ms}ms")
            
            if sr.error:
                lines.append(f"      {self._color(f'Error: {sr.error}', 'red')}")
            
            if sr.scraping_method != 'unknown':
                lines.append(f"      Method: {sr.scraping_method} ({sr.confidence} confidence)")
        
        return "\n".join(lines)
    
    def _format_data_records(
        self,
        data: List[Dict[str, Any]],
        source_results: List[SourceResult] = None
    ) -> str:
        """Format data records, grouped by source if multi-source."""
        lines = [self._color("DATA RECORDS:", 'bold')]
        
        # Check if we need to group by source
        has_source_info = any('_source_url' in record for record in data if isinstance(record, dict))
        
        if has_source_info and source_results and len(source_results) > 1:
            # Group by source URL
            grouped = self._group_by_source(data)
            
            for source_url, records in grouped.items():
                lines.append(f"\n  {self._color(f'From: {source_url}', 'blue')}")
                lines.append(f"  {'-' * 60}")
                lines.extend(self._format_record_list(records, indent=4))
        else:
            # Single source or no source info
            lines.extend(self._format_record_list(data, indent=2))
        
        return "\n".join(lines)
    
    def _group_by_source(self, data: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Group records by source URL."""
        grouped: Dict[str, List[Dict]] = {}
        
        for record in data:
            if isinstance(record, dict):
                source = record.get('_source_url', 'unknown')
                if source not in grouped:
                    grouped[source] = []
                grouped[source].append(record)
        
        return grouped
    
    def _format_record_list(
        self,
        records: List[Dict[str, Any]],
        indent: int = 2
    ) -> List[str]:
        """Format a list of records."""
        lines = []
        prefix = " " * indent
        
        display_count = min(len(records), self.max_records_display)
        
        for idx, record in enumerate(records[:display_count], 1):
            lines.append(f"{prefix}{self._color(f'Record {idx}:', 'cyan')}")
            
            if isinstance(record, dict):
                # Filter out internal fields
                display_record = {
                    k: v for k, v in record.items()
                    if not k.startswith('_')
                }
                
                if self.show_full_data:
                    # Show all fields with longer truncation
                    for key, value in display_record.items():
                        lines.append(f"{prefix}  {key}: {self._truncate(str(value), 500)}")
                else:
                    # Show key fields only
                    key_fields = ['title', 'name', 'date', 'description', 'link', 'url']
                    shown = False
                    
                    for field in key_fields:
                        if field in display_record:
                            lines.append(f"{prefix}  {field}: {self._truncate(str(display_record[field]), 80)}")
                            shown = True
                    
                    # If no key fields, show first few fields
                    if not shown:
                        for key, value in list(display_record.items())[:4]:
                            lines.append(f"{prefix}  {key}: {self._truncate(str(value), 80)}")
                    
                    # Show field count if more fields exist
                    extra_fields = len(display_record) - len([f for f in key_fields if f in display_record])
                    if extra_fields > 0 and not self.show_full_data:
                        lines.append(f"{prefix}  {self._color(f'... and {extra_fields} more fields', 'gray')}")
            else:
                lines.append(f"{prefix}  {self._truncate(str(record), 100)}")
        
        # Show remaining count
        if len(records) > display_count:
            remaining = len(records) - display_count
            lines.append(f"{prefix}{self._color(f'... and {remaining} more records', 'gray')}")
        
        return lines
    
    def _format_errors(self, errors: List[str]) -> str:
        """Format error messages."""
        lines = [self._color("ERRORS:", 'red')]
        
        for idx, error in enumerate(errors, 1):
            # Truncate long error messages
            error_display = self._truncate(error, 200)
            lines.append(f"  {idx}. {error_display}")
        
        return "\n".join(lines)
    
    def _format_footer(self, result: ExecutionResult) -> str:
        """Format footer with summary."""
        separator = "=" * 80
        
        summary_parts = []
        
        if result.success:
            summary_parts.append(f"Extracted {len(result.data)} records")
        else:
            summary_parts.append(f"Execution failed with {len(result.errors)} error(s)")
        
        if result.source_results:
            successful = sum(1 for sr in result.source_results if sr.success)
            total = len(result.source_results)
            summary_parts.append(f"{successful}/{total} sources succeeded")
        
        summary = " | ".join(summary_parts)
        
        return f"{separator}\n{summary}\n{separator}"
    
    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to max length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
    
    def format_json(self, result: ExecutionResult, indent: int = 2) -> str:
        """
        Format result as JSON string.
        
        Args:
            result: ExecutionResult to format
            indent: JSON indentation level
            
        Returns:
            JSON string representation
        """
        return result.to_json(indent=indent)
    
    def print_json(self, result: ExecutionResult, indent: int = 2) -> None:
        """Print result as formatted JSON."""
        print(self.format_json(result, indent))
