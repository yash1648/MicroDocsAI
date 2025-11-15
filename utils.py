"""
MicroDocs AI: Utility Functions and Configuration Helpers
Provides common utilities for the multi-agent system
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, env_file: Optional[str] = None):
        self.config = {}
        self.load_from_env(env_file)
    
    def load_from_env(self, env_file: Optional[str] = None) -> None:
        """Load configuration from environment or .env file"""
        if env_file and os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.split('=', 1)
                        self.config[key.strip()] = value.strip()
        
        # Load from environment variables
        self.config['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', '')
        self.config['PROJECT_PATH'] = os.environ.get('PROJECT_PATH', './sample_project')
        self.config['LOG_LEVEL'] = os.environ.get('LOG_LEVEL', 'INFO')
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def validate(self) -> bool:
        """Validate required configuration"""
        required_keys = ['GOOGLE_API_KEY']
        missing = [k for k in required_keys if not self.config.get(k)]
        
        if missing:
            logger.error(f"Missing required configuration: {missing}")
            return False
        
        return True

class LoggingConfigurator:
    """Configures application logging"""
    
    @staticmethod
    def setup(
        level: str = 'INFO',
        log_file: Optional[str] = None,
        format_string: Optional[str] = None
    ) -> None:
        """Configure logging"""
        if format_string is None:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Create logger
        logging.basicConfig(
            level=getattr(logging, level),
            format=format_string,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_file or 'microdocs.log')
            ]
        )
        
        logger.info(f"Logging configured at {level} level")

class CodeMetricsCollector:
    """Collects metrics about analyzed code"""
    
    def __init__(self):
        self.metrics = {
            'total_files': 0,
            'total_classes': 0,
            'total_methods': 0,
            'total_endpoints': 0,
            'total_dependencies': 0,
            'lines_of_code': 0
        }
    
    def add_file(self, file_path: str, content: str) -> None:
        """Record file analysis"""
        self.metrics['total_files'] += 1
        self.metrics['lines_of_code'] += len(content.split('\n'))
        
        if content.count('public class') > 0:
            self.metrics['total_classes'] += content.count('public class')
        
        if content.count('public') > 0:
            self.metrics['total_methods'] += content.count('public')
        
        if '@RequestMapping' in content or '@GetMapping' in content:
            self.metrics['total_endpoints'] += max(
                content.count('@GetMapping'),
                content.count('@PostMapping'),
                content.count('@PutMapping'),
                content.count('@DeleteMapping')
            )
        
        if '@Autowired' in content or '@Inject' in content:
            self.metrics['total_dependencies'] += max(
                content.count('@Autowired'),
                content.count('@Inject')
            )
    
    def get_metrics(self) -> Dict[str, int]:
        """Get collected metrics"""
        return self.metrics
    
    def get_summary(self) -> str:
        """Get human-readable metrics summary"""
        summary = "# Code Analysis Metrics\n\n"
        for key, value in self.metrics.items():
            summary += f"- {key}: {value}\n"
        return summary

class DocumentationFormatter:
    """Formats documentation output"""
    
    @staticmethod
    def format_api_doc(endpoint: Dict) -> str:
        """Format API endpoint documentation"""
        doc = f"""
### {endpoint.get('method', 'GET')} {endpoint.get('path', '/')}

**Handler**: `{endpoint.get('handler', 'N/A')}`

**Parameters**:
{DocumentationFormatter._format_params(endpoint.get('parameters', []))}

**Response**:
```json
{json.dumps(endpoint.get('response_schema', {}), indent=2)}
```

