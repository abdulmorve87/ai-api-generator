"""
Console Logger - Colorful and informative console logging with progress indicators.

This module provides a rich console logging system with:
- Colorful output using the Rich library
- Progress bars for long-running operations (AI calls, scraping)
- Structured logging with timestamps and context
- Visual separators and status indicators
"""

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich import box
from rich.style import Style
from rich.theme import Theme
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import time


# Custom theme for consistent styling
CUSTOM_THEME = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "highlight": "bold magenta",
    "muted": "dim white",
    "step": "bold blue",
    "ai": "bold cyan",
    "scrape": "bold yellow",
    "api": "bold green",
    "data": "bold white",
})

# Global console instance
console = Console(theme=CUSTOM_THEME)


class ConsoleLogger:
    """Rich console logger with colorful output and progress indicators."""
    
    def __init__(self):
        self.console = console
        self._start_time: Optional[float] = None
        self._current_phase: Optional[str] = None
    
    # =========================================================================
    # SECTION HEADERS
    # =========================================================================
    
    def header(self, title: str, subtitle: str = None, style: str = "bold white on blue"):
        """Print a prominent header section."""
        self.console.print()
        header_text = Text(f"  {title}  ", style=style)
        self.console.print(Panel(header_text, expand=True, border_style="blue"))
        if subtitle:
            self.console.print(f"  [muted]{subtitle}[/muted]")
        self.console.print()
    
    def section(self, title: str, icon: str = "📌"):
        """Print a section divider."""
        self.console.print()
        self.console.print(f"[step]{'─' * 60}[/step]")
        self.console.print(f"[step]{icon} {title}[/step]")
        self.console.print(f"[step]{'─' * 60}[/step]")
    
    def subsection(self, title: str, icon: str = "▸"):
        """Print a subsection header."""
        self.console.print(f"\n[highlight]{icon} {title}[/highlight]")
    
    # =========================================================================
    # STATUS MESSAGES
    # =========================================================================
    
    def info(self, message: str, icon: str = "ℹ️"):
        """Print an info message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.print(f"[muted]{timestamp}[/muted] {icon} [info]{message}[/info]")
    
    def success(self, message: str, icon: str = "✅"):
        """Print a success message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.print(f"[muted]{timestamp}[/muted] {icon} [success]{message}[/success]")
    
    def warning(self, message: str, icon: str = "⚠️"):
        """Print a warning message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.print(f"[muted]{timestamp}[/muted] {icon} [warning]{message}[/warning]")
    
    def error(self, message: str, icon: str = "❌"):
        """Print an error message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.print(f"[muted]{timestamp}[/muted] {icon} [error]{message}[/error]")
    
    def step(self, step_num: int, total: int, message: str):
        """Print a step indicator."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.print(
            f"[muted]{timestamp}[/muted] [step]Step {step_num}/{total}:[/step] {message}"
        )
    
    # =========================================================================
    # DATA DISPLAY
    # =========================================================================
    
    def key_value(self, key: str, value: Any, indent: int = 2):
        """Print a key-value pair."""
        spaces = " " * indent
        self.console.print(f"{spaces}[data]{key}:[/data] [info]{value}[/info]")
    
    def table(self, title: str, data: Dict[str, Any], style: str = "info"):
        """Print data as a formatted table."""
        table = Table(title=title, box=box.ROUNDED, border_style=style)
        table.add_column("Property", style="bold")
        table.add_column("Value")
        
        for key, value in data.items():
            table.add_row(str(key), str(value))
        
        self.console.print(table)
    
    def code_block(self, code: str, language: str = "python", title: str = None):
        """Print a code block with syntax highlighting."""
        from rich.syntax import Syntax
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        if title:
            self.console.print(Panel(syntax, title=title, border_style="green"))
        else:
            self.console.print(syntax)
    
    # =========================================================================
    # PROGRESS INDICATORS
    # =========================================================================
    
    @contextmanager
    def progress_spinner(self, description: str, style: str = "cyan"):
        """Context manager for a simple spinner."""
        with self.console.status(f"[{style}]{description}[/{style}]", spinner="dots"):
            yield
    
    @contextmanager
    def ai_progress(self, operation: str = "AI Processing"):
        """
        Context manager for AI API calls with animated progress.
        Shows a pulsing progress bar to indicate ongoing AI processing.
        """
        self.console.print()
        self.console.print(f"[ai]🤖 {operation}[/ai]")
        
        with Progress(
            SpinnerColumn(spinner_name="dots12", style="cyan"),
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(bar_width=40, style="cyan", complete_style="bold cyan"),
            TextColumn("[cyan]{task.fields[status]}"),
            TimeElapsedColumn(),
            console=self.console,
            transient=False
        ) as progress:
            task = progress.add_task(
                "Calling DeepSeek API...",
                total=None,  # Indeterminate
                status="⏳ Waiting for response..."
            )
            
            class ProgressUpdater:
                def __init__(self, progress_obj, task_id):
                    self.progress = progress_obj
                    self.task_id = task_id
                
                def update(self, description: str = None, status: str = None):
                    updates = {}
                    if description:
                        updates["description"] = description
                    if status:
                        updates["status"] = status
                    self.progress.update(self.task_id, **updates)
                
                def complete(self, message: str = "Done!"):
                    self.progress.update(self.task_id, status=f"✅ {message}")
            
            yield ProgressUpdater(progress, task)
    
    @contextmanager
    def scraping_progress(self, urls: List[str]):
        """
        Context manager for scraping operations with progress tracking.
        Shows progress through multiple URLs being scraped.
        """
        self.console.print()
        self.console.print(f"[scrape]🔍 Scraping Data Sources[/scrape]")
        self.console.print(f"[muted]   Processing {len(urls)} URL(s)[/muted]")
        
        with Progress(
            SpinnerColumn(spinner_name="dots", style="yellow"),
            TextColumn("[bold yellow]{task.description}"),
            BarColumn(bar_width=40, style="yellow", complete_style="bold green"),
            TaskProgressColumn(),
            TextColumn("[yellow]{task.fields[status]}"),
            TimeElapsedColumn(),
            console=self.console,
            transient=False
        ) as progress:
            task = progress.add_task(
                "Scraping...",
                total=len(urls),
                status="Starting..."
            )
            
            class ScrapingProgressUpdater:
                def __init__(self, progress_obj, task_id, total_urls):
                    self.progress = progress_obj
                    self.task_id = task_id
                    self.total = total_urls
                    self.current = 0
                    self.records_collected = 0
                
                def start_url(self, url: str, index: int):
                    short_url = url[:50] + "..." if len(url) > 50 else url
                    self.progress.update(
                        self.task_id,
                        description=f"Scraping: {short_url}",
                        status=f"URL {index + 1}/{self.total}"
                    )
                
                def complete_url(self, url: str, records: int, success: bool = True):
                    self.current += 1
                    self.records_collected += records
                    status = f"✓ {records} records" if success else "✗ Failed"
                    self.progress.update(
                        self.task_id,
                        advance=1,
                        status=status
                    )
                
                def finish(self, total_records: int):
                    self.progress.update(
                        self.task_id,
                        description="Scraping complete",
                        status=f"✅ {total_records} total records"
                    )
            
            yield ScrapingProgressUpdater(progress, task, len(urls))

    
    # =========================================================================
    # WORKFLOW LOGGING - API GENERATION FLOW
    # =========================================================================
    
    def start_api_generation(self, form_data: Dict[str, Any]):
        """Log the start of API generation workflow."""
        self._start_time = time.time()
        
        self.header(
            "🚀 API GENERATION STARTED",
            f"Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            style="bold white on blue"
        )
        
        # Display form data summary
        table = Table(title="📋 Request Details", box=box.ROUNDED, border_style="blue")
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Data Description", str(form_data.get('data_description', 'N/A'))[:80])
        table.add_row("Data Source", str(form_data.get('data_source', 'AI will suggest'))[:80])
        table.add_row("Desired Fields", str(form_data.get('desired_fields', 'N/A'))[:80])
        table.add_row("Scraping Mode", "Light (HTML+AI)" if form_data.get('use_light_scraping') else "Traditional")
        
        self.console.print(table)
        self.console.print()
    
    def log_script_generation_start(self, scraping_mode: str):
        """Log the start of script generation phase."""
        self._current_phase = "script_generation"
        self.section("PHASE 1: Script Generation", "🤖")
        self.info(f"Scraping Mode: {scraping_mode}")
    
    def log_script_generation_complete(self, validation_result: Any, metadata: Any):
        """Log successful script generation."""
        self.success("Script generated successfully!")
        
        # Validation status
        status_table = Table(box=box.SIMPLE, show_header=False, border_style="green")
        status_table.add_column("Check", style="bold")
        status_table.add_column("Status")
        
        checks = [
            ("Syntax Valid", validation_result.syntax_valid),
            ("Imports Valid", validation_result.imports_valid),
            ("No Forbidden Ops", validation_result.no_forbidden_ops),
            ("Function Signature", validation_result.function_signature_valid),
        ]
        
        for check_name, passed in checks:
            icon = "✅" if passed else "❌"
            status_table.add_row(check_name, f"{icon} {'Pass' if passed else 'Fail'}")
        
        self.console.print(status_table)
        
        # Metadata
        if metadata:
            self.key_value("Generation Time", f"{metadata.generation_time_ms}ms")
            self.key_value("Tokens Used", metadata.tokens_used)
            self.key_value("Model", metadata.model)
    
    def log_scraping_start(self, urls: List[str]):
        """Log the start of scraping phase."""
        self._current_phase = "scraping"
        self.section("PHASE 2: Data Scraping", "🔍")
        self.info(f"Target URLs: {len(urls)}")
        for i, url in enumerate(urls, 1):
            short_url = url[:70] + "..." if len(url) > 70 else url
            self.console.print(f"  [muted]{i}.[/muted] {short_url}")
    
    def log_scraping_complete(self, total_records: int, source_results: List[Any] = None):
        """Log successful scraping completion."""
        self.success(f"Scraping complete! Extracted {total_records} records")
        
        if source_results:
            table = Table(title="📊 Source Results", box=box.ROUNDED, border_style="yellow")
            table.add_column("Source", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Records", justify="right")
            table.add_column("Method")
            table.add_column("Confidence")
            
            for sr in source_results:
                status = "[green]✓ Success[/green]" if sr.success else f"[red]✗ {sr.error or 'Failed'}[/red]"
                short_url = sr.source_url[:40] + "..." if len(sr.source_url) > 40 else sr.source_url
                table.add_row(
                    short_url,
                    status,
                    str(sr.record_count),
                    getattr(sr, 'scraping_method', 'N/A'),
                    getattr(sr, 'confidence', 'N/A')
                )
            
            self.console.print(table)
    
    def log_parsing_start(self, records_count: int):
        """Log the start of data parsing phase."""
        self._current_phase = "parsing"
        self.section("PHASE 3: AI Data Parsing", "🧠")
        self.info(f"Parsing {records_count} records into structured JSON")
    
    def log_parsing_complete(self, metadata: Any):
        """Log successful parsing completion."""
        self.success("Data parsed successfully!")
        
        table = Table(box=box.SIMPLE, show_header=False, border_style="cyan")
        table.add_column("Metric", style="bold")
        table.add_column("Value")
        
        table.add_row("Records Parsed", str(metadata.records_parsed))
        table.add_row("Fields Extracted", ", ".join(metadata.fields_extracted[:5]) + ("..." if len(metadata.fields_extracted) > 5 else ""))
        table.add_row("Parsing Time", f"{metadata.parsing_time_ms}ms")
        table.add_row("Model", metadata.model)
        
        self.console.print(table)
    
    def log_endpoint_creation_start(self, description: str):
        """Log the start of endpoint creation phase."""
        self._current_phase = "endpoint_creation"
        self.section("PHASE 4: API Endpoint Creation", "🔗")
        self.info(f"Creating endpoint: {description[:50]}...")
    
    def log_endpoint_creation_complete(self, endpoint_info: Any):
        """Log successful endpoint creation."""
        self.success("API Endpoint created successfully!")
        
        # Prominent endpoint URL display
        url_panel = Panel(
            Text(endpoint_info.access_url, style="bold green"),
            title="🌐 API Endpoint URL",
            border_style="green",
            expand=False
        )
        self.console.print(url_panel)
        
        self.key_value("Endpoint ID", endpoint_info.endpoint_id)
        self.key_value("Records Available", endpoint_info.records_count)
        self.key_value("Created At", endpoint_info.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    
    def log_workflow_complete(self):
        """Log the completion of the entire workflow."""
        if self._start_time:
            total_time = time.time() - self._start_time
            
            self.console.print()
            self.header(
                "✨ API GENERATION COMPLETE",
                f"Total time: {total_time:.2f} seconds",
                style="bold white on green"
            )
        
        self._start_time = None
        self._current_phase = None
    
    def log_workflow_error(self, phase: str, error: Exception):
        """Log a workflow error."""
        self.console.print()
        self.error(f"Error in {phase}: {str(error)}")
        
        if self._start_time:
            elapsed = time.time() - self._start_time
            self.console.print(f"[muted]Failed after {elapsed:.2f} seconds[/muted]")
        
        self._start_time = None
        self._current_phase = None


# Global logger instance
logger = ConsoleLogger()


# =========================================================================
# CONVENIENCE FUNCTIONS
# =========================================================================

def start_api_generation(form_data: Dict[str, Any]):
    """Start API generation workflow logging."""
    logger.start_api_generation(form_data)

def log_ai_call_start(operation: str):
    """Log start of an AI API call."""
    return logger.ai_progress(operation)

def log_scraping_start(urls: List[str]):
    """Log start of scraping operation."""
    return logger.scraping_progress(urls)

def log_success(message: str):
    """Log a success message."""
    logger.success(message)

def log_error(message: str):
    """Log an error message."""
    logger.error(message)

def log_info(message: str):
    """Log an info message."""
    logger.info(message)

def log_warning(message: str):
    """Log a warning message."""
    logger.warning(message)
