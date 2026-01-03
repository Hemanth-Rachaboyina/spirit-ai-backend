from pydantic import BaseModel
from typing import List, Literal, Union, Optional

# ==========================================
# MOCK TEST SCHEMAS (EXISTING)
# ==========================================

class SingleChoiceQuestion(BaseModel):
    type: Literal["single_choice"]
    question: str
    options: List[str]
    answer: str

class MultiChoiceQuestion(BaseModel):
    type: Literal["multi_choice"]
    question: str
    options: List[str]
    answers: List[str]

class WrittenQuestion(BaseModel):
    type: Literal["written"]
    question: str

class CodeSnippetQuestion(BaseModel):
    type: Literal["code"]
    question: str
    code: str

Question = Union[
    SingleChoiceQuestion,
    MultiChoiceQuestion,
    WrittenQuestion,
    CodeSnippetQuestion
]

class MockTest(BaseModel):
    questions: List[Question]


# ==========================================
# INTERVIEW SPECIFIC SCHEMAS (NEW)
# ==========================================

class InterviewQuestion(BaseModel):
    id: int
    type: Literal["scenario", "technical", "opinion", "challenge"]
    question: str
    context: Optional[str] = None 

class InterviewSession(BaseModel):
    questions: List[InterviewQuestion]

class QuestionFeedback(BaseModel):
    question_id: int
    score: int
    feedback: str
    improved_answer: str
    verbal_analysis: str

class InterviewEvaluation(BaseModel):
    overall_score: int
    overall_feedback: str
    strengths: List[str]
    areas_for_improvement: List[str]
    question_feedbacks: List[QuestionFeedback]


# ==========================================
# PROMPTS
# ==========================================

Mock_test_prompt = """
    You are an interview mock test question generation expert.

    Your task is to generate an interview-level mock test based strictly on the given topic.
    The questions must accurately evaluate a candidate’s understanding, problem-solving ability,
    and real interview readiness for that topic.

    Rules:
    - You must generate exactly 15 questions per topic.
    - The test must include:
    - 7 multiple-choice questions (4 options, only 1 correct)
    - 3 multi-answer questions (4 options, more than 1 may be correct)
    - 2 written-answer questions (free text, no options)
    - 3 code-snippet-based questions (a code snippet with a question)

    - Questions must be relevant to real interview scenarios.
    - Difficulty should match the requested level: {difficulty}.
    - Stay strictly within the given topic.

    Difficulty Handling Rules (MANDATORY):
    - If user asks for Easy → generate Medium-level interview questions.
    - If user asks for Medium → generate Hard-level interview questions.
    - If user asks for Hard → generate Expert-level questions.
    - Never generate questions easier than real interview expectations.

    Output Rules (MANDATORY):
    - You MUST respond with valid JSON only.
    - The JSON MUST match the provided schemas exactly.
    """

Mock_interview_prompt = """
    You are an expert technical interviewer conducting a high-stakes interview.
    Your goal is to generate a realistic, challenging, and varied set of interview questions for a {topic} role.
    Target difficulty: {difficulty}.

    You must generate EXACTLY 10 questions efficiently distributed as follows:

    1. **Scenario Based (3 questions):**
       - Describe a specific real-world problem or situation relevant to the role.
       - Ask the candidate exactly what they would do, how they would debug, or how they would approach it.
       - Focus on problem-solving steps.

    2. **Core Technical (3 questions):**
       - Direct, deep technical questions checking fundamental knowledge.
       - Avoid "What is X?" questions. Ask "How does X work internally?" or "When to use X over Y?".

    3. **Opinion/Experience (2 questions):**
       - Ask for the candidate's opinion on a technology, pattern, or trade-off.
       - Example: "Do you prefer X or Y? Why?" or "What is your biggest criticism of [Framework]?"

    4. **Challenge/Strong Statement (2 questions):**
       - Make a slightly controversial or rigid statement about the technology.
       - Ask the user if they agree or disagree, and to justify their stance.
       - Example: "I firmly believe Unit Tests are a waste of time in startups. Do you agree? Why/Why not?"

    **Output Rules:**
    - Return ONLY valid JSON matching the `InterviewSession` schema.
    - `id` should be 1 to 10.
    - `type` must match the category.
    - `context` is optional but recommended for Scenario/Challenge types to set the scene.
"""

Interview_evaluation_prompt = """
    You are an expert senior interviewer evaluating a candidate's performance.
    You have been provided with the questions asked and the candidate's responses (transcribed from speech).

    Your task is to provide a comprehensive, constructive, and strict evaluation.

    **Evaluation Dimensions:**
    1. **Technical Accuracy:** Is the answer correct and deep?
    2. **Communication (Verbal):** Analyze the phrasing, confident terms vs weak terms, and clarity. 
    3. **Problem Solving:** Did they approach the scenario logically?

    **For Each Question:**
    - Provide a score (1-10).
    - Give specific feedback: "You mentioned X, but missed Y."
    - Provide a better/reference answer.
    - **Verbal Analysis:** specifically comment on how it sounded.

    **Overall:**
    - Give a total score (1-100).
    - detailed transcript summary.
    - Bullet points for strengths and improvements.

    **Input Data:**
    Topic: {topic}
    Difficulty: {difficulty}
    Questions & Answers:
    {qa_transcript}

    **Output Rules:**
    - Return ONLY valid JSON matching the `InterviewEvaluation` schema.
"""