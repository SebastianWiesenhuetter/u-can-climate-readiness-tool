# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from sqlalchemy import func
# from typing import List
# from app.database import SessionLocal
# from app import models, schemas

# router = APIRouter()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # Create/ensure a session record (idempotent)
# @router.post("/sessions", status_code=201)
# def ensure_session(payload: schemas.SessionCreate, db: Session = Depends(get_db)):
#     sess = db.query(models.ResponseSession).filter_by(session_id=payload.session_id).first()
#     if not sess:
#         sess = models.ResponseSession(session_id=payload.session_id, respondent_ref=payload.respondent_ref)
#         db.add(sess)
#         db.commit()
#     else:
#         # optionally update respondent_ref
#         if payload.respondent_ref and payload.respondent_ref != sess.respondent_ref:
#             sess.respondent_ref = payload.respondent_ref
#             db.commit()
#     return {"ok": True, "session_id": payload.session_id}

# # Upsert a single answer
# @router.post("/answers", response_model=schemas.AnswerOut)
# def submit_answer(payload: schemas.AnswerIn, db: Session = Depends(get_db)):
#     # ensure session exists
#     sess = db.query(models.ResponseSession).filter_by(session_id=payload.session_id).first()
#     if not sess:
#         sess = models.ResponseSession(session_id=payload.session_id)
#         db.add(sess)
#         db.commit()

#     # validate question exists
#     q = db.query(models.Question).get(payload.question_id)
#     if not q:
#         raise HTTPException(status_code=404, detail="Question not found")

#     # upsert logic: try find existing, else insert
#     existing = (
#         db.query(models.Answer)
#         .filter(models.Answer.session_id == payload.session_id,
#                 models.Answer.question_id == payload.question_id)
#         .first()
#     )
#     if existing:
#         existing.value = payload.value
#         db.commit()
#         db.refresh(existing)
#         return existing
#     else:
#         ans = models.Answer(session_id=payload.session_id, question_id=payload.question_id, value=payload.value)
#         db.add(ans)
#         db.commit()
#         db.refresh(ans)
#         return ans

# # Bulk submit (nice for end-of-page or end-of-survey save)
# @router.post("/answers/bulk")
# def submit_answers_bulk(payload: schemas.AnswersBulkIn, db: Session = Depends(get_db)):
#     # ensure session
#     sess = db.query(models.ResponseSession).filter_by(session_id=payload.session_id).first()
#     if not sess:
#         sess = models.ResponseSession(session_id=payload.session_id, respondent_ref=payload.respondent_ref)
#         db.add(sess)
#         db.commit()

#     # validate all questions
#     q_ids = [a.question_id for a in payload.answers]
#     existing_qs = {q.id for q in db.query(models.Question.id).filter(models.Question.id.in_(q_ids)).all()}
#     missing = [qid for qid in q_ids if qid not in existing_qs]
#     if missing:
#         raise HTTPException(status_code=404, detail=f"Unknown question_ids: {missing}")

#     # Upsert one by one (simple and clear for prototype)
#     for a in payload.answers:
#         existing = (
#             db.query(models.Answer)
#             .filter(models.Answer.session_id == payload.session_id,
#                     models.Answer.question_id == a.question_id)
#             .first()
#         )
#         if existing:
#             existing.value = a.value
#         else:
#             db.add(models.Answer(session_id=a.session_id, question_id=a.question_id, value=a.value))
#     db.commit()
#     return {"ok": True, "count": len(payload.answers)}

# # Per-session per-category averages (for spider)
# @router.get("/sessions/{session_id}/summary", response_model=schemas.SessionSummary)
# def get_session_summary(session_id: str, db: Session = Depends(get_db)):
#     # join answers -> questions, group by category
#     rows = (
#         db.query(
#             models.Question.category_id,
#             models.Question.category_name,
#             func.avg(models.Answer.value).label("avg_value"),
#             func.count(models.Answer.id).label("count"),
#         )
#         .join(models.Question, models.Question.id == models.Answer.question_id)
#         .filter(models.Answer.session_id == session_id)
#         .group_by(models.Question.category_id, models.Question.category_name)
#         .order_by(models.Question.category_id.asc())
#         .all()
#     )

