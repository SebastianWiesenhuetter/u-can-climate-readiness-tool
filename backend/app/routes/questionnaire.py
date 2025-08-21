from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from typing import List, Dict
from app.database import SessionLocal
from app import models, schemas
import re

router = APIRouter()

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper: parse "Scale" text like "0 = None\n1 = Past only\n..." -> list[{value,label}]
scale_line_re = re.compile(r"^\s*(\d+)\s*[:=]\s*(.+?)\s*$")

def parse_option_labels(raw: str):
    if not raw:
        return None
    lines = [l for l in str(raw).replace("\r\n", "\n").split("\n") if l.strip()]
    out = []
    for ln in lines:
        m = scale_line_re.match(ln)
        if m:
            out.append({"value": int(m.group(1)), "label": m.group(2)})
    return out or None


@router.get("/meta", response_model=schemas.MetaOut)
def get_meta(db: Session = Depends(get_db)):
    meta = db.get(models.QuestionnaireMeta, 1)
    if not meta:
        return {"title": None, "subtitle": None}
    return {"title": meta.title, "subtitle": meta.subtitle}


@router.get("/categories", response_model=List[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    rows = (
        db.query(
            models.Question.category_id.label("category_id"),
            models.Question.category_name.label("category_name"),
            func.count(models.Question.id).label("question_count"),
        )
        .group_by(models.Question.category_id, models.Question.category_name)
        .order_by(models.Question.category_id.asc())
        .all()
    )
    return [
        schemas.CategoryOut(
            category_id=r.category_id,
            category_name=r.category_name,
            question_count=r.question_count,
        )
        for r in rows
    ]


@router.get("/questions", response_model=List[schemas.QuestionOut])
def list_questions(
    grouped: bool = Query(False, description="If true, return grouped by category (different endpoint recommended)"),
    db: Session = Depends(get_db),
):
    # flat list (sorted)
    qs = (
        db.query(models.Question)
        .order_by(models.Question.category_id.asc(), models.Question.sub_index.asc())
        .all()
    )
    out = []
    for q in qs:
        opts = parse_option_labels(q.option_labels)
        out.append(
            schemas.QuestionOut(
                id=q.id,
                category_id=q.category_id,
                category_name=q.category_name,
                sub_index=q.sub_index,
                sub_name=q.sub_name,
                question_text=q.question_text,
                scale_min=q.scale_min,
                scale_max=q.scale_max,
                option_labels_raw=q.option_labels,
                option_labels=opts,
                references_text=q.references_text,
                source_links=q.source_links,
            )
        )
    return out


@router.get("/questions/by-category/{category_id}", response_model=schemas.GroupedCategory)
def list_questions_by_category(category_id: int, db: Session = Depends(get_db)):
    qs = (
        db.query(models.Question)
        .filter(models.Question.category_id == category_id)
        .order_by(models.Question.sub_index.asc())
        .all()
    )
    if not qs:
        raise HTTPException(status_code=404, detail="Category not found or no questions")
    cat_name = qs[0].category_name
    out = []
    for q in qs:
        out.append(
            schemas.QuestionOut(
                id=q.id,
                category_id=q.category_id,
                category_name=q.category_name,
                sub_index=q.sub_index,
                sub_name=q.sub_name,
                question_text=q.question_text,
                scale_min=q.scale_min,
                scale_max=q.scale_max,
                option_labels_raw=q.option_labels,
                option_labels=parse_option_labels(q.option_labels),
                references_text=q.references_text,
                source_links=q.source_links,
            )
        )
    return {"category_id": category_id, "category_name": cat_name, "questions": out}


@router.get("/questions/grouped", response_model=List[schemas.GroupedCategory])
def list_questions_grouped(db: Session = Depends(get_db)):
    # fetch once, then group in memory
    qs = (
        db.query(models.Question)
        .order_by(models.Question.category_id.asc(), models.Question.sub_index.asc())
        .all()
    )
    grouped = {}
    for q in qs:
        key = q.category_id
        if key not in grouped:
            grouped[key] = {
                "category_id": q.category_id,
                "category_name": q.category_name,
                "questions": [],
            }
        grouped[key]["questions"].append(
            schemas.QuestionOut(
                id=q.id,
                category_id=q.category_id,
                category_name=q.category_name,
                sub_index=q.sub_index,
                sub_name=q.sub_name,
                question_text=q.question_text,
                scale_min=q.scale_min,
                scale_max=q.scale_max,
                option_labels_raw=q.option_labels,
                option_labels=parse_option_labels(q.option_labels),
                references_text=q.references_text,
                source_links=q.source_links,
            )
        )
    return list(grouped.values())



