from load_data import upload_csv_to_sqlite
import pandas as pd
import sqlite3
import google.generativeai as genai
import openai
# Initialize the Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]


# Configuration for the AI model's generation behavior
config={
    "max_output_tokens": 2048,
    "temperature": 0,
    "top_p": 1,
    "top_k": 32
}


def marketing_agent(user_query, marketing_file_path):
    """Handles marketing queries using the content of the .csv file (uploaded to SQLite)."""
    
    # Upload the marketing CSV data to SQLite database
    db_file_path = 'database.db'
    upload_csv_to_sqlite(marketing_file_path, db_file_path)
    
    # Read the marketing data into a Pandas DataFrame
    df = pd.read_csv(marketing_file_path)
    
    # Extract the column names and first few rows (head data) from the DataFrame
    columns = df.columns.tolist()
    head_data = df.head().to_string(index=False)

    # Step 2: Generate SQL Query for the given user query
    generated_sql = generate_sql_query(user_query, "data_table", columns, head_data)
    
    print("Generated SQL Query:", generated_sql)  # Print the generated SQL query for debugging

    # Step 3: Execute the generated SQL query on the SQLite database
    result = execute_sql_query(db_file_path, generated_sql)
    
    if result.shape != (1, 1) and not isinstance(result, str):
        prompt = f""" 
        1. if response is not in single column then check if {result}, is as per {user_query} if not then do analysis on {result} and get the answer, 
            as per user_query compare multiple columns or find difference of values or calculate correlate  etc.
            when quetion asked about how ? with the explanation also give calculation if possible. 
            do not reply with code , only give answer and figures to justify the analysis.
        2. if response is none then use {df} and get proper answer for the same.
        after doing above analysis  provide proper answer only. do not ask for futher instructions. just give proper response.
        """

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages + [{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0
        )

        return response.choices[0].message.content.strip().lower()
    else:
        return result.values.flatten()[0]


def technical_agent(query, doc_content):
    """Handles technical queries using error code data from a .docx document."""

    # Construct the prompt for the Gemini model to answer technical queries
    prompt = f"""
        You are a technical support agent. Only respond to technical queries, and do not include marketing data.
        Important : give response very fast.
        Use the following error codes to answer the query:

        {doc_content}

        Query: {query}

        If the error code or relevant data is not found, return an appropriate message. Do not include random data from the internet.
        """

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages + [{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()


def generate_sql_query(user_query, data_table, columns, head_data):
    """Generates a valid SQL query based on the user's query and the given table data."""

    # Construct the prompt to generate a SQL query using the Gemini model
    prompt = f"""
        You are a marketing support agent. Only respond if the query is related to marketing.

        Based on the user query "{user_query}" and the table {data_table}, generate a valid SQL query. The table has the following columns: {', '.join(columns)}. Example: "total ad spend" should match the column "total_ad_spend".

        If a date is provided, convert it to 'yyyy-mm-dd' format.
        If a month is provided without a day, assume it spans from day 1 to the last day of that month.
        For a quarter, use the respective months (Q1 = Jan-Mar, Q2 = Apr-Jun, etc.).
        In query always write date in 'yyyy-mm-dd' format.
        If user_query is asking to compare or find difference of two or multiple columns then write subquery to achieve it.

        Here are the first few rows of the data:
        {head_data}

        Generate the SQL query based on the above rules.
        return only sql query without any syntax error.
        """

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages + [{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()


def execute_sql_query(db_file_path, sql_query):
    """Executes a SQL query on an SQLite database and returns the result."""
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file_path)
    try:
        # Clean the SQL query string to remove any unnecessary formatting
        clean_sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        # Execute the cleaned SQL query and fetch the result into a Pandas DataFrame
        result = pd.read_sql_query(clean_sql_query, conn)
        print(result)
        # Return the query result

        return result
        # if isinstance(result, str):
        #     return result
        # else:
        #     return result.values.flatten()[0]
    except Exception as e:
        # Return any error that occurs during query execution
        return str(e)
    finally:
        # Ensure the database connection is closed
        conn.close()
