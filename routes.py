import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Body
from sqlalchemy.orm import Session
import models
from database import get_db
import gemini_service
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api")

class RenameSessionRequest(BaseModel):
    title: str

@router.get("/")
def read_root():
    return {"message": "Welcome to the AI Chat Assistant API!"}


@router.post("/chat")
async def chat(
        message: str = Form(...),
        session_id: Optional[int] = Form(None),
        file: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db)
):
    # Assume default user id=1
    user = db.query(models.User).filter(models.User.id == 1).first()
    if not user:
        user = models.User(id=1, username="default")
        db.add(user)
        db.commit()
        db.refresh(user)

    if session_id:
        session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == user.id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        # Create new session with title based on first message
        title = message[:30] + "..." if len(message) > 30 else message
        session = models.ChatSession(user_id=user.id, title=title)
        db.add(session)
        db.commit()
        db.refresh(session)

    # Load history for multi-turn context
    chats = db.query(models.ChatHistory).filter(models.ChatHistory.session_id == session.id).order_by(
        models.ChatHistory.timestamp).all()

    history_contents = []
    for h in chats:
        user_parts = []
        if h.document_path and h.document_mime_type:
            try:
                # Re-load the document bytes to pass to gemini history
                with open(h.document_path, "rb") as f:
                    doc_bytes = f.read()
                
                if "image" in h.document_mime_type:
                    user_parts.append(gemini_service.types.Part.from_bytes(data=doc_bytes, mime_type=h.document_mime_type))
                elif "pdf" in h.document_mime_type:
                    # For history, using from_bytes might trigger limits, but it's the simplest approach for now
                    # Ideally Google caching or URI uploads are used for large PDFs in history
                    pass # We will rely on get_gemini_response handling the current file. Passing previous PDFs in history is complex with the SDK without saving URIs permanently.
                    
            except Exception as e:
                print(f"Failed to load previous document {h.document_path}: {e}")
                
        user_parts.append({"text": h.message})
        
        history_contents.append({"role": "user", "parts": user_parts})
        history_contents.append({"role": "model", "parts": [{"text": h.response}]})

    file_bytes = None
    mime_type = None
    saved_file_path = None
    
    if file:
        # Basic validation: only accept images and pdfs for now
        if not ("image" in file.content_type or "pdf" in file.content_type):
            raise HTTPException(status_code=400, detail="Unsupported file type. Accepts images and PDFs.")
        file_bytes = await file.read()
        mime_type = file.content_type
        
        # Save file to disk
        ext = file.filename.split('.')[-1] if '.' in file.filename else ''
        filename = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
        saved_file_path = os.path.join("uploads", filename)
        
        with open(saved_file_path, "wb") as f:
            f.write(file_bytes)

    # Get response from Gemini
    try:
        response_text = gemini_service.get_gemini_response(history_contents, message, file_bytes, mime_type)
    except Exception as e:
        # Log and return user-friendly error
        print(f"Error calling gemini service: {e}")
        raise HTTPException(status_code=502, detail="Upstream model service error")

    # Save to database
    chat = models.ChatHistory(
        session_id=session.id,
        message=message,
        response=response_text,
        document_path=saved_file_path,
        document_mime_type=mime_type,
        timestamp=datetime.utcnow()
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)

    return {"response": response_text, "session_id": session.id}


@router.get("/sessions")
def get_sessions(db: Session = Depends(get_db)):
    sessions = db.query(models.ChatSession).filter(models.ChatSession.user_id == 1).order_by(models.ChatSession.created_at.desc()).all()
    return [{"id": s.id, "title": s.title, "created_at": s.created_at.isoformat()} for s in sessions]


@router.put("/sessions/{session_id}")
def rename_session(session_id: int, request: RenameSessionRequest, db: Session = Depends(get_db)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == 1).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session.title = request.title
    db.commit()
    return {"status": "renamed", "title": session.title}


@router.get("/history/{session_id}")
def get_session_history(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == 1).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    history = db.query(models.ChatHistory).filter(models.ChatHistory.session_id == session_id).order_by(models.ChatHistory.timestamp).all()
    
    results = []
    for h in history:
        has_doc = h.document_path is not None
        doc_name = os.path.basename(h.document_path) if has_doc else None
        results.append({
            "message": h.message, 
            "response": h.response, 
            "timestamp": h.timestamp.isoformat(),
            "has_document": has_doc,
            "document_name": doc_name
        })
    return results


@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == 1).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"status": "deleted"}


@router.delete("/history")
def clear_all_history(db: Session = Depends(get_db)):
    db.query(models.ChatSession).filter(models.ChatSession.user_id == 1).delete()
    db.commit()
    return {"status": "cleared"}