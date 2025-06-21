import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, Tool, create_openai_functions_agent
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import psycopg2

load_dotenv()
# GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
# os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",  
# )

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

llm = ChatOpenAI(
    model="gpt-4o-mini",  
)


DB_NAME = 'mydatabase'
DB_USER = 'postgres'
DB_PASSWORD = '1234'
DB_HOST = 'localhost'
DB_PORT = '5432'

def generate_sql(query: str) -> str:
    """Generates an SQL query based on the user's request."""
    messages = [
        SystemMessage(content="You are an expert SQL assistant. You can only generate SQL queries and nothing else. Do not answer any other questions."),
        HumanMessage(content=f"""
        Generate an optimized SQL query for the following request:
        "{query}"

        Use the following schema for PostgresSql Database:

        - customers (customer_id, first_name, last_name, email, phone)
        - products (product_id, transaction_id, date, product_category, product_name, units_sold, unit_price, total_revenue, region, payment_method)
        - sales (sale_id, customer_id, product_id, amount, sale_date)

        Relationships:
        - sales.customer_id -> customers.customer_id
        - sales.product_id -> products.product_id

        Query Requirements:
        - If retrieving data from a single table, include **all columns** from that table.
        - Always include `customers.first_name` and `customers.last_name` for customer-related queries.
        - Always include `products.name`, `products.price`, and `products.category` for product-related queries.
        - Ensure the SQL query is correctly formatted and optimized for execution.
        - Return **only the SQL query** without any explanation or additional text.
    """)]

    response = llm.invoke(messages)
    return response.content.strip()


def execute_query(sql_query: str) -> list:
    """Executes the SQL query and returns the result."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        return [str(e)]

def generate_insights(data: list) -> str:
    """Generates insights based on the executed query results."""
    messages = [
        SystemMessage(content="You are a data analysis and Summary and Key Insights assistant."),
        HumanMessage(content=f"""
        Analyze the following data and generate key insights:

        Data: {data}

        Provide a short summary with actionable insights. For example, if sales are low for certain products, suggest a possible action like giving a discount on them.
        """),
    ]
    
    response = llm.invoke(messages)
    return response.content.strip()

tools = [
    Tool(name="generate_sql", func=generate_sql, description="Generates an optimized SQL query based on the user's request."),
    Tool(name="execute_query", func=execute_query, description="Executes the SQL query and returns the result."),
    Tool(name="generate_insights", func=generate_insights, description="Generates insights based on the executed query results.")
]

prompt_template = """
You are an expert SQL query master  generator who has deep knwoledge of the database and tables provide and a capable maths expert too . Your task is to generate an optimized SQL query based on the user's request. 
And then execute those query to retrive the result.Try to provide only the necessary columns and see if thhere is duplicate value in a columns for all row don't proivde them  ,Atfer that provide teh data analysis.

if(stricly when a message is a greeting message then only):
    if got any greeting message please greet and ask how can i help you? or I'm an sql query agent to help you for getting your desire query answer without any sql query writing.

- customers (customer_id, first_name, last_name, email, phone)
- products (product_id, transaction_id, date, product_category, product_name, units_sold, unit_price, total_revenue, region, payment_method)
- sales (sale_id, customer_id, product_id, amount, sale_date)

Relationships:
- sales.customer_id -> customers.customer_id
- sales.product_id -> products.product_id

Query Requirements:
- If retrieving data from a single table, include **all columns** from that table.
- Always include `customers.first_name` and `customers.last_name` for customer-related queries.
- Always include `products.name`, `products.price`, and `products.category` for product-related queries.
- Ensure the SQL query is correctly formatted and optimized for execution.

try not to provide sql query in your output but provide the sql query result  in a table format after executing the query

Query:
{query}

{agent_scratchpad}




"""

prompt = PromptTemplate(input_variables=["query","agent_scratchpad"], template=prompt_template)

agent = create_openai_functions_agent(llm, prompt=prompt, tools=tools)

agent_executor = AgentExecutor(
    agent=agent,  
    tools=tools, 
    verbose=True    
)

def process_query(user_query: str):
    """Processes the user query using the agent."""
    response = agent_executor.invoke({"query": user_query})

    if isinstance(response, dict) and "output" in response:
        result = response["output"]
        
       
                    
        return f"{result}"
    
    return "Error: Could not generate SQL query."

if __name__ == "__main__":
    user_query = input("Enter the query:")
    response = process_query(user_query)
    print(response)
