import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime

# Initialize Firebase Admin
# We expect a serviceAccountKey.json file or an environment variable with the JSON content
def initialize_firebase():
    try:
        # Check if app is already initialized
        firebase_admin.get_app()
    except ValueError:
        # Check for service account file
        cred_path = "serviceAccountKey.json"
        
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin initialized with serviceAccountKey.json")
        else:
            print("Warning: serviceAccountKey.json not found. Database writes will fail.")

def save_test_result(user_id: str, topic: str, difficulty: str, score: float, total_questions: int):
    """
    Saves a mock test result to Firestore and updates user aggregates.
    """
    # Ensure Firebase is initialized (Lazy load for robustness)
    try:
        firebase_admin.get_app()
    except ValueError:
        initialize_firebase()

    try:
        db = firestore.client()
        
        # 1. Save detailed activity
        activity_data = {
            "type": "mock_test",
            "topic": topic,
            "difficulty": difficulty,
            "score": score,
            "total_questions": total_questions,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "date_str": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        # Add to subcollection
        print(f"DEBUG: Saving Activity to users/{user_id}/activities")
        db.collection("users").document(user_id).collection("activities").add(activity_data)
        
        # 2. Update Aggregates (Profile)
        user_ref = db.collection("users").document(user_id)
        doc = user_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            current_total = data.get("totalTests", 0)
            current_avg = data.get("averageScore", 0)
            
            # Calculate new average
            new_total = current_total + 1
            new_avg = ((current_avg * current_total) + (score / total_questions * 100)) / new_total
            
            user_ref.update({
                "totalTests": new_total,
                "averageScore": new_avg,
                "lastActive": firestore.SERVER_TIMESTAMP
            })
        else:
            # Create new user profile if not exists
            user_ref.set({
                "totalTests": 1,
                "averageScore": (score / total_questions * 100),
                "interviewHours": 0,
                "streakDays": 1,
                "joinedAt": firestore.SERVER_TIMESTAMP
            })
        print("DEBUG: Successfully saved test result to Firestore")
    except Exception as e:
        print(f"CRITICAL ERROR Saving to Firestore: {e}")
        raise e

def save_interview_result(user_id: str, topic: str, difficulty: str, feedback: dict):
    """
    Saves an interview result. 
    Feedback is the JSON object from the AI evaluator.
    """
    # Ensure Firebase is initialized
    try:
        firebase_admin.get_app()
    except ValueError:
        initialize_firebase()

    try:
        db = firestore.client()
        overall_score = feedback.get("overall_score", 0)
        
        activity_data = {
            "type": "mock_interview",
            "topic": topic,
            "difficulty": difficulty,
            "score": overall_score,
            "feedback_summary": feedback.get("overall_feedback", "")[:200], # Store preview
            "timestamp": firestore.SERVER_TIMESTAMP,
            "date_str": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        print(f"DEBUG: Saving Interview to users/{user_id}/activities")
        db.collection("users").document(user_id).collection("activities").add(activity_data)
        
        # Update aggregates
        user_ref = db.collection("users").document(user_id)
        # Simple increment for now, logic can be expanded
        user_ref.update({
            "interviewCount": firestore.Increment(1),
            "lastActive": firestore.SERVER_TIMESTAMP
        })
        print("DEBUG: Successfully saved Interview result")
    except Exception as e:
        print(f"CRITICAL ERROR Saving Interview: {e}")
        raise e
