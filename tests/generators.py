"""
Hypothesis generators for property-based testing.

This module provides custom generators for creating test data that covers
the full range of inputs the scraping system might encounter.
"""

from hypothesis import strategies as st
from hypothesis.strategies import composite
from typing import Dict, Any, List
import string

from scraping_layer.models import (
    ScriptConfig, ScrapingStrategy, FrameworkType, BrowserRequirements,
    RetryConfig, InteractionStep, PaginationConfig, WebsiteAnalysis,
    FrameworkInfo, ScrapingError, PerformanceMetrics
)


# Basic generators
@composite
def urls(draw):
    """Generate valid URLs for testing."""
    protocol = draw(st.sampled_from(['http', 'https']))
    domain = draw(st.text(
        alphabet=string.ascii_lowercase + string.digits + '-',
        min_size=3,
        max_size=20
    ).filter(lambda x: not x.startswith('-') and not x.endswith('-')))
    tld = draw(st.sampled_from(['com', 'org', 'net', 'io', 'co.uk']))
    path = draw(st.text(
        alphabet=string.ascii_letters + string.digits + '/-_',
        min_size=0,
        max_size=50
    ))
    
    url = f"{protocol}://{domain}.{tld}"
    if path and not path.startswith('/'):
        path = '/' + path
    return url + path


@composite
def css_selectors(draw):
    """Generate valid CSS selectors."""
    selector_types = [
        # Element selectors
        st.sampled_from(['div', 'span', 'p', 'h1', 'h2', 'h3', 'a', 'img']),
        # Class selectors
        st.text(alphabet=string.ascii_letters + '-_', min_size=1, max_size=20).map(lambda x: f'.{x}'),
        # ID selectors
        st.text(alphabet=string.ascii_letters + '-_', min_size=1, max_size=20).map(lambda x: f'#{x}'),
        # Attribute selectors
        st.text(alphabet=string.ascii_letters, min_size=1, max_size=10).map(lambda x: f'[{x}]'),
        # Combined selectors
        st.text(alphabet=string.ascii_letters + ' .#-_', min_size=3, max_size=30)
    ]
    
    return draw(st.one_of(selector_types))


@composite
def selector_dict(draw):
    """Generate dictionaries of CSS selectors."""
    keys = draw(st.lists(
        st.text(alphabet=string.ascii_letters + '_', min_size=1, max_size=15),
        min_size=1,
        max_size=10,
        unique=True
    ))
    
    selectors = {}
    for key in keys:
        selectors[key] = draw(css_selectors())
    
    return selectors


