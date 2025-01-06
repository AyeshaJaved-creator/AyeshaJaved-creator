from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
import os
import uvicorn

# Load environment variables from .env file
load_dotenv()

# Configure the Generative AI with the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini Pro model and initialize a chat session
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Function to send query to the Gemini model and retrieve a response
def get_gemini_response(question: str) -> str:
    """
    Sends a query to the Gemini API and retrieves the response text.
    
    Args:
        question (str): User's input question.
    
    Returns:
        str: The text response from the Gemini model.
    """
    try:
        # Strict medical-response prompt
        medical_prompt = (
            "You are a highly knowledgeable medical assistant. "
            "Answer the following question strictly with medically relevant information only. "
            "Avoid providing unrelated or generic information.\n\n"
            f"Question: {question}"
        )
        response = chat.send_message(medical_prompt, stream=False)

        # Extract the text content from the response object
        if response and response.candidates:
            # Access the first candidate's content directly
            text_response = response.candidates[0].content.parts[0].text
            return text_response.strip()
        else:
            return "No valid response received from the model."
    except Exception as e:
        return f"An error occurred while processing your query: {e}"

# FastAPI app initialization
app = FastAPI()

# Request model for the question input
class QuestionRequest(BaseModel):
    question: str

@app.post("/api/ask")
async def ask_question(request: QuestionRequest):
    """
    API endpoint that accepts a POST request with a health-related question.
    Returns a medically relevant response from the Gemini model.
    """
    user_question = request.question

    if not user_question:
        raise HTTPException(status_code=400, detail="Please provide a valid question.")

    response = get_gemini_response(user_question)

    return {"response": response}

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
