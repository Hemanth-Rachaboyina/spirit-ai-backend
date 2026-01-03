from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
from Schema_and_prompts import (
    InterviewSession, 
    Mock_interview_prompt, 
    InterviewEvaluation, 
    Interview_evaluation_prompt
)
import json

load_dotenv()

def generate_interview_questions(
    topic: str,
    difficulty: str = "Medium",
    model: str = "gpt-4o"
) -> List[dict]:
    """
    Generates scenario-based and behavioural interview questions.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found")

    client = OpenAI(api_key=api_key)

    formatted_prompt = Mock_interview_prompt.format(topic=topic, difficulty=difficulty)

    completion = client.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": formatted_prompt},
        ],
        response_format=InterviewSession,
    )

    session: InterviewSession = completion.choices[0].message.parsed
    questions_list = [q.model_dump() for q in session.questions]
    print("\n" + "="*50)
    print(f"GENERATED INTERVIEW QUESTIONS FOR: {topic} ({difficulty})")
    print("="*50)
    print(json.dumps(questions_list, indent=2))
    print("="*50 + "\n")
    return questions_list


def evaluate_interview(
    topic: str,
    difficulty: str,
    qa_list: List[Dict[str, Any]], # List of {question_id, question_text, user_answer}
    model: str = "gpt-4o"
) -> Dict[str, Any]:
    """
    Evaluates the entire interview session.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    # Format transcript for the prompt
    transcript = ""
    for item in qa_list:
        transcript += f"\nQ{item.get('question_id')}: {item.get('question_text')}\n"
        transcript += f"Candidate Answer: {item.get('user_answer')}\n"
        transcript += "-" * 20

    formatted_prompt = Interview_evaluation_prompt.format(
        topic=topic,
        difficulty=difficulty,
        qa_transcript=transcript
    )

    completion = client.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": formatted_prompt},
        ],
        response_format=InterviewEvaluation,
    )

    evaluation: InterviewEvaluation = completion.choices[0].message.parsed
    return evaluation.model_dump()

if __name__ == "__main__":
    # Test generation
    print("Generating Interview Questions...")
    qs = generate_interview_questions("React Senior Developer", "Hard")
    print(json.dumps(qs, indent=2))
