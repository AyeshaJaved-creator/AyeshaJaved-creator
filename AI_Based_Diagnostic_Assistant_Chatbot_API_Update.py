from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# FastAPI app initialization
app = FastAPI()

# Request models
class SymptomInfoRequest(BaseModel):
    name: str
    symptoms: str
    age: int

# Function to process the symptoms and provide a diagnosis (without fetching data)
def process_symptoms(symptoms: str) -> str:
    """
    Analyzes the symptoms provided and returns a diagnosis and treatment suggestion.
    """
    # Mock logic to simulate diagnosis based on symptoms
    if "fever" in symptoms.lower() and "headache" in symptoms.lower():
        return "Possible diagnosis: Influenza (Flu)\nTreatment: Rest, fluids, over-the-counter fever medications."
    elif "cough" in symptoms.lower() and "shortness of breath" in symptoms.lower():
        return "Possible diagnosis: COVID-19 or Respiratory infection\nTreatment: Seek medical advice for testing."
    elif "chest pain" in symptoms.lower() and "nausea" in symptoms.lower():
        return "Possible diagnosis: Heart attack\nTreatment: Seek immediate emergency medical attention."
    else:
        return "Symptoms unclear. Please consult a healthcare provider for a proper diagnosis."

# API endpoint for diagnosis based on user symptoms
@app.post("/api/get_diagnosis")
async def get_diagnosis(info: SymptomInfoRequest):
    """
    Endpoint to provide diagnosis based on user symptoms.
    """
    if not info.name or not info.symptoms or info.age <= 0:
        raise HTTPException(status_code=400, detail="Please provide valid name, symptoms, and age.")

    # Process the symptoms directly to get a diagnosis
    diagnosis = process_symptoms(info.symptoms)

    return {"name": info.name, "age": info.age, "diagnosis_and_treatment": diagnosis}

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
