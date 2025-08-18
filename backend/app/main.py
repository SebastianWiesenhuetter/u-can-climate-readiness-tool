from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import questionnaire
from app.routes import answers


Base.metadata.create_all(bind=engine)

app = FastAPI(title="U_CAN Spider API")

# Allow your frontend during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(questionnaire.router, prefix="/api", tags=["Questionnaire"])


app.include_router(answers.router, prefix="/api", tags=["Answers"])