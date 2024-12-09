import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import List
from datetime import datetime
import uvicorn

# データベース設定
DATABASE_URL = "sqlite:///../shirane/votes.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# データベースモデル
class Vote(Base):
    __tablename__ = "votes"
    sentence = Column(Integer, primary_key=True, index=True)
    score_one = Column(Integer, default=0)
    score_two = Column(Integer, default=0)
    score_thr = Column(Integer, default=0)
    score_fou = Column(Integer, default=0)
    score_fiv = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Pydanticモデル
class BulkVote(BaseModel):
    sentence_id: int
    score: List[int]

app = FastAPI()
if not os.path.exists("./ogg"):
    os.makedirs("./ogg")

# CORS-block avoiding
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

# データベースセッションの依存性
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Welcome to my World. This is HTMLrecorder"}
    

@app.get("/api")
async def apiroot():
    return {"message": "Welcome to my World. This is HC85."}


@app.post("/upload/{courpus}")
async def fileget(request: Request, courpus):
    form = await request.form()

    filename = {courpus}
    filename = str(list(filename)[0]) + ".ogg"  # ONLY filename pickup
    num = 1
    uploadedpath = "./ogg"
    files = os.listdir(uploadedpath)
    while filename in files:  # avoiding @overwrite
        filename = filename.rstrip(".ogg")
        number = "(" + str(num-1) + ")"
        filename = filename.rstrip(number)
        filename = filename + "(" + str(num) + ").ogg"
        num = num + 1

    for formdata in form:  # chunk & file writing
        uploadfile = form[formdata]
        path = os.path.join("./ogg", filename)
        fout = open(path, 'wb')
        while 1:
            chunk = await uploadfile.read(100000)
            if not chunk:
                break
            fout.write(chunk)
        fout.close()
    return {"status": "OK"}  # I hope return "200"



@app.post("/bulk_vote", status_code=201)
def record_bulk_vote(bulk_vote: BulkVote, db: Session = Depends(get_db)):
    sentence_id = bulk_vote.sentence_id
    scores = bulk_vote.score

    # スコアをカウント
    if len(scores) != 5 or any(score < 1 or score > 5 for score in scores):
        raise HTTPException(status_code=400, detail="Invalid score data")
    score_counts = [scores.count(i + 1) for i in range(5)]

    # データベースに保存
    new_vote = Vote(
        sentence=sentence_id,
        score_one=score_counts[0],
        score_two=score_counts[1],
        score_thr=score_counts[2],
        score_fou=score_counts[3],
        score_fiv=score_counts[4],
    )
    db.add(new_vote)
    db.commit()
    
    return {"message": f"{vote_count} votes recorded successfully", "total_votes": vote_count}

    
@app.get("/result/")
def get_results(db: Session = Depends(get_db)):
    results = db.query(Vote).all()
    formatted_results = [
        {
            "sentence_id": result.sentence_id,
            "score: 1": result.score_one,
            "score: 2": result.score_two,
            "score: 3": result.score_thr,
            "score: 4": result.score_fou,
            "score: 5": result.score_fiv
        }
        for result in results
    ]
    return {"results": formatted_results}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
