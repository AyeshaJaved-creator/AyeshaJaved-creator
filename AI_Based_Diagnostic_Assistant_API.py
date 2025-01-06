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

# FastAPI app initialization
app = FastAPI()

# Request models
class BasicInfoRequest(BaseModel):
    name: str
    symptoms: str
    age: int

class QuestionAnswersRequest(BaseModel):
    name: str
    symptoms: str
    age: int
    answers: list[str]

# Function to send query to the Gemini model and retrieve a response
# Function to send query to the Gemini model and retrieve a response
def get_gemini_response(question: str) -> str:
    """
    Sends a query to the Gemini API and retrieves the response text.
    """
    try:
        # Send the question to the chat session
        response = chat.send_message(question, stream=False)
        
        # Log the entire response for debugging
        print(f"Full response from Gemini model: {response}")

        # Ensure the response contains valid candidates and a proper structure
        if response and hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]  # Access the first candidate
            
            # Check if the candidate content is valid
            if hasattr(candidate, 'content') and isinstance(candidate.content, str):
                return candidate.content  # Return the valid content
            else:
                raise ValueError(f"Invalid response structure: Missing or malformed content. Response: {response}")
        else:
            raise ValueError(f"No valid response received from the model. Response: {response}")
    except Exception as e:
        # Log the error and return a detailed error message
        print(f"Error in get_gemini_response: {e}")
        return f"An error occurred while processing your query: {e}"


# API endpoint for basic information
@app.post("/api/submit_basic_info")
async def submit_basic_info(info: BasicInfoRequest):
    """
    Endpoint to submit basic information about the patient.
    """
    if not info.name or not info.symptoms or info.age <= 0:
        raise HTTPException(status_code=400, detail="Please provide valid name, symptoms, and age.")

    return {"message": "Basic information submitted successfully."}

# API endpoint for answering additional questions and generating the response
@app.post("/api/get_diagnosis")
async def get_diagnosis(info: QuestionAnswersRequest):
    """
    Endpoint to provide answers to additional questions and get a diagnosis.
    """
    if not info.name or not info.symptoms or info.age <= 0 or not info.answers:
        raise HTTPException(status_code=400, detail="Please provide valid information and answers to all questions.")

    # Construct personalized prompt for Gemini AI
    personalized_prompt = (
        f"Patient Details:\n"
        f"Name: {info.name}\n"
        f"Age: {info.age}\n"
        f"Symptoms: {info.symptoms}\n"
        f"Additional Questions and Answers: {info.answers}\n\n"
        "Based on the above information, provide a medically accurate diagnosis "
        "and suggest specific treatment options. Ensure the response is tailored to the details provided."
    )

    # Get AI response
    response = get_gemini_response(personalized_prompt)

    if not response:
        raise HTTPException(status_code=500, detail="Failed to retrieve a response. Please try again.")

    return {"diagnosis_and_treatment": response}

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
