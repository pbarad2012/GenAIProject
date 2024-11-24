# Import necessary functions and libraries
from load_data import load_marketing_data, load_technical_data, load_open_api_key
from intent import process_query
import gradio as gr
import time

# Function to handle chatbot logic
def chatbot_interface(query, marketing_data_file, technical_data_file, state):
    """Gradio interface to interact with the query processing."""

    start_time = time.time()
    if state == None:
        state = {}

     # Load the Open API key for authentication
    load_open_api_key("Data_Sets\\key.json")


    if state.get("cancelled", False):
        return "Query processing has been cancelled."
    
    # Check if both files are uploaded
    if not marketing_data_file or not technical_data_file:
        return "Please upload both the marketing data (CSV) and technical data (DOCX) files."
    
    if 'conversation_history' not in list(state.keys()):
        state['conversation_history'] = []
   

    # Load marketing and technical data from the provided file paths
    if 'marketing_data' not in list(state.keys()):
        state['marketing_data'] = load_marketing_data(marketing_data_file)
    if 'technical_data' not in list(state.keys()):
        state['technical_data'] = load_technical_data(technical_data_file)

    # Process the query using the loaded data
    result = process_query(query, marketing_data_file, state['technical_data'],state)

    # Check the identified intent and return the appropriate response
    if result['Intent'].lower() == 'both':
        response = f"**Intent**: {result['Intent']}\n\n**Marketing Response**:\n{result['Marketing Response']}\n\n**Technical Response**:\n{result['Technical Response']}"
    elif result['Intent'].lower() == 'marketing':
        response = f"**Intent**: {result['Intent']}\n\n**Marketing Response**:\n{result['Marketing Response']}"
    elif result['Intent'].lower() == 'technical':
            response = f"**Intent**: {result['Intent']}\n\n**Technical Response**:\n{result['Technical Response']}"

    end_time = time.time()
    response_time = round(end_time - start_time, 2)
    response += f"\n\n**Response Time**: {response_time} seconds"
    state['conversation_history'].append(f"Query: {query}\nResponse: {response}")

        # Display the conversation history
    conversation = "\n\n".join(state['conversation_history'])

    return conversation


def cancel_query(state):
    """Handle cancellation by setting the cancelled flag in state."""
    if state == None:
        state = {}
    state["cancelled"] = True

# Gradio UI setup
with gr.Blocks() as block:
    gr.Markdown("# ChatBot with Marketing and Technical Query Processing")


    # File upload options for marketing and technical data
    marketing_file = gr.File(label="Upload Marketing Data (CSV)")
    technical_file = gr.File(label="Upload Technical Data (DOCX)")

    # Textbox for user input
    query_input = gr.Textbox(placeholder="Enter your query here...")

    # Output response display
    output = gr.Textbox(label="Response", interactive=False)

    # Submit button to process the query
    submit_button = gr.Button("Submit")
    cancel_button = gr.Button("Cancel")
    cancel_button.click(cancel_query, inputs=[gr.State()], outputs=[])
    submit_button.click(chatbot_interface, inputs=[query_input, marketing_file, technical_file, gr.State()], outputs=output)

# Launch the Gradio interface
block.launch(debug=True)
