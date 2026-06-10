from fastapi import FastAPI
from database import Base, engine
from models import models

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Nube API"}