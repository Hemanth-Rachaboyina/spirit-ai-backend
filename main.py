from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mock_test import generate_mock_test_questions
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for production (Vercel)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TopicRequest(BaseModel):
    topic: str
    difficulty: str = "Medium"

from mock_interview import generate_interview_questions, evaluate_interview
from typing import List, Dict, Any

class InterviewRequest(BaseModel):
    topic: str
    difficulty: str = "Medium"

class QAItem(BaseModel):
    question_id: int
    question_text: str
    user_answer: str

class EvaluationRequest(BaseModel):
    topic: str
    difficulty: str
    qa_list: List[QAItem]
    user_id: str = "anonymous" # Optional for backward compatibility

@app.post("/api/generate-mock-test")
async def generate_test(request: TopicRequest):
    try:
        print(f"Generating test for topic: {request.topic}, Difficulty: {request.difficulty}")
        questions = generate_mock_test_questions(request.topic, request.difficulty)
        return {"questions": questions}
    except Exception as e:
        print(f"Error generating test: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-interview")
async def generate_interview(request: InterviewRequest):
    try:
        print(f"Generating INTERVIEW for topic: {request.topic}, Difficulty: {request.difficulty}")
        questions = generate_interview_questions(request.topic, request.difficulty)
        return {"questions": questions}
    except Exception as e:
        print(f"Error generating interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluate-interview")
async def evaluate_interview_endpoint(request: EvaluationRequest):
    try:
        print(f"Evaluating Interview for topic: {request.topic}")
        # Convert Pydantic models to dicts
        qa_list_dicts = [item.dict() for item in request.qa_list]
        evaluation = evaluate_interview(request.topic, request.difficulty, qa_list_dicts)
        
        # Save to Firebase if user_id is provided
        if request.user_id and request.user_id != "anonymous":
            try:
                save_interview_result(request.user_id, request.topic, request.difficulty, evaluation)
            except Exception as e:
                print(f"Failed to save interview result: {e}")
                
        return evaluation
    except Exception as e:
        print(f"Error evaluating interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "AI Interview Simulator Backend is running"}

from firebase_utils import initialize_firebase, save_test_result, save_interview_result

# Initialize Firebase
initialize_firebase()

class TestSubmission(BaseModel):
    user_id: str
    topic: str
    difficulty: str
    score: float
    total_questions: int

@app.post("/api/submit-test")
async def submit_test(submission: TestSubmission):
    try:
        print(f"Saving test result for user: {submission.user_id}")
        save_test_result(
            submission.user_id, 
            submission.topic, 
            submission.difficulty, 
            submission.score, 
            submission.total_questions
        )
        return {"message": "Test result saved successfully"}
    except Exception as e:
        print(f"Error saving test result: {e}")
        # Don't fail the request if saving fails (graceful degradation)
        return {"message": "Failed to save result", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
