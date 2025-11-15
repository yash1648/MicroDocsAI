#!/usr/bin/env python3
"""
MicroDocs AI: Context-Aware Documentation Generator for Spring Boot Microservices
Main orchestrator agent coordinating specialized documentation agents
Uses Google Gemini API
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Google Gemini client
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
MODEL = "gemini-2.5-flash-lite"

class DocumentationSession:
    """Manages documentation generation sessions"""
    def __init__(self, user_id: str, project_name: str):
        self.session_id = f"{user_id}_{project_name}_{datetime.now().timestamp()}"
        self.user_id = user_id
        self.project_name = project_name
        self.created_at = datetime.now()
        self.state = "initialized"
        self.memory: Dict[str, Any] = {}
        self.results = {}
    
    def save_result(self, agent_name: str, result: Any):
        """Store agent results"""
        self.results[agent_name] = result
        logger.info(f"Saved result from {agent_name}")
    
    def get_context(self) -> str:
        """Build context from previous results"""
        context = f"Session: {self.session_id}\nProject: {self.project_name}\n"
        for agent, result in self.results.items():
            context += f"\n{agent} Results:\n{json.dumps(result, indent=2)}\n"
        return context

class SpringAnalyzer:
    """Analyzes Spring Boot source code"""
    
    @staticmethod
    def extract_controllers(project_path: str) -> Dict[str, Any]:
        """Extract REST controllers from project"""
        logger.info(f"Analyzing Spring controllers in {project_path}")
        controllers = {}
        
        for root, dirs, files in os.walk(project_path):
            # Skip non-source directories
            dirs[:] = [d for d in dirs if d not in ['target', 'build', '.git']]
            
            for file in files:
                if file.endswith('Controller.java'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Parse controller annotations
                        controller_info = {
                            'path': file_path,
                            'class_name': file.replace('.java', ''),
                            'endpoints': SpringAnalyzer._parse_endpoints(content),
                            'base_path': SpringAnalyzer._extract_base_path(content)
                        }
                        controllers[file] = controller_info
                    except Exception as e:
                        logger.error(f"Error parsing {file}: {e}")
        
        return controllers
    
    @staticmethod
    def _parse_endpoints(content: str) -> List[Dict]:
        """Extract endpoint definitions"""
        endpoints = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if '@GetMapping' in line or '@PostMapping' in line or '@PutMapping' in line or '@DeleteMapping' in line:
                method_type = line.split('@')[1].split('(')[0]
                path = line.split('value="')[1].split('"')[0] if 'value="' in line else '/'
                # Get method name from next few lines
                for j in range(i+1, min(i+5, len(lines))):
                    if 'public' in lines[j]:
                        method_name = lines[j].split('(')[0].split()[-1]
                        endpoints.append({
                            'method': method_type.replace('Mapping', '').upper(),
                            'path': path,
                            'handler': method_name
                        })
                        break
        
        return endpoints
    
    @staticmethod
    def _extract_base_path(content: str) -> str:
        """Extract base RequestMapping path"""
        for line in content.split('\n'):
            if '@RequestMapping' in line and 'class' not in line:
                if 'value="' in line:
                    return line.split('value="')[1].split('"')[0]
        return ''
    
    @staticmethod
    def extract_dependencies(project_path: str) -> Dict[str, List[str]]:
        """Extract service dependencies"""
        logger.info(f"Mapping dependencies in {project_path}")
        dependencies = {}
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ['target', 'build', '.git']]
            
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Find @Autowired and constructor injection
                        deps = SpringAnalyzer._find_injections(content)
                        if deps:
                            dependencies[file] = deps
                    except Exception as e:
                        logger.error(f"Error parsing {file}: {e}")
        
        return dependencies
    
    @staticmethod
    def _find_injections(content: str) -> List[str]:
        """Find dependency injection patterns"""
        injections = []
        lines = content.split('\n')
        
        for line in lines:
            if '@Autowired' in line or '@Inject' in line:
                for next_line in lines:
                    if 'private' in next_line and ';' in next_line:
                        # Extract type name
                        parts = next_line.split()
                        if len(parts) >= 3:
                            injections.append(parts[1])
                        break
        
        return injections
    
    @staticmethod
    def parse_application_properties(project_path: str) -> Dict[str, str]:
        """Extract application configuration"""
        config = {}
        config_files = [
            'application.properties',
            'application.yml',
            'application.yaml'
        ]
        
        for root, dirs, files in os.walk(project_path):
            for config_file in config_files:
                if config_file in files:
                    file_path = os.path.join(root, config_file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                if '=' in line and not line.strip().startswith('#'):
                                    key, val = line.split('=', 1)
                                    config[key.strip()] = val.strip()
                    except Exception as e:
                        logger.error(f"Error parsing {config_file}: {e}")
        
        return config

class APIDocumentationAgent:
    """Generates OpenAPI documentation"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(MODEL)
    
    def generate_api_docs(self, controllers: Dict, session: DocumentationSession) -> Dict:
        """Generate OpenAPI specifications"""
        logger.info("API Documentation Agent: Starting")
        
        prompt = f"""Analyze these Spring Boot controllers and generate comprehensive API documentation:

{json.dumps(controllers, indent=2)}

For each controller, create:
1. Complete endpoint listing with HTTP methods and paths
2. Request/response schemas
3. Authentication requirements
4. Error codes and responses
5. Example curl commands

Format as structured JSON with OpenAPI 3.0 compatible schema."""

        response = self.model.generate_content(prompt)
        api_docs = response.text
        session.save_result("api_documentation_agent", api_docs)
        logger.info("API Documentation Agent: Complete")
        return {"agent": "api_docs", "output": api_docs}