@composite
def html_content(draw):
    """Generate HTML content with various framework signatures."""
    framework = draw(st.sampled_from(list(FrameworkType)))
    
    base_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        {head_scripts}
    </head>
    <body>
        <div id="root">
            {body_content}
        </div>
        {body_scripts}
    </body>
    </html>
    """
    
    title = draw(st.text(min_size=1, max_size=50))
    
    # Framework-specific signatures
    framework_signatures = {
        FrameworkType.REACT: {
            'head_scripts': '<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>',
            'body_content': '<div class="react-component">React Content</div>',
            'body_scripts': '<script>ReactDOM.render(React.createElement("div"), document.getElementById("root"));</script>'
        },
        FrameworkType.ANGULAR: {
            'head_scripts': '<script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.6.9/angular.min.js"></script>',
            'body_content': '<div ng-app="myApp" ng-controller="myCtrl">{{message}}</div>',
            'body_scripts': '<script>angular.module("myApp", []);</script>'
        },
        FrameworkType.VUE: {
            'head_scripts': '<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>',
            'body_content': '<div id="app">{{ message }}</div>',
            'body_scripts': '<script>Vue.createApp({ data() { return { message: "Hello Vue!" } } }).mount("#app");</script>'
        },
        FrameworkType.JQUERY: {
            'head_scripts': '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>',
            'body_content': '<div class="jquery-content">Content</div>',
            'body_scripts': '<script>$(document).ready(function() { console.log("jQuery loaded"); });</script>'
        },
        FrameworkType.VANILLA_JS: {
            'head_scripts': '',
            'body_content': '<div class="vanilla-content">Vanilla JS Content</div>',
            'body_scripts': '<script>document.addEventListener("DOMContentLoaded", function() { console.log("Loaded"); });</script>'
        },
        FrameworkType.UNKNOWN: {
            'head_scripts': '',
            'body_content': '<div>Static Content</div>',
            'body_scripts': ''
        }
    }
    
    signatures = framework_signatures.get(framework, framework_signatures[FrameworkType.UNKNOWN])
    
    return base_html.format(
        title=title,
        head_scripts=signatures['head_scripts'],
        body_content=signatures['body_content'],
        body_scripts=signatures['body_scripts']
    )


@composite
def interaction_steps(draw):
    """Generate interaction steps for dynamic scraping."""
    actions = ['click', 'scroll', 'type', 'wait', 'submit']
    action = draw(st.sampled_from(actions))
    
    step = InteractionStep(action=action)
    
    if action in ['click', 'type', 'submit']:
        step.selector = draw(css_selectors())
    
    if action == 'type':
        step.value = draw(st.text(min_size=1, max_size=100))
    
    if action == 'wait':
        step.timeout = draw(st.integers(min_value=1000, max_value=30000))
    
    return step


@composite
def script_configs(draw):
    """Generate ScriptConfig objects for testing."""
    return ScriptConfig(
        url=draw(urls()),
        script_type=draw(st.sampled_from(list(ScrapingStrategy))),
        selectors=draw(selector_dict()),
        interactions=draw(st.lists(interaction_steps(), min_size=0, max_size=5)),
        cache_ttl=draw(st.integers(min_value=60, max_value=86400)),
        timeout=draw(st.integers(min_value=5, max_value=120))
    )


@composite
def website_analyses(draw):
    """Generate WebsiteAnalysis objects for testing."""
    framework_type = draw(st.sampled_from(list(FrameworkType)))
    is_static = framework_type in [FrameworkType.UNKNOWN, FrameworkType.VANILLA_JS]
    
    framework_info = None
    if framework_type != FrameworkType.UNKNOWN:
        framework_info = FrameworkInfo(
            framework=framework_type,
            version=draw(st.text(min_size=1, max_size=10)),
            confidence=draw(st.floats(min_value=0.0, max_value=1.0))
        )
    
    return WebsiteAnalysis(
        is_static=is_static,
        framework=framework_info,
        requires_javascript=not is_static,
        has_anti_bot=draw(st.booleans()),
        estimated_load_time=draw(st.floats(min_value=0.1, max_value=10.0)),
        recommended_strategy=draw(st.sampled_from(list(ScrapingStrategy))),
        confidence_score=draw(st.floats(min_value=0.0, max_value=1.0))
    )


@composite
def extracted_data(draw):
    """Generate extracted data for testing."""
    num_items = draw(st.integers(min_value=0, max_value=20))
    
    data = []
    for _ in range(num_items):
        item = {}
        num_fields = draw(st.integers(min_value=1, max_value=10))
        
        for _ in range(num_fields):
            field_name = draw(st.text(
                alphabet=string.ascii_letters + '_',
                min_size=1,
                max_size=20
            ))
            field_value = draw(st.one_of([
                st.text(min_size=0, max_size=200),
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.booleans(),
                st.none()
            ]))
            item[field_name] = field_value
        
        data.append(item)
    
    return data


@composite
def malformed_data(draw):
    """Generate malformed data for testing data cleaning."""
    base_data = draw(extracted_data())
    
    # Introduce various types of malformation
    for item in base_data:
        for key, value in item.items():
            if isinstance(value, str) and value:
                # Add HTML entities
                if draw(st.booleans()):
                    item[key] = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                # Add extra whitespace
                if draw(st.booleans()):
                    item[key] = f"  {value}  \n\t"
                
                # Add potential XSS
                if draw(st.booleans()):
                    item[key] = f"<script>alert('xss')</script>{value}"
    
    return base_data


@composite
def error_scenarios(draw):
    """Generate error scenarios for testing error handling."""
    error_types = [
        'NetworkError', 'TimeoutError', 'ValidationError',
        'SecurityError', 'BrowserError', 'ScriptError'
    ]
    
    return ScrapingError(
        error_type=draw(st.sampled_from(error_types)),
        message=draw(st.text(min_size=10, max_size=200)),
        recoverable=draw(st.booleans())
    )


# Export commonly used generators
url_generator = urls()
selector_generator = css_selectors()
html_generator = html_content()
script_config_generator = script_configs()
website_analysis_generator = website_analyses()
data_generator = extracted_data()
malformed_data_generator = malformed_data()
error_generator = error_scenarios()