**Status Codes**:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 500: Server Error
"""
        return doc
    
    @staticmethod
    def _format_params(params: List[Dict]) -> str:
        """Format parameters list"""
        if not params:
            return "None"
        
        formatted = ""
        for param in params:
            formatted += f"- `{param.get('name')}` ({param.get('type')}): {param.get('description')}\n"
        return formatted
    
    @staticmethod
    def format_dependency_graph(dependencies: Dict) -> str:
        """Format dependency graph as Mermaid diagram"""
        mermaid = "```mermaid\ngraph TD\n"
        
        for service, deps in dependencies.items():
            for dep in deps:
                service_name = service.replace('.java', '').split('/')[-1]
                dep_name = dep.replace('[', '').replace(']', '')
                mermaid += f"    {service_name} --> {dep_name}\n"
        
        mermaid += "```"
        return mermaid

class PerformanceTracker:
    """Tracks and reports performance metrics"""
    
    def __init__(self):
        self.timings: Dict[str, List[float]] = {}
        self.start_times: Dict[str, float] = {}
    
    def start(self, operation: str) -> None:
        """Start timing an operation"""
        import time
        self.start_times[operation] = time.time()
    
    def end(self, operation: str) -> float:
        """End timing an operation and return elapsed time"""
        import time
        if operation not in self.start_times:
            logger.warning(f"No start time for operation: {operation}")
            return 0.0
        
        elapsed = time.time() - self.start_times[operation]
        
        if operation not in self.timings:
            self.timings[operation] = []
        
        self.timings[operation].append(elapsed)
        logger.info(f"{operation} completed in {elapsed:.2f} seconds")
        
        return elapsed
    
    def get_averages(self) -> Dict[str, float]:
        """Get average timings for all operations"""
        averages = {}
        for op, times in self.timings.items():
            averages[op] = sum(times) / len(times) if times else 0
        return averages
    
    def get_report(self) -> str:
        """Generate performance report"""
        report = "# Performance Report\n\n"
        report += f"**Generated**: {datetime.now().isoformat()}\n\n"
        
        averages = self.get_averages()
        report += "## Operation Timings\n\n"
        
        for op, avg_time in sorted(averages.items(), key=lambda x: x[1], reverse=True):
            samples = len(self.timings.get(op, []))
            report += f"- {op}: {avg_time:.2f}s (avg over {samples} runs)\n"
        
        total_time = sum(averages.values())
        report += f"\n**Total Time**: {total_time:.2f}s\n"
        
        return report

class CacheManager:
    """Simple in-memory cache for documentation results"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, tuple] = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve from cache"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            import time
            if time.time() - timestamp < self.ttl:
                logger.debug(f"Cache hit for {key}")
                return value
            else:
                del self.cache[key]
                logger.debug(f"Cache expired for {key}")
        
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Store in cache"""
        import time
        self.cache[key] = (value, time.time())
        logger.debug(f"Cached {key}")
    
    def clear(self) -> None:
        """Clear entire cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'ttl_seconds': self.ttl
        }

class ValidationHelper:
    """Helpers for validating code structures"""
    
    @staticmethod
    def is_valid_controller(content: str) -> bool:
        """Check if content is valid Spring controller"""
        return '@RestController' in content or '@Controller' in content
    
    @staticmethod
    def is_valid_service(content: str) -> bool:
        """Check if content is valid Spring service"""
        return '@Service' in content
    
    @staticmethod
    def has_endpoints(content: str) -> bool:
        """Check if controller has endpoint mappings"""
        mappings = [
            '@GetMapping',
            '@PostMapping',
            '@PutMapping',
            '@DeleteMapping',
            '@PatchMapping',
            '@RequestMapping'
        ]
        return any(mapping in content for mapping in mappings)
    
    @staticmethod
    def has_dependencies(content: str) -> bool:
        """Check if class has injected dependencies"""
        return '@Autowired' in content or '@Inject' in content or 'constructor' in content.lower()

def generate_summary_statistics(project_data: Dict) -> Dict:
    """Generate summary statistics from project analysis"""
    stats = {
        'analysis_timestamp': datetime.now().isoformat(),
        'project_name': project_data.get('project', 'Unknown'),
        'total_controllers': len(project_data.get('api_documentation', {})),
        'total_dependencies': len(project_data.get('dependency_mapping', {})),
        'configuration_items': len(project_data.get('configuration', {}))
    }
    
    return stats

def export_documentation(documentation: Dict, format: str = 'json', output_path: str = None) -> str:
    """Export documentation in various formats"""
    if output_path is None:
        output_path = f"./documentation.{format}"
    
    if format == 'json':
        with open(output_path, 'w') as f:
            json.dump(documentation, f, indent=2)
    
    elif format == 'markdown':
        markdown_content = "# Project Documentation\n\n"
        markdown_content += f"Generated: {datetime.now().isoformat()}\n\n"
        
        # Add sections for each component
        for key, value in documentation.items():
            markdown_content += f"## {key.replace('_', ' ').title()}\n\n"
            markdown_content += f"{json.dumps(value, indent=2)}\n\n"
        
        with open(output_path, 'w') as f:
            f.write(markdown_content)
    
    logger.info(f"Documentation exported to {output_path}")
    return output_path

# Example usage
if __name__ == "__main__":
    # Setup logging
    LoggingConfigurator.setup(level='DEBUG')
    
    # Load configuration
    config = ConfigManager('.env')
    if not config.validate():
        logger.error("Configuration validation failed")
        exit(1)
    
    # Create tracker
    tracker = PerformanceTracker()
    tracker.start("test_operation")
    
    # Simulate work
    import time
    time.sleep(0.5)
    
    tracker.end("test_operation")
    print(tracker.get_report())
    
    # Test metrics collector
    metrics = CodeMetricsCollector()
    metrics.add_file("test.java", "public class Test { public void method() {} }")
    print(metrics.get_summary())