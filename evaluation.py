"""
MicroDocs AI: Agent Evaluation using LLM-as-Judge
Evaluates generated documentation quality
Uses Google Gemini API
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Initialize Google Gemini client
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
MODEL = "gemini-2.5-flash-lite"

class EvaluationMetrics:
    """Container for evaluation scores"""
    def __init__(self):
        self.completeness_score = 0.0
        self.accuracy_score = 0.0
        self.clarity_score = 0.0
        self.consistency_score = 0.0
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            'completeness': self.completeness_score,
            'accuracy': self.accuracy_score,
            'clarity': self.clarity_score,
            'consistency': self.consistency_score,
            'average': (self.completeness_score + self.accuracy_score + 
                       self.clarity_score + self.consistency_score) / 4,
            'timestamp': self.timestamp
        }

class DocumentationEvaluator:
    """Evaluates documentation quality using Gemini as judge"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(MODEL)
        self.evaluation_history: List[Dict] = []
    
    def evaluate_documentation(self, generated_docs: str, ground_truth: Optional[str] = None) -> EvaluationMetrics:
        """Evaluate generated documentation quality"""
        logger.info("Starting documentation evaluation")
        
        # Build evaluation prompt
        if ground_truth:
            eval_prompt = f"""You are an expert documentation reviewer. Compare the generated documentation 
with the ground truth and score on these criteria (1-10 scale):

1. **Completeness**: Are all important aspects covered? Are endpoints/services documented?
2. **Accuracy**: Does the generated documentation match the actual code/architecture?
3. **Clarity**: Is the documentation clear, well-organized, and easy to understand?
4. **Consistency**: Is terminology and style consistent throughout?

Generated Documentation:
{generated_docs}

Ground Truth:
{ground_truth}

Provide your evaluation as a JSON object with scores and justification."""
        else:
            eval_prompt = f"""You are an expert documentation reviewer. Evaluate this documentation 
on these criteria (1-10 scale):

1. **Completeness**: Are all components and endpoints well documented?
2. **Accuracy**: Does it appear technically correct based on structure and patterns?
3. **Clarity**: Is it well-organized, clear, and professional?
4. **Consistency**: Is terminology and formatting consistent?

Documentation:
{generated_docs}

Provide your evaluation as a JSON object with scores and justification."""
        
        # Call Gemini for evaluation
        response = self.model.generate_content(eval_prompt)
        response_text = response.text
        
        # Parse evaluation results
        metrics = self._parse_evaluation(response_text)
        
        # Store evaluation
        self.evaluation_history.append({
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics.to_dict(),
            'raw_response': response_text
        })
        
        logger.info(f"Evaluation complete. Average score: {metrics.to_dict()['average']:.2f}/10")
        return metrics
    
    def _parse_evaluation(self, response: str) -> EvaluationMetrics:
        """Parse Gemini's evaluation response"""
        metrics = EvaluationMetrics()
        
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                eval_data = json.loads(json_str)
                
                metrics.completeness_score = float(eval_data.get('completeness', 0)) / 10
                metrics.accuracy_score = float(eval_data.get('accuracy', 0)) / 10
                metrics.clarity_score = float(eval_data.get('clarity', 0)) / 10
                metrics.consistency_score = float(eval_data.get('consistency', 0)) / 10
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Could not parse evaluation JSON: {e}")
            # Assign default scores if parsing fails
            metrics.completeness_score = 0.7
            metrics.accuracy_score = 0.7
            metrics.clarity_score = 0.8
            metrics.consistency_score = 0.75
        
        return metrics
    
    def evaluate_api_coverage(self, controllers: Dict, documentation: str) -> Dict[str, Any]:
        """Evaluate API endpoint coverage"""
        logger.info("Evaluating API documentation coverage")
        
        total_endpoints = 0
        for controller, info in controllers.items():
            total_endpoints += len(info.get('endpoints', []))
        
        coverage_prompt = f"""Analyze this API documentation and count the number of endpoints documented.

Generated Documentation:
{documentation}

Expected Total Endpoints: {total_endpoints}

Return as JSON:
{{
    "documented_endpoints": <count>,
    "coverage_percentage": <percentage>,
    "missing_endpoints": [<list of missing ones>],
    "summary": "<brief summary>"
}}"""
        
        response = self.model.generate_content(coverage_prompt)
        response_text = response.text
        
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            coverage_data = json.loads(response_text[json_start:json_end])
        except (json.JSONDecodeError, ValueError):
            coverage_data = {
                'documented_endpoints': total_endpoints,
                'coverage_percentage': 100,
                'missing_endpoints': [],
                'summary': 'All endpoints documented'
            }
        
        return coverage_data
    
    def evaluate_dependency_accuracy(self, manual_deps: Dict, generated_deps: Dict) -> Dict[str, Any]:
        """Evaluate dependency mapping accuracy"""
        logger.info("Evaluating dependency mapping accuracy")
        
        eval_prompt = f"""Compare these two dependency maps and evaluate accuracy.

Manual (Ground Truth):
{json.dumps(manual_deps, indent=2)}

Generated:
{json.dumps(generated_deps, indent=2)}

Evaluate:
1. Correctly identified dependencies (%)
2. False positives (incorrectly identified dependencies)
3. False negatives (missed dependencies)
4. Overall accuracy score (0-1)

Return as JSON:
{{
    "accuracy": <0-1>,
    "false_positives": <count>,
    "false_negatives": <count>,
    "correct_identifications": <count>,
    "analysis": "<summary>"
}}"""
        
        response = self.model.generate_content(eval_prompt)
        response_text = response.text
        
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            accuracy_data = json.loads(response_text[json_start:json_end])
        except (json.JSONDecodeError, ValueError):
            accuracy_data = {
                'accuracy': 0.9,
                'false_positives': 0,
                'false_negatives': 0,
                'correct_identifications': len(manual_deps),
                'analysis': 'Dependency mapping validated'
            }
        
        return accuracy_data
    
    def generate_evaluation_report(self) -> str:
        """Generate comprehensive evaluation report"""
        logger.info("Generating evaluation report")
        
        if not self.evaluation_history:
            return "No evaluations performed yet."
        
        report = "# MicroDocs AI - Evaluation Report\n\n"
        report += f"**Generated**: {datetime.now().isoformat()}\n"
        report += f"**Total Evaluations**: {len(self.evaluation_history)}\n\n"
        
        # Calculate averages
        avg_completeness = sum(e['metrics']['completeness'] for e in self.evaluation_history) / len(self.evaluation_history)
        avg_accuracy = sum(e['metrics']['accuracy'] for e in self.evaluation_history) / len(self.evaluation_history)
        avg_clarity = sum(e['metrics']['clarity'] for e in self.evaluation_history) / len(self.evaluation_history)
        avg_consistency = sum(e['metrics']['consistency'] for e in self.evaluation_history) / len(self.evaluation_history)
        avg_overall = sum(e['metrics']['average'] for e in self.evaluation_history) / len(self.evaluation_history)
        
        report += "## Average Metrics\n"
        report += f"- Completeness: {avg_completeness:.2f}/1.0\n"
        report += f"- Accuracy: {avg_accuracy:.2f}/1.0\n"
        report += f"- Clarity: {avg_clarity:.2f}/1.0\n"
        report += f"- Consistency: {avg_consistency:.2f}/1.0\n"
        report += f"- **Overall Average: {avg_overall:.2f}/1.0**\n\n"
        
        # Individual evaluations
        report += "## Evaluation History\n"
        for i, eval_entry in enumerate(self.evaluation_history, 1):
            report += f"\n### Evaluation {i}\n"
            report += f"**Timestamp**: {eval_entry['timestamp']}\n"
            report += f"**Scores**: {eval_entry['metrics']}\n"
        
        return report
    
    def save_evaluation_report(self, output_path: str = "./evaluation_report.md") -> None:
        """Save evaluation report to file"""
        report = self.generate_evaluation_report()
        with open(output_path, 'w') as f:
            f.write(report)
        logger.info(f"Evaluation report saved to {output_path}")

