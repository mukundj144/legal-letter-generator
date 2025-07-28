# Retrieval-Augmented Generation system logic
import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI  
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self):
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4-turbo-preview",  # Changed from model_name to model
            temperature=0.3
        )
        self.vector_store = None
        self.documents = []
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    def process_documents(self, sections: List[Dict[str, str]]):
        """Process and chunk legal documents"""
        all_chunks = []
        
        for section in sections:
            # Create chunks from section content
            chunks = self.text_splitter.split_text(section["content"])
            
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "content": chunk,
                    "section_title": section["section_title"],
                    "page_number": section["page_number"],
                    "chunk_id": f"{section['section_title']}_{i}"
                })
        
        self.documents = all_chunks
        logger.info(f"Processed {len(all_chunks)} document chunks")
        return all_chunks
    
    def create_vector_store(self):
        """Create FAISS vector store from documents"""
        if not self.documents:
            raise ValueError("No documents processed. Call process_documents first.")
        
        # Extract text content for embedding
        texts = [doc["content"] for doc in self.documents]
        
        # Generate embeddings
        embeddings = self.embeddings_model.encode(texts)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.vector_store = faiss.IndexFlatL2(dimension)
        self.vector_store.add(embeddings.astype('float32'))
        
        logger.info(f"Created FAISS vector store with {len(texts)} documents")
        
    def save_vector_store(self, path: str = "vector_store"):
        """Save vector store and documents to disk"""
        os.makedirs(path, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.vector_store, f"{path}/faiss_index")
        
        # Save documents
        with open(f"{path}/documents.pkl", "wb") as f:
            pickle.dump(self.documents, f)
            
        logger.info(f"Vector store saved to {path}")
    
    def load_vector_store(self, path: str = "vector_store"):
        """Load vector store and documents from disk"""
        try:
            # Load FAISS index
            self.vector_store = faiss.read_index(f"{path}/faiss_index")
            
            # Load documents
            with open(f"{path}/documents.pkl", "rb") as f:
                self.documents = pickle.load(f)
                
            logger.info(f"Vector store loaded from {path}")
            return True
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return False
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar documents"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        # Generate query embedding
        query_embedding = self.embeddings_model.encode([query])
        
        # Search similar documents
        distances, indices = self.vector_store.search(
            query_embedding.astype('float32'), k
        )
        
        # Return relevant documents
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc["similarity_score"] = float(distances[0][i])
                results.append(doc)
        
        return results
    
    def generate_response(self, query: str, context_docs: List[Dict]) -> str:
        """Generate response using LLM with context"""
        context = "\n\n".join([
            f"Section: {doc['section_title']}\nContent: {doc['content']}"
            for doc in context_docs
        ])
        
        prompt = f"""
        Based on the following legal context, provide a detailed response to the query.
        
        Legal Context:
        {context}
        
        Query: {query}
        
        Please provide a comprehensive legal analysis based on the provided context.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return "Error generating response"
