from app.services.document.ocr import extract_text_from_image
from app.services.ai.summarizer import summarize_document
from app.services.ai.entity_extractor import extract_legal_entities
import PyPDF2

async def process_document(file_path: str, file_type: str):
    """Main document processing pipeline"""
    
    # 1. Extract text
    if file_type == "application/pdf":
        text = extract_text_from_pdf(file_path)
    else:  # image
        text = await extract_text_from_image(file_path)
    
    # 2. Summarize
    summary = await summarize_document(text)
    
    # 3. Extract entities
    entities = await extract_legal_entities(text)
    
    # 4. Store in vector DB
    # await store_embeddings(text, document_id)
    
    return {
        "text": text,
        "summary": summary,
        "entities": entities
    }