#     result = [
#         schemas.CategoryAvg(
#             category_id=r.category_id,
#             category_name=r.category_name,
#             avg_value=float(r.avg_value),
#             count=r.count,
#         )
#         for r in rows
#     ]
#     return {"session_id": session_id, "per_category": result}


from fastapi import APIRouter, Depends, HTTPException, Query
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
# @router.post("/sessions", status_code=201)
# def ensure_session(payload: schemas.SessionCreate, db: Session = Depends(get_db)):
#     sess = db.query(models.ResponseSession).filter_by(session_id=payload.session_id).first()
#     if not sess:
#         sess = models.ResponseSession(session_id=payload.session_id, respondent_ref=payload.respondent_ref)
#         db.add(sess)
#         db.commit()
#     else:
#         # optionally update respondent_ref
#         if payload.respondent_ref and payload.respondent_ref != sess.respondent_ref:
#             sess.respondent_ref = payload.respondent_ref
#             db.commit()
#     return {"ok": True, "session_id": payload.session_id}

@router.post("/sessions", status_code=201)
def ensure_session(payload: schemas.SessionCreate, db: Session = Depends(get_db)):
    if not payload.session_id:
        raise HTTPException(status_code=400, detail="session_id required")

    sess = db.query(models.ResponseSession).filter_by(session_id=payload.session_id).first()

    if not sess:
        if not payload.city_id:
            raise HTTPException(status_code=400, detail="city_id required for new session")
        sess = models.ResponseSession(
            session_id=payload.session_id,
            respondent_ref=payload.respondent_ref,
            city_id=payload.city_id,
        )
        db.add(sess)
        db.commit()
        return {"ok": True, "session_id": payload.session_id, "city_id": sess.city_id}

    changed = False
    if payload.respondent_ref and payload.respondent_ref != sess.respondent_ref:
        sess.respondent_ref = payload.respondent_ref
        changed = True

    if payload.city_id and payload.city_id != sess.city_id:
        has_answers = db.query(models.Answer.id).filter_by(session_id=sess.session_id).first() is not None
        if has_answers:
            raise HTTPException(status_code=409, detail="City already set for session with answers")
        sess.city_id = payload.city_id
        changed = True

    if changed:
        db.commit()

    return {"ok": True, "session_id": payload.session_id, "city_id": sess.city_id}



# # Upsert a single answer  ✅ now includes city_id, and upserts by (session_id, city_id, question_id)
# @router.post("/answers", response_model=schemas.AnswerOut)
# def submit_answer(payload: schemas.AnswerIn, db: Session = Depends(get_db)):
#     # ensure session exists
#     sess = db.query(models.ResponseSession).filter_by(session_id=payload.session_id).first()
#     if not sess:
#         sess = models.ResponseSession(session_id=payload.session_id)
#         db.add(sess)
#         db.commit()

#     # validate question exists
#     q = db.get(models.Question, payload.question_id)
#     if not q:
#         raise HTTPException(status_code=404, detail="Question not found")

#     # upsert per (session, city, question)
#     existing = (
#         db.query(models.Answer)
#         .filter(
#             models.Answer.session_id == payload.session_id,
#             models.Answer.city_id == payload.city_id,
#             models.Answer.question_id == payload.question_id,
#         )
#         .first()
#     )
#     if existing:
#         existing.value = payload.value
#         db.commit()
#         db.refresh(existing)
#         return existing

#     ans = models.Answer(
#         session_id=payload.session_id,
#         city_id=payload.city_id,          # ✅ new
#         question_id=payload.question_id,
#         value=payload.value,
#     )
#     db.add(ans)
#     db.commit()
#     db.refresh(ans)
#     return ans


# # Bulk submit  ✅ carries payload.city_id (one city per batch)
# @router.post("/answers/bulk")
# def submit_answers_bulk(payload: schemas.AnswersBulkIn, db: Session = Depends(get_db)):
#     # ensure session
#     sess = db.query(models.ResponseSession).filter_by(session_id=payload.session_id).first()
#     if not sess:
#         sess = models.ResponseSession(session_id=payload.session_id, respondent_ref=payload.respondent_ref)
#         db.add(sess)
#         db.commit()

#     # validate questions
#     q_ids = [a.question_id for a in payload.answers]
#     if q_ids:
#         found = {
#             qid
#             for (qid,) in db.query(models.Question.id)
#                             .filter(models.Question.id.in_(q_ids))
#                             .all()
#         }
#         missing = [qid for qid in q_ids if qid not in found]
#         if missing:
#             raise HTTPException(status_code=404, detail=f"Unknown question_ids: {missing}")

#     # preload existing for this (session, city)
#     existing_by_qid = {
#         row.question_id: row
#         for row in db.query(models.Answer)
#                      .filter(
#                          models.Answer.session_id == payload.session_id,
#                          models.Answer.city_id == payload.city_id,  # ✅ new filter
#                      )
#     }

#     for a in payload.answers:
#         ex = existing_by_qid.get(a.question_id)
#         if ex:
#             ex.value = a.value
#         else:
#             db.add(models.Answer(
#                 session_id=payload.session_id,
#                 city_id=payload.city_id,     # ✅ new
#                 question_id=a.question_id,
#                 value=a.value,
#             ))
#     db.commit()
#     return {"ok": True, "count": len(payload.answers)}


@router.post("/answers", response_model=schemas.AnswerOut)
def submit_answer(payload: schemas.AnswerIn, db: Session = Depends(get_db)):
    sess = db.query(models.ResponseSession).filter_by(session_id=payload.session_id).first()
    if not sess or not sess.city_id:
        raise HTTPException(status_code=400, detail="Unknown session_id or city not set")

    q = db.get(models.Question, payload.question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

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
        ans = models.Answer(session_id=payload.session_id, question_id=payload.question_id, value=payload.value, city_id=sess.city_id)
        db.add(ans)
        db.commit()
        db.refresh(ans)
        return ans


@router.post("/answers/bulk")
def submit_answers_bulk(payload: schemas.AnswersBulkIn, db: Session = Depends(get_db)):
    sess = db.query(models.ResponseSession).filter_by(session_id=payload.session_id).first()
    if not sess or not sess.city_id:
        raise HTTPException(status_code=400, detail="Unknown session_id or city not set")

    q_ids = [a.question_id for a in payload.answers]
    existing_qs = {qid for (qid,) in db.query(models.Question.id).filter(models.Question.id.in_(q_ids)).all()}
    missing = [qid for qid in q_ids if qid not in existing_qs]
    if missing:
        raise HTTPException(status_code=404, detail=f"Unknown question_ids: {missing}")

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
            db.add(models.Answer(session_id=a.session_id, question_id=a.question_id, value=a.value, city_id=sess.city_id))
    db.commit()
    return {"ok": True, "count": len(payload.answers)}




# Per-session per-category averages (for spider)  ✅ filtered by city ######### this is not necessarily valid anymore? we should get the city_id from response_sessions - needs to be updated
## BUT ONLY NEED THIS - when we want to display individual sessions
@router.get("/sessions/{session_id}/summary", response_model=schemas.SessionSummary)
def get_session_summary(
    session_id: str,
    city: str = Query(..., min_length=1, description="City key to summarize"),  # ✅ new
    db: Session = Depends(get_db)
):
    rows = (
        db.query(
            models.Question.category_id,
            models.Question.category_name,
            func.avg(models.Answer.value).label("avg_value"),
            func.count(models.Answer.id).label("count"),
        )
        .join(models.Question, models.Question.id == models.Answer.question_id)
        .filter(
            models.Answer.session_id == session_id,
            models.Answer.city_id == city,  # ✅ only this city’s answers
        )
        .group_by(models.Question.category_id, models.Question.category_name)
        .order_by(models.Question.category_id.asc())
        .all()
    )

    result = [
        schemas.CategoryAvg(
            category_id=r.category_id,
            category_name=r.category_name,
            avg_value=float(r.avg_value) if r.avg_value is not None else 0.0,
            count=int(r.count or 0),
        )
        for r in rows
    ]
    return {"session_id": session_id, "per_category": result}


#######################
# # --- Analytics: per-city averages across ALL sessions (for radar) ---
# @router.get("/analytics/radar-all-cities")
# def radar_all_cities(db: Session = Depends(get_db)):
#     """
#     Returns:
#     {
#       "categories": ["Partnership networks", "…", ...],    # ordered by category_id
#       "cities": ["kyiv","lviv",...],                       # sorted
#       "series": [                                          # same order as cities[]
#         [3.2, 4.1, ...],                                   # city 0 per-category avgs
#         [2.8, 3.7, ...],                                   # city 1 …
#         ...
#       ]
#     }
#     """
#     # 1) fetch ordered categories (id -> name)
#     cats = (
#         db.query(models.Question.category_id, models.Question.category_name)
#           .group_by(models.Question.category_id, models.Question.category_name)
#           .order_by(models.Question.category_id.asc())
#           .all()
#     )
#     if not cats:
#         return {"categories": [], "cities": [], "series": []}

#     cat_ids = [c.category_id for c in cats]
#     cat_names = [c.category_name for c in cats]
#     cat_index = {cid: idx for idx, cid in enumerate(cat_ids)}

#     # 2) compute avg by (city_id, category_id) over ALL sessions
#     rows = (
#         db.query(
#             models.Answer.city_id,
#             models.Question.category_id,
#             func.avg(models.Answer.value).label("avg_value"),
#         )
#         .join(models.Question, models.Question.id == models.Answer.question_id)
#         .group_by(models.Answer.city_id, models.Question.category_id)
#         .all()
#     )

#     # 3) collect unique cities (stable order)
#     city_set = sorted({r.city_id for r in rows if r.city_id is not None})
#     # If you want to restrict to your 6 cities, replace city_set with a fixed list

#     # 4) pivot to matrix [cities][categories]
#     series = [[None] * len(cat_ids) for _ in range(len(city_set))]
#     for r in rows:
#         try:
#             ci = city_set.index(r.city_id)
#             kj = cat_index[r.category_id]
#             series[ci][kj] = float(r.avg_value) if r.avg_value is not None else None
#         except Exception:
#             pass

#     # Replace Nones with 0 (or leave Nones and let front-end skip)
#     series = [[(v if v is not None else 0.0) for v in row] for row in series]

#     return {
#         "categories": cat_names,
#         "cities": city_set,
#         "series": series,
#     }

##########################################################
# --- Analytics: per-city averages across ALL sessions (for radar) ---
@router.get("/analytics/radar-all-cities")
def radar_all_cities(db: Session = Depends(get_db)):
    """
    Returns:
    {
      "categories": [...],     # ordered by category_id
      "cities": ["kyiv","lviv",...],  # sorted
      "series": [ [..], [..], ... ]   # same order as cities[]
    }
    """
    # 1) categories (ordered)
    cats = (
        db.query(models.Question.category_id, models.Question.category_name)
          .group_by(models.Question.category_id, models.Question.category_name)
          .order_by(models.Question.category_id.asc())
          .all()
    )
    if not cats:
        return {"categories": [], "cities": [], "series": []}

    cat_ids   = [c.category_id for c in cats]
    cat_names = [c.category_name for c in cats]
    cat_index = {cid: idx for idx, cid in enumerate(cat_ids)}

    # 2) avg by (city_id, category_id) using session join
    rows = (
        db.query(
            models.ResponseSession.city_id,
            models.Question.category_id,
            func.avg(models.Answer.value).label("avg_value"),
        )
        .join(models.Answer, models.Answer.session_id == models.ResponseSession.session_id)
        .join(models.Question, models.Question.id == models.Answer.question_id)
        .group_by(models.ResponseSession.city_id, models.Question.category_id)
        .all()
    )

    # 3) unique cities
    city_list = sorted({r.city_id for r in rows if r.city_id})

    # 4) pivot to matrix
    series = [[0.0] * len(cat_ids) for _ in range(len(city_list))]
    for r in rows:
        ci = city_list.index(r.city_id)
        kj = cat_index[r.category_id]
        series[ci][kj] = float(r.avg_value) if r.avg_value is not None else 0.0

    return {"categories": cat_names, "cities": city_list, "series": series}

