import streamlit as st
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import os

# Initialize the summarization pipeline
summarizer = pipeline("summarization")

# Function to extract text from PDF files
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Function to extract text from web pages
def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return ' '.join([p.get_text() for p in soup.find_all('p')])

# Function to summarize text
def summarize_text(text, max_length=150):
    if len(text.split()) > max_length:
        return summarizer(text, max_length=max_length, min_length=50, do_sample=False)[0]['summary_text']
    else:
        return "The text is too short for summarization."

# Streamlit UI
def main():
    st.title("Document and Web Link Summarizer")
    st.write("Upload a document or provide a web link to extract and summarize content.")

    # File upload section
    uploaded_file = st.file_uploader("Upload a PDF or text file", type=["pdf", "txt"])
    url = st.text_input("Enter a web link")

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".pdf"):
            text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".txt"):
            text = uploaded_file.read().decode("utf-8")
        else:
            st.error("Unsupported file type.")
            return

        st.subheader("Extracted Text")
        st.text_area("Text", text, height=300)

        if st.button("Summarize Document"):
            summary = summarize_text(text)
            st.subheader("Summary")
            st.write(summary)

    if url:
        try:
            text = extract_text_from_url(url)
            st.subheader("Extracted Text from URL")
            st.text_area("Text", text, height=300)

            if st.button("Summarize URL"):
                summary = summarize_text(text)
                st.subheader("Summary")
                st.write(summary)
        except Exception as e:
            st.error(f"Failed to extract text from the URL: {e}")

if __name__ == "__main__":
    main()
