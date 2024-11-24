import pandas as pd
import sqlite3
from docx import Document 
import os
import google.generativeai as genai 
import json

# Function to upload CSV data to an SQLite database
def upload_csv_to_sqlite(csv_file_path, db_file_path):
    """Reads a CSV file and uploads its content to an SQLite database."""
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)
    
    # Connect to the SQLite database (or create one if it doesn't exist)
    conn = sqlite3.connect(db_file_path)
    
    # Upload the DataFrame to a table named "data_table" in the SQLite database
    df.to_sql("data_table", conn, if_exists="replace", index=False)
    
    # Print success message once the data is uploaded
    print(f"CSV data successfully uploaded to SQLite database: {db_file_path}")


# Function to load marketing data (CSV file)
def load_marketing_data(file_path):
    """Loads marketing data from a CSV file."""

    # Simply load and return the marketing data as a DataFrame
    return pd.read_csv(file_path)


# Function to load technical data (from a .docx file)
def load_technical_data(file_path):
    """Loads technical data (error codes) from a .docx file."""
    
    # Load the .docx file using the python-docx library
    doc = Document(file_path)

    
    # Extract text from each paragraph in the document and join them into a single string
    full_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    # Optionally clean up the text to remove irrelevant parts (like "Error Codes" header)
    full_text = full_text.replace("Error Codes", "").strip()
    
    # Return the cleaned-up text (you can later process this into structured error codes if needed)
    return full_text


# Function to load and set the Open API key from a JSON file
def load_open_api_key(json_file_path):
    """Loads the Open API key from a JSON file and sets it as an environment variable."""
    
    # Open the JSON file containing the API key
    with open(json_file_path, 'r') as f:
        data = json.load(f)
        
        # Get the API key from the JSON data
        api_key = data.get("OPENAI_API_KEY_Value")
        
        # Set the API key as an environment variable for further use
        os.environ["OPENAI_API_KEY_Value"] = api_key
        
        openai_api_key = data.get("OPENAI_API_KEY_Value")

        os.environ["OPENAI_API_KEY"] = openai_api_key
