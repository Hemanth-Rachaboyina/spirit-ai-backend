# pip install --upgrade openai
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import List
from Schema_and_prompts import MockTest, Mock_test_prompt

load_dotenv()


def generate_mock_test_questions(
    topic: str,
    difficulty: str = "Medium",
    model: str = "gpt-4o"
) -> List[dict]:
    """
    Generates interview-level mock test questions for a given topic and difficulty.

    Returns:
        List[dict]: List of questions ready to be consumed by frontend
    """

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    client = OpenAI(api_key=api_key)

    # dynamically insert difficulty into prompt
    formatted_prompt = Mock_test_prompt.format(difficulty=difficulty)

    completion = client.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": topic},
        ],
        response_format=MockTest,
    )

    mock_test: MockTest = completion.choices[0].message.parsed

    # Convert Pydantic models → plain dicts for frontend
    questions = [q.model_dump() for q in mock_test.questions]


    print("*"*50)
    for q in questions:
        print(q)
    print("*"*50)

    return questions



generate_mock_test_questions("React Js Developer")
