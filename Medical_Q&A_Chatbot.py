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

# Streamlit App Front-End
def main():
    """
    Main function for the Streamlit app.
    """
    st.title("Medical Chatbot")
    st.subheader("Ask me about your health concerns!")
    st.write("Enter your question below, and I'll provide a medically relevant response.")
    
    # Input box for user question
    user_question = st.text_input("Your question:")
    
    if st.button("Get Response"):
        if user_question.strip() == "":
            st.warning("Please enter a valid question.")
        else:
            with st.spinner("Processing your query..."):
                # Get the chatbot response
                response = get_gemini_response(user_question)
                st.success("Response:")
                st.write(response)

# Run the app
if __name__ == "__main__":
    main()
