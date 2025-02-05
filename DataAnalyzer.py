import pandas as pd
import google.generativeai as genai
import re  # Import regex module for cleaning numbering

# Set your Gemini API key
genai.configure(api_key="YOUR_GEMINI_API_KEY")

# Function to generate three key insights dynamically
def generate_three_key_insights(query, response_data):
    try:
        # Generate 3 key insights from the provided data
        insight_prompt = f"""
        Based on the following data, provide 3 key insights:
        Query: {query}
        Data:
        {response_data}
        """
        model = genai.GenerativeModel("gemini-1.5-flash")
        insights_response = model.generate_content(insight_prompt)

        # Extract the text from the response
        insights_text = insights_response.text.strip()

        # Remove any introductory lines and existing numbering using regex
        insights_cleaned = re.sub(r'(Based on.*?insights:|^\s*\d+[\.\)]\s*)', '', insights_text, flags=re.MULTILINE)

        # Split insights into a list, assuming each insight is on a new line
        insights_list = insights_cleaned.split("\n")

        # Filter out empty strings and generic text, limit to first 3 insights
        insights_list = [insight.strip() for insight in insights_list if insight.strip() and not insight.lower().startswith("based on")][:3]

        # If fewer than 3 insights are returned, pad with placeholder insights
        while len(insights_list) < 3:
            insights_list.append("No additional insight available.")

        return insights_list
    except Exception as e:
        return [f"Error generating insights: {e}"]

# Function to analyze distribution dynamically
def analyze_distribution(df, column, query):
    try:
        # Group data for distribution
        distribution = df[column].value_counts(dropna=False)
        total_count = len(df)
        percentage_distribution = (distribution / total_count) * 100

        # Prepare dynamic response with the distribution data
        response_data = f"""
        Total Records: {total_count}
        Distribution for {column}:
        {distribution.to_string()}

        Percentage Breakdown:
        {percentage_distribution.round(2).to_string()}
        """

        # Generate 3 key insights dynamically
        key_insights = generate_three_key_insights(query, response_data)

        # Format the response with clean numbering
        insights_summary = "\n".join([f"{i+1}. {insight}" for i, insight in enumerate(key_insights)])
        return f"Summary for {column}:\n{response_data}\n\nKey Insights:\n{insights_summary}"

    except Exception as e:
        return f"Error analyzing distribution for column '{column}': {e}"

# Function to dynamically identify relevant columns based on the query
def identify_relevant_column(df, query):
    # Convert query to lowercase for case-insensitive matching
    query = query.lower()

    # Define a mapping of keywords to potential column names
    keyword_to_columns = {
        "gender": ["sex", "gender"],  # Adjusted based on column name in dataset
        "chest pain": ["chestpain", "chestpain_type", "cp", "chest_pain"],
        "ecg": ["restingecg", "ecg", "resting_ecg"],
        "age": ["age"],
        "cholesterol": ["cholesterol", "chol"],
        "blood pressure": ["bloodpressure", "bp"],
    }

    # Debug: Print the available columns in the dataset
    print(f"Available columns in the dataset: {df.columns.tolist()}")

    # Iterate through the mapping to find a matching column
    for keyword, columns in keyword_to_columns.items():
        if keyword in query:
            for column in columns:
                # Print debug message for each column being checked
                print(f"Checking for column '{column}' in the dataset...")
                if column.lower() in [col.lower() for col in df.columns]:
                    print(f"Found matching column: {column}")
                    # Use the correct exact column name as found in the dataset
                    return [col for col in df.columns if column.lower() == col.lower()][0]
    return None

# Main function to process queries
def process_query(query, dataset_path="Path_To_Your_Dataset"):
    try:
        # Load the dataset from the local path
        file_df = pd.read_csv(dataset_path)

        # Check if dataset is loaded successfully
        if file_df.empty:
            return "Error: Dataset is empty or failed to load."

        # Dynamically identify relevant columns based on the query
        relevant_column = identify_relevant_column(file_df, query)

        if relevant_column:
            return analyze_distribution(file_df, relevant_column, query)
        else:
            return "Error: Could not detect a relevant column in the dataset based on your query."

    except Exception as e:
        return f"Error processing query: {e}"

# Example usage
if __name__ == "__main__":
    while True:
        user_query = input("Enter your query (or type 'exit' to quit): ")
        if user_query.lower() == 'exit':
            break
        result = process_query(user_query)
        print(result)
