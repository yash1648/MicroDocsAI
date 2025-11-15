"""
MicroDocs AI: RAG Implementation with Vector Database
Enables semantic search across codebase documentation
Uses Google Gemini API
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Initialize Google Gemini client
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
MODEL = "gemini-2.5-flash-lite"

class Document:
    """Represents a document in the knowledge base"""
    def __init__(self, content: str, metadata: Dict[str, Any], doc_id: Optional[str] = None):
        self.content = content
        self.metadata = metadata
        self.doc_id = doc_id or f"doc_{datetime.now().timestamp()}"
        self.created_at = datetime.now()

class SimpleVectorStore:
    """In-memory vector store for RAG (simple implementation)"""
    
    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.model = genai.GenerativeModel(MODEL)
    
    def add_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add document to knowledge base"""
        doc = Document(content, metadata)
        self.documents[doc.doc_id] = doc
        logger.info(f"Added document: {doc.doc_id}")
        return doc.doc_id
    
    def search(self, query: str, top_k: int = 5) -> List[Document]:
        """Semantic search using LLM"""
        if not self.documents:
            logger.warning("No documents in knowledge base")
            return []
        
        # Build search context
        all_docs = "\n---\n".join([
            f"ID: {doc.doc_id}\nType: {doc.metadata.get('type', 'unknown')}\n"
            f"Path: {doc.metadata.get('path', 'N/A')}\n"
            f"Content: {doc.content[:300]}..."
            for doc in self.documents.values()
        ])
        
        # Use Gemini to find relevant documents
        search_prompt = f"""Given this query: "{query}"

Search through these documents and return the top {top_k} most relevant document IDs:

{all_docs}

Return only the document IDs as a JSON array, like: ["doc_123", "doc_456"]"""
        
        response = self.model.generate_content(search_prompt)
        response_text = response.text
        
        try:
            doc_ids = json.loads(response_text)
            return [self.documents[doc_id] for doc_id in doc_ids if doc_id in self.documents]
        except (json.JSONDecodeError, KeyError):
            logger.warning(f"Failed to parse search results: {response_text}")
            return list(self.documents.values())[:top_k]
    
    def list_documents(self, doc_type: Optional[str] = None) -> List[Document]:
        """List documents with optional filtering"""
        docs = list(self.documents.values())
        if doc_type:
            docs = [d for d in docs if d.metadata.get('type') == doc_type]
        return docs

class RAGQueryEngine:
    """RAG-powered query interface for architecture questions"""
    
    def __init__(self, vector_store: SimpleVectorStore):
        self.vector_store = vector_store
        self.model = genai.GenerativeModel(MODEL)
        self.query_history: List[Dict] = []
    
    def query(self, question: str, context_limit: int = 3) -> str:
        """Answer architecture questions using RAG"""
        logger.info(f"Processing query: {question}")
        
        # Retrieve relevant documents
        relevant_docs = self.vector_store.search(question, top_k=context_limit)
        
        if not relevant_docs:
            return "No relevant documentation found for your query."
        
        # Build context from retrieved documents
        context = "## Relevant Documentation\n\n"
        for doc in relevant_docs:
            context += f"### {doc.metadata.get('path', 'Unknown')}\n"
            context += f"Type: {doc.metadata.get('type', 'unknown')}\n"
            context += f"{doc.content}\n\n"
        
        # Generate answer using Gemini with RAG context
        rag_prompt = f"""Based on this microservices documentation, answer the question.

{context}

Question: {question}

Provide a clear, detailed answer based on the documentation context."""
        
        response = self.model.generate_content(rag_prompt)
        answer = response.text
        
        # Store query history
        self.query_history.append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "docs_used": [d.doc_id for d in relevant_docs]
        })
        
        return answer
    
    def get_query_history(self) -> List[Dict]:
        """Retrieve query history"""
        return self.query_history

def index_codebase(project_path: str, vector_store: SimpleVectorStore) -> None:
    """Index entire codebase into vector store"""
    logger.info(f"Indexing codebase: {project_path}")
    
    for root, dirs, files in os.walk(project_path):
        # Skip non-essential directories
        dirs[:] = [d for d in dirs if d not in ['target', 'build', '.git', '__pycache__', 'node_modules']]
        
        for file in files:
            if file.endswith(('.java', '.properties', '.yml', '.yaml', '.md')):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Determine document type
                    if file.endswith('Controller.java'):
                        doc_type = 'controller'
                    elif file.endswith('.java'):
                        doc_type = 'java_class'
                    elif file.endswith(('.properties', '.yml', '.yaml')):
                        doc_type = 'configuration'
                    elif file.endswith('.md'):
                        doc_type = 'documentation'
                    else:
                        doc_type = 'other'
                    
                    # Add to vector store
                    vector_store.add_document(
                        content=content,
                        metadata={
                            'path': rel_path,
                            'type': doc_type,
                            'indexed_at': datetime.now().isoformat()
                        }
                    )
                except Exception as e:
                    logger.error(f"Error indexing {file_path}: {e}")
    
    logger.info(f"Indexed {len(vector_store.documents)} documents")

def main():
    """Example RAG usage"""
    # Initialize vector store
    vector_store = SimpleVectorStore()
    
    # Index sample project
    sample_project_path = "./sample_project"
    if os.path.exists(sample_project_path):
        index_codebase(sample_project_path, vector_store)
    else:
        # Demo with sample documents
        vector_store.add_document(
            content="@RestController class OrderController { @GetMapping('/orders') public List<Order> getOrders() }",
            metadata={'path': 'OrderController.java', 'type': 'controller'}
        )
        vector_store.add_document(
            content="@Service class OrderService { @Autowired private PaymentClient paymentClient; }",
            metadata={'path': 'OrderService.java', 'type': 'java_class'}
        )
    
    # Initialize RAG query engine
    rag_engine = RAGQueryEngine(vector_store)
    
    # Example queries
    questions = [
        "How does authentication work in the Order service?",
        "Which services depend on the Payment API?",
        "Show me all endpoints that modify order data"
    ]
    
    print("\n" + "="*60)
    print("RAG Query Engine - Architecture Questions")
    print("="*60)
    
    for question in questions:
        print(f"\nQ: {question}")
        answer = rag_engine.query(question)
        print(f"A: {answer}\n")
    
    # Save query history
    history_path = "./query_history.json"
    with open(history_path, 'w') as f:
        json.dump(rag_engine.get_query_history(), f, indent=2)
    
    logger.info(f"Query history saved to {history_path}")

if __name__ == "__main__":
    main()