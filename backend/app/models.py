# from sqlalchemy import Column, Integer, String, Text, BigInteger, TIMESTAMP, ForeignKey, UniqueConstraint, func
# from app.database import Base
# from sqlalchemy.orm import relationship



# ### question model

# class Question(Base):
#     __tablename__ = "questions"

#     id = Column(Integer, primary_key=True, index=True)
#     category_id = Column(Integer, nullable=False, index=True)
#     category_name = Column(String(255), nullable=False)
#     sub_index = Column(Integer, nullable=False)
#     sub_name = Column(String(255))
#     question_text = Column(Text, nullable=False)
#     scale_min = Column(Integer, nullable=False, default=0)
#     scale_max = Column(Integer, nullable=False, default=5)
#     option_labels = Column(Text)           # raw "0 = None\n1 = …"
#     references_text = Column(Text)
#     source_links = Column(Text)

# class QuestionnaireMeta(Base):
#     __tablename__ = "questionnaire_meta"

#     id = Column(Integer, primary_key=True)  # always 1
#     title = Column(Text)
#     subtitle = Column(Text)


# ### answer model

# class ResponseSession(Base):
#     __tablename__ = "response_sessions"
#     id = Column(BigInteger, primary_key=True, index=True)
#     session_id = Column(String(64), unique=True, nullable=False, index=True)
#     respondent_ref = Column(String(255), nullable=True)
#     created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

# class Answer(Base):
#     __tablename__ = "answers"
#     id = Column(BigInteger, primary_key=True, index=True)
#     session_id = Column(String(64), nullable=False, index=True)
#     question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
#     value = Column(Integer, nullable=False)
#     created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

#     __table_args__ = (UniqueConstraint("session_id", "question_id", name="uq_session_question"),)



from sqlalchemy import Column, Integer, String, Text, BigInteger, TIMESTAMP, ForeignKey, UniqueConstraint, func
from app.database import Base
from sqlalchemy.orm import relationship


### question model

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, nullable=False, index=True)
    category_name = Column(String(255), nullable=False)
    sub_index = Column(Integer, nullable=False)
    sub_name = Column(String(255))
    question_text = Column(Text, nullable=False)
    scale_min = Column(Integer, nullable=False, default=0)
    scale_max = Column(Integer, nullable=False, default=5)
    option_labels = Column(Text)           # raw "0 = None\n1 = …"
    references_text = Column(Text)
    source_links = Column(Text)


class QuestionnaireMeta(Base):
    __tablename__ = "questionnaire_meta"

    id = Column(Integer, primary_key=True)  # always 1
    title = Column(Text)
    subtitle = Column(Text)


### answer/session models

class ResponseSession(Base):
    __tablename__ = "response_sessions"
    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    respondent_ref = Column(String(255), nullable=True)
    city_id = Column(String(32), nullable=False, index=True)  # <-- required
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


class Answer(Base):
    __tablename__ = "answers"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(String(64), nullable=False, index=True)
    city_id = Column(String(32), nullable=False, index=True)  # ✅ NEW: answers are per city
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    value = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # (session, city, question) must be unique
    __table_args__ = (
        UniqueConstraint("session_id", "city_id", "question_id", name="uq_session_city_question"),
    )
