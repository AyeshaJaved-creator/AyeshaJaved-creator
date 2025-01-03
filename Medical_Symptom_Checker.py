import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os

# Load environment variables
load_dotenv()

# Configure the Generative AI with the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini Pro model and initialize a chat session
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Function to send query to the Gemini model and retrieve a response
def get_gemini_response(question):
    """
    Sends a query to the Gemini API and retrieves the response text.
    """
    try:
        response = chat.send_message(question, stream=False)
        if response and response.candidates:
            text_response = response.candidates[0].content.parts[0].text
            return text_response.strip()
        else:
            return "No valid response received from the model."
    except Exception as e:
        return f"An error occurred while processing your query: {e}"

# Streamlit App Front-End
def main():
    """
    Main function for the Streamlit app.
    """
    st.title("Medical Chatbot")

    if "step" not in st.session_state:
        st.session_state.step = 1

    if st.session_state.step == 1:
        st.write("Hello! I am your medical chatbot.")
        st.write("What's your name?")
        name = st.text_input("Enter your name:")
        if st.button("Submit Name") and name.strip():
            st.session_state.name = name.strip()
            st.session_state.step = 2

    elif st.session_state.step == 2:
        st.write(f"Hi {st.session_state.name}! What are your symptoms?")
        symptoms = st.text_area("Describe your symptoms:")
        if st.button("Submit Symptoms") and symptoms.strip():
            st.session_state.symptoms = symptoms.strip()
            st.session_state.step = 3

    elif st.session_state.step == 3:
        st.write("Thank you! What's your age?")
        age = st.number_input("Enter your age:", min_value=0, max_value=120, step=1)
        if st.button("Submit Age") and age > 0:
            st.session_state.age = age
            st.session_state.step = 4

    elif st.session_state.step == 4:
        questions = [
            "How long have you been experiencing these symptoms?",
            "Have you had any recent illnesses or infections?",
            "Are you taking any medications?",
            "Have you experienced these symptoms before?"
        ]

        if "question_index" not in st.session_state:
            st.session_state.question_index = 0
            st.session_state.answers = []

        current_question = questions[st.session_state.question_index]
        st.write(f"Question {st.session_state.question_index + 1} of {len(questions)}:")
        st.write(current_question)

        answer = st.text_input("Your answer:", key=f"answer_{st.session_state.question_index}")

        if st.button("Next Question"):
            if answer.strip():
                st.session_state.answers.append(answer.strip())
                st.session_state.question_index += 1

            if st.session_state.question_index >= len(questions):
                st.session_state.step = 5

    elif st.session_state.step == 5:
        st.write("Analyzing your information...")
        with st.spinner("Please wait..."):
            personalized_prompt = (
                f"Patient Details:\n"
                f"Name: {st.session_state.name}\n"
                f"Age: {st.session_state.age}\n"
                f"Symptoms: {st.session_state.symptoms}\n"
                f"Additional Questions and Answers: {st.session_state.answers}\n\n"
                "Based on the above information, provide a medically accurate diagnosis "
                "and suggest specific treatment options. Ensure the response is tailored to the details provided."
            )
            response = get_gemini_response(personalized_prompt)

            if response:
                st.success("Diagnosis and Treatment:")
                st.markdown(response)
            else:
                st.error("Failed to retrieve a valid response. Please try again.")
        st.session_state.step = 6

    elif st.session_state.step == 6:
        st.write("Thank you for using the Medical Chatbot. Stay healthy!")

# Run the app
if __name__ == "__main__":
    main()
