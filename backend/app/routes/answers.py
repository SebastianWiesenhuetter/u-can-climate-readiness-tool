from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import SessionLocal
from app import models, schemas

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create/ensure a session record (idempotent)
@router.post("/sessions", status_code=201)
def ensure_session(payload: schemas.SessionCreate, db: Session = Depends(get_db)):
    sess = db.query(models.ResponseSession).filter_by(session_id=payload.session_id).first()
    if not sess:
        sess = models.ResponseSession(session_id=payload.session_id, respondent_ref=payload.respondent_ref)
        db.add(sess)
        db.commit()
    else:
        # optionally update respondent_ref
        if payload.respondent_ref and payload.respondent_ref != sess.respondent_ref:
            sess.respondent_ref = payload.respondent_ref
            db.commit()
    return {"ok": True, "session_id": payload.session_id}

# Upsert a single answer
@router.post("/answers", response_model=schemas.AnswerOut)
def submit_answer(payload: schemas.AnswerIn, db: Session = Depends(get_db)):
    # ensure session exists
    sess = db.query(models.ResponseSession).filter_by(session_id=payload.session_id).first()
    if not sess:
        sess = models.ResponseSession(session_id=payload.session_id)
        db.add(sess)
        db.commit()

    # validate question exists
    q = db.query(models.Question).get(payload.question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    # upsert logic: try find existing, else insert
    existing = (
        db.query(models.Answer)
        .filter(models.Answer.session_id == payload.session_id,
                models.Answer.question_id == payload.question_id)
        .first()
    )
    if existing:
        existing.value = payload.value
        db.commit()
        db.refresh(existing)
        return existing
    else:
        ans = models.Answer(session_id=payload.session_id, question_id=payload.question_id, value=payload.value)
        db.add(ans)
        db.commit()
        db.refresh(ans)
        return ans

# Bulk submit (nice for end-of-page or end-of-survey save)
@router.post("/answers/bulk")
def submit_answers_bulk(payload: schemas.AnswersBulkIn, db: Session = Depends(get_db)):
    # ensure session
    sess = db.query(models.ResponseSession).filter_by(session_id=payload.session_id).first()
    if not sess:
        sess = models.ResponseSession(session_id=payload.session_id, respondent_ref=payload.respondent_ref)
        db.add(sess)
        db.commit()

    # validate all questions
    q_ids = [a.question_id for a in payload.answers]
    existing_qs = {q.id for q in db.query(models.Question.id).filter(models.Question.id.in_(q_ids)).all()}
    missing = [qid for qid in q_ids if qid not in existing_qs]
    if missing:
        raise HTTPException(status_code=404, detail=f"Unknown question_ids: {missing}")

    # Upsert one by one (simple and clear for prototype)
    for a in payload.answers:
        existing = (
            db.query(models.Answer)
            .filter(models.Answer.session_id == payload.session_id,
                    models.Answer.question_id == a.question_id)
            .first()
        )
        if existing:
            existing.value = a.value
        else:
            db.add(models.Answer(session_id=a.session_id, question_id=a.question_id, value=a.value))
    db.commit()
    return {"ok": True, "count": len(payload.answers)}

# Per-session per-category averages (for spider)
@router.get("/sessions/{session_id}/summary", response_model=schemas.SessionSummary)
def get_session_summary(session_id: str, db: Session = Depends(get_db)):
    # join answers -> questions, group by category
    rows = (
        db.query(
            models.Question.category_id,
            models.Question.category_name,
            func.avg(models.Answer.value).label("avg_value"),
            func.count(models.Answer.id).label("count"),
        )
        .join(models.Question, models.Question.id == models.Answer.question_id)
        .filter(models.Answer.session_id == session_id)
        .group_by(models.Question.category_id, models.Question.category_name)
        .order_by(models.Question.category_id.asc())
        .all()
    )

    result = [
        schemas.CategoryAvg(
            category_id=r.category_id,
            category_name=r.category_name,
            avg_value=float(r.avg_value),
            count=r.count,
        )
        for r in rows
    ]
    return {"session_id": session_id, "per_category": result}
