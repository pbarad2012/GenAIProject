# Import necessary agents and libraries
from Agents import marketing_agent, technical_agent  
import google.generativeai as genai  
from load_data import load_marketing_data 
import openai

# Initialize the Gemini model with the specific version.
model = genai.GenerativeModel('gemini-1.5-flash')


messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Configuration for the model's text generation parameters.
config={
    "max_output_tokens": 2048,
    "temperature": 0,
    "top_p": 1,
    "top_k": 32
}

def recognize_intent(query, marketing_data, technical_data):
    """Identify the query's intent and determine if it's related to marketing, technical, or both."""
    
    # Define the prompt for the AI to analyze the intent.
    prompt = f"""
        You are an intent recognition system. Below is data from two sources:

        Important : Recognize very fast amd return very fast.

        Marketing Data (CSV content): If the query relates to sales, dates, or values, the intent is Marketing. Example data:
        {marketing_data.head(2).to_string(index=False)}

        Technical Data (Error Codes from .docx): 
        If the query relates to error codes, issues, resolutions, or causes, the intent is Technical,diagnosed,resolved,
        questions like how to fixe, how to resolve , intent should be Technical only.
        example data : {technical_data[:1000]} 
        Query: {query}

        Determine if the query is related to Marketing, Technical, or Both. Return one of the following: ['Marketing', 'Technical', 'Both']
        """

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages + [{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()


def process_query(query, marketing_file_path, technical_data,state):
    """Recognize the query intent and route it to the appropriate agent(s) for a response."""
    
    if 'marketing_data' not in list(state.keys()):
        state['marketing_data'] = load_marketing_data(marketing_file_path)

    # Use the 'recognize_intent' function to determine the intent of the query.
    intent = recognize_intent(query, state['marketing_data'] , technical_data)
    print("intent value",intent)
    # Based on the detected intent, route the query to the appropriate agent(s).
    if "both" in intent.lower():
        # If the intent is "Both", get responses from both marketing and technical agents.
        marketing_response = marketing_agent(query, marketing_file_path)
        technical_response = technical_agent(query, technical_data)
        return {
            "Intent": "Both",
            "Marketing Response": marketing_response,
            "Technical Response": technical_response
        }
    
    elif "marketing" in intent.lower():
        # If the intent is "Marketing", get the response from the marketing agent only.
        return {
            "Intent": "Marketing",
            "Marketing Response": marketing_agent(query, marketing_file_path)
        }
    
    elif "technical" in intent.lower():
        # If the intent is "Technical", get the response from the technical agent only.
        return {
            "Intent": "Technical",
            "Technical Response": technical_agent(query, technical_data)
        }
    
    else:
        # If no intent could be determined, return an "Unknown" intent with a fallback message.
        return {
            "Intent": "Unknown",
            "Response": "Unable to determine the intent of your query. Please provide more details."
        }
