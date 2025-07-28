# Entry point for FastAPI app
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from dotenv import load_dotenv

from .models import CaseInput, CaseResponse, GeneratedLetter
from .database import connect_to_mongo, close_mongo_connection, save_case, get_case, get_all_cases
from .pdf_processor import PDFProcessor
from .rag_system import RAGSystem
from .letter_generator import LegalLetterGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize global variables
rag_system = None
letter_generator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    await initialize_rag_system()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Legal Letter Generator API",
    description="AI-powered legal letter generation system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def initialize_rag_system():
    """Initialize RAG system with legal documents"""
    global rag_system, letter_generator
    
    try:
        rag_system = RAGSystem()
        
        # Try to load existing vector store
        if not rag_system.load_vector_store():
            logger.info("Vector store not found. Processing PDF...")
            
            # Process legal PDF
            pdf_path = r"C:\Users\hp\Desktop\mukund work related\legal-letter-generator\backend\documents\legal-IPC.pdf"
            if not os.path.exists(pdf_path):
                logger.error(f"Legal PDF not found at {pdf_path}")
                return
            
            processor = PDFProcessor(pdf_path)
            sections = processor.extract_sections()
            processor.close()
            
            # Create vector store
            rag_system.process_documents(sections)
            rag_system.create_vector_store()
            rag_system.save_vector_store()
            
            logger.info("RAG system initialized successfully")
        
        letter_generator = LegalLetterGenerator(rag_system)
        
    except Exception as e:
        logger.error(f"Error initializing RAG system: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Legal Letter Generator API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "rag_system_ready": rag_system is not None,
        "letter_generator_ready": letter_generator is not None
    }

@app.post("/generate-letter", response_model=CaseResponse)
async def generate_letter(case_input: CaseInput):
    """Generate legal letter for a case"""
    
    if not rag_system or not letter_generator:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Convert input to dict
        case_data = case_input.dict()
        
        # Generate letter
        letter_data = letter_generator.generate_formal_letter(case_data)
        
        # Prepare data for database
        db_data = {
            **case_data,
            **letter_data
        }
        
        # Save to database
        case_id = await save_case(db_data)
        
        # Create response
        generated_letter = GeneratedLetter(
            case_id=case_id,
            case_title=case_input.case_title,
            formal_letter=letter_data["formal_letter"],
            legal_arguments=letter_data["legal_arguments"],
            supporting_sections=letter_data["supporting_sections"],
            created_at=db_data["created_at"]
        )
        
        return CaseResponse(
            success=True,
            message="Letter generated successfully",
            case_id=case_id,
            letter=generated_letter
        )
        
    except Exception as e:
        logger.error(f"Error generating letter: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/case/{case_id}")
async def get_case_details(case_id: str):
    """Get case details by ID"""
    try:
        case = await get_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        return case
    except Exception as e:
        logger.error(f"Error retrieving case: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cases")
async def list_all_cases():
    """Get all cases"""
    try:
        cases = await get_all_cases()
        return {"cases": cases}
    except Exception as e:
        logger.error(f"Error retrieving cases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export-pdf/{case_id}")
async def export_case_pdf(case_id: str):
    """Export case as PDF"""
    try:
        case = await get_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Format for PDF export
        formatted_html = letter_generator.format_letter_for_export(case, case)
        argument_html = letter_generator.format_arguments_for_export(case,case)
        
        return {
            "success": True,
            "case_title": case["case_title"],
            "formal_content": formatted_html,
            "arguments": argument_html
        }
        
    except Exception as e:
        logger.error(f"Error exporting PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