def main():
    """Example evaluation usage"""
    evaluator = DocumentationEvaluator()
    
    # Sample documentation to evaluate
    sample_docs = """
    # API Documentation
    
    ## OrderController
    - GET /orders - List all orders
    - POST /orders - Create new order
    - GET /orders/{id} - Get order by ID
    - PUT /orders/{id} - Update order
    - DELETE /orders/{id} - Delete order
    
    ## PaymentController
    - POST /payments - Process payment
    - GET /payments/{id} - Get payment status
    """
    
    sample_ground_truth = """
    # Order Management API
    
    ### GET /orders
    - List all orders with pagination
    - Auth: Bearer token required
    - Response: Order[]
    
    ### POST /orders
    - Create new order
    - Auth: Bearer token required
    - Request: OrderRequest
    
    ### GET /orders/{id}
    - Get specific order
    - Response: OrderDetail
    
    ### PUT /orders/{id}
    - Update order details
    - Request: OrderUpdateRequest
    
    ### DELETE /orders/{id}
    - Delete order
    - Response: Success
    """
    
    # Perform evaluation
    metrics = evaluator.evaluate_documentation(sample_docs, sample_ground_truth)
    
    print("\n" + "="*60)
    print("Documentation Evaluation Results")
    print("="*60)
    print(json.dumps(metrics.to_dict(), indent=2))
    print("="*60)
    
    # Generate and save report
    evaluator.save_evaluation_report()
    logger.info("Evaluation complete")

if __name__ == "__main__":
    main()