from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

###### question schemas ######

class OptionLabel(BaseModel):
    value: int
    label: str

class QuestionOut(BaseModel):
    id: int
    category_id: int
    category_name: str
    sub_index: int
    sub_name: str | None = None
    question_text: str
    scale_min: int
    scale_max: int
    option_labels_raw: Optional[str] = None
    option_labels: Optional[List[OptionLabel]] = None
    references_text: Optional[str] = None
    source_links: Optional[str] = None

    class Config:
        from_attributes = True

class CategoryOut(BaseModel):
    category_id: int
    category_name: str
    question_count: int

class GroupedCategory(BaseModel):
    category_id: int
    category_name: str
    questions: List[QuestionOut]

class MetaOut(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None

###### answer schemas ######

class SessionCreate(BaseModel):
    session_id: str
    respondent_ref: Optional[str] = None

class AnswerIn(BaseModel):
    session_id: str = Field(..., description="Client-generated UUID")
    question_id: int
    value: int = Field(..., ge=0, le=5)

class AnswersBulkIn(BaseModel):
    session_id: str
    respondent_ref: Optional[str] = None
    answers: List[AnswerIn]

class AnswerOut(BaseModel):
    id: int
    session_id: str
    question_id: int
    value: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True

class CategoryAvg(BaseModel):
    category_id: int
    category_name: str
    avg_value: float
    count: int

class SessionSummary(BaseModel):
    session_id: str
    per_category: List[CategoryAvg]