class DependencyMapperAgent:
    """Maps service dependencies"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(MODEL)
    
    def generate_dependency_map(self, dependencies: Dict, session: DocumentationSession) -> Dict:
        """Generate dependency graphs and documentation"""
        logger.info("Dependency Mapper Agent: Starting")
        
        prompt = f"""Analyze these Spring Boot service dependencies and create comprehensive documentation:

{json.dumps(dependencies, indent=2)}

Generate:
1. Service dependency graph (Mermaid syntax)
2. Dependency analysis (incoming and outgoing)
3. Architecture patterns identified
4. Potential circular dependencies
5. Integration points documentation

Format as structured output with Mermaid diagrams and analysis."""

        response = self.model.generate_content(prompt)
        dep_map = response.text
        session.save_result("dependency_mapper_agent", dep_map)
        logger.info("Dependency Mapper Agent: Complete")
        return {"agent": "dependency_mapper", "output": dep_map}

class MemoryContextAgent:
    """Manages documentation history and context"""
    
    def __init__(self):
        self.memory_store = {}
    
    def store_documentation(self, session: DocumentationSession, docs: Dict) -> None:
        """Store documentation in memory"""
        logger.info(f"Memory Agent: Storing documentation for {session.session_id}")
        self.memory_store[session.session_id] = {
            "session_id": session.session_id,
            "project": session.project_name,
            "timestamp": datetime.now().isoformat(),
            "documentation": docs
        }
    
    def retrieve_context(self, session_id: str) -> Optional[Dict]:
        """Retrieve stored documentation context"""
        return self.memory_store.get(session_id)
    
    def generate_summary(self, session: DocumentationSession) -> str:
        """Create documentation summary"""
        logger.info("Memory Agent: Generating documentation summary")
        
        summary = f"""
# Documentation Summary for {session.project_name}

**Session ID**: {session.session_id}
**Generated**: {datetime.now().isoformat()}

## Results Overview
"""
        for agent, result in session.results.items():
            summary += f"\n### {agent}\n{str(result)[:500]}...\n"
        
        return summary

class OrchestratorAgent:
    """Main orchestrator coordinating all agents"""
    
    def __init__(self):
        self.api_agent = APIDocumentationAgent()
        self.dependency_agent = DependencyMapperAgent()
        self.memory_agent = MemoryContextAgent()
    
    def orchestrate(self, project_path: str, user_id: str = "developer_1") -> Dict:
        """Orchestrate documentation generation workflow"""
        logger.info(f"Orchestrator: Starting documentation for {project_path}")
        
        # Create session
        project_name = os.path.basename(project_path)
        session = DocumentationSession(user_id, project_name)
        session.state = "analyzing"
        
        # Step 1: Analyze Spring Boot project
        logger.info("Orchestrator: Analyzing Spring Boot project structure")
        controllers = SpringAnalyzer.extract_controllers(project_path)
        dependencies = SpringAnalyzer.extract_dependencies(project_path)
        config = SpringAnalyzer.parse_application_properties(project_path)
        
        session.memory['controllers'] = len(controllers)
        session.memory['dependencies'] = len(dependencies)
        
        # Step 2: Generate API documentation (parallel execution)
        logger.info("Orchestrator: Delegating to API Documentation Agent")
        api_result = self.api_agent.generate_api_docs(controllers, session)
        
        # Step 3: Generate dependency mapping (parallel execution)
        logger.info("Orchestrator: Delegating to Dependency Mapper Agent")
        dep_result = self.dependency_agent.generate_dependency_map(dependencies, session)
        
        # Step 4: Store in memory and generate summary
        logger.info("Orchestrator: Storing results and generating summary")
        final_docs = {
            "project": project_name,
            "api_documentation": api_result,
            "dependency_mapping": dep_result,
            "configuration": config,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        self.memory_agent.store_documentation(session, final_docs)
        summary = self.memory_agent.generate_summary(session)
        
        session.state = "complete"
        
        return {
            "session_id": session.session_id,
            "project": project_name,
            "status": "success",
            "summary": summary,
            "full_documentation": final_docs,
            "memory": session.memory
        }

def main():
    """Main entry point"""
    # Example usage with sample project
    sample_project_path = "./sample_project"
    
    # Create orchestrator
    orchestrator = OrchestratorAgent()
    
    # Run documentation generation
    result = orchestrator.orchestrate(sample_project_path)
    
    # Save results
    output_path = "./documentation_output.json"
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    logger.info(f"Documentation generated successfully. Output saved to {output_path}")
    print("\n" + "="*60)
    print(result['summary'])
    print("="*60)

if __name__ == "__main__":
    main()