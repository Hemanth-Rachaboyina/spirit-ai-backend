
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Explicitly load the service account file
cred_path = "serviceAccountKey.json"
if os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized.")
    except ValueError:
        pass # Already initialized
else:
    print(f"❌ '{cred_path}' not found!")
    exit(1)

db = firestore.client()
USER_ID = "B5L6LZOSlbhAKkpV3BQc5fMiFqD3"

print(f"fixing stats for {USER_ID}...")

# 1. Get all activities (tests only for average score)
activities_ref = db.collection("users").document(USER_ID).collection("activities")
docs = activities_ref.stream()

total_score = 0
count = 0
all_activities = []

for d in docs:
    data = d.to_dict()
    all_activities.append(data)
    if data.get("type") == "mock_test":
        # Check if score is stored as raw or percentage?
        # The frontend stored it. 
        # If it was stored recently, it might be the wrong value?
        # The frontend sends 'percentage'.
        # Let's assume the score field coming from FE was correct (0-100).
        score = data.get("score", 0)
        total_score += score
        count += 1
        print(f"Found Test: Score {score}")

if count > 0:
    new_avg = total_score / count
    print(f"Calculated New Average: {new_avg} (from {count} tests)")
    
    # Update User Profile
    db.collection("users").document(USER_ID).update({
        "averageScore": new_avg,
        "totalTests": count
    })
    print("✅ User Profile Updated.")
else:
    print("No mock tests found to average.")
