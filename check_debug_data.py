
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Explicitly load the service account file
cred_path = "serviceAccountKey.json"
if os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized successfully.")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        exit(1)
else:
    print(f"❌ '{cred_path}' not found!")
    exit(1)

db = firestore.client()

# The User ID we observed in the browser agent logs for hera123@gmail.com
USER_ID = "B5L6LZOSlbhAKkpV3BQc5fMiFqD3" 

print(f"\n--- Checking Data for User: {USER_ID} ---")

# 1. Check Profile
print("\n[Profile Data]")
user_ref = db.collection("users").document(USER_ID)
doc = user_ref.get()
if doc.exists:
    print(f"Account Exists: {doc.to_dict()}")
else:
    print("❌ No User Profile Document found.")

# 2. Check Activities
print("\n[Activities]")
activities_ref = user_ref.collection("activities")
docs = activities_ref.stream()
count = 0
for d in docs:
    print(f"- Activity {d.id}: {d.to_dict()}")
    count += 1

if count == 0:
    print("❌ No activities found for this user.")
else:
    print(f"✅ Found {count} activities.")
