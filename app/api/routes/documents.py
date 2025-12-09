import logging
import time

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.config.settings import get_db_service, get_embedding_service
from app.models.schemas import UploadResponse
from app.services.database_service import DatabaseService
from app.services.embedding_service import EmbeddingService
from app.utils.exceptions import handle_exception

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_endpoint(
    file: UploadFile,
    db_service: DatabaseService = Depends(get_db_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
):
    """Document upload endpoint"""
    try:
        start_time = time.time()

        # Read file content
        content_bytes = await file.read()
        text_content = content_bytes.decode("utf-8", errors="ignore")

        if not text_content.strip():
            raise HTTPException(status_code=400, detail="El archivo está vacío")

        # Generate embedding
        embedding = await embedding_service.get_embedding(text_content)
        if not embedding:
            raise HTTPException(status_code=500, detail="No se pudo generar el embedding")

        # Store in database
        doc = await db_service.create_document(
            filename=file.filename, content=text_content, embedding=embedding
        )

        processing_time = (time.time() - start_time) * 1000

        logger.info(f"Document uploaded successfully: {doc.id}")

        return {
            "message": "Documento procesado exitosamente",
            "document_id": doc.id,
            "filename": file.filename,
            "content_length": len(text_content),
            "processing_time_ms": processing_time,
        }

    except Exception as e:
        logger.error(f"Error in document upload: {e}")
        http_exc = handle_exception(e)
        return JSONResponse(status_code=http_exc.status_code, content={"detail": http_exc.detail})
