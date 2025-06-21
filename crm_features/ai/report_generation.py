import os
import json
import psycopg2  # For PostgreSQL connection
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, Tool, create_openai_functions_agent
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import PromptTemplate
import matplotlib.pyplot as plt
import seaborn as sns

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")




weekly_sales = []
monthly_sales = []
yearly_sales = []

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

def fetch_sales_data(date_filter=None):
    """
    Fetches weekly, monthly, and yearly sales data from PostgreSQL and stores it in global variables.
    """
    global weekly_sales, monthly_sales, yearly_sales

    try:
        connection = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = connection.cursor()

        cursor.execute("""
            SELECT * FROM products
            WHERE EXTRACT(YEAR FROM Date) = 2024
            AND EXTRACT(WEEK FROM Date) = 6
            ORDER BY Date;
        """)
        weekly_sales = cursor.fetchall()
        print("Weekly Sales done")

        cursor.execute("""
            SELECT * FROM products
            WHERE TO_CHAR(Date, 'YYYY-MM') = '2024-06'
            ORDER BY Date;
        """)
        monthly_sales = cursor.fetchall()
        print("Monthly Sales done")


        cursor.execute("""
            SELECT * FROM products
            WHERE EXTRACT(YEAR FROM Date) = 2024
            ORDER BY Date;
        """)
        yearly_sales = cursor.fetchall()
        print("Yearly Sales done")


    except psycopg2.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        connection.close()

    return weekly_sales,monthly_sales,yearly_sales    


def generate_sales_report1():
    global weekly_sales, monthly_sales, yearly_sales  
    print(yearly_sales)


    messages = [
        SystemMessage(content="You are an expert Data analyst. You can create a full-fledged data analysis report. Do not answer any other questions."),
        HumanMessage(content=f"""
        Generate a comprehensive data analysis report based on the given sales data across different time periods: weekly, monthly, and yearly.
        {weekly_sales, monthly_sales, yearly_sales}
        
        **Requirements:**
        - Identify key trends and patterns in sales performance.
        - Highlight significant growth or decline across different periods.
        - Provide insights into category-wise, product-wise, and regional sales performance.
        - Summarize payment method preferences and customer purchasing behaviors.
        - Offer actionable recommendations for improving sales and optimizing business strategies.

        Ensure the report is structured with clear sections, including Overview, Key Metrics, Trends Analysis, Insights, and Recommendations. Do not include raw data samples.
    """)
    ]
    
    response = llm.invoke(messages)
    return response.content.strip()

def generate_sales_report2():
    """
    Generates a structured JSON sales analysis report using LLM.
    
    Args:
    - llm: Language model instance
    
    Returns:
    - JSON string containing structured sales insights
    """
    global weekly_sales, monthly_sales, yearly_sales 

    messages = [
        SystemMessage(content="You are an expert Data Analyst. Your task is to analyze sales data and generate structured insights in JSON format for visualization purposes. Do not include raw data samples."),
        HumanMessage(content=f"""
        Analyze the given sales data across different time periods (weekly, monthly, yearly) and provide key insights in JSON format.
        
        **Data:**
        - **Weekly Sales:** {weekly_sales}
        - **Monthly Sales:** {monthly_sales}
        - **Yearly Sales:** {yearly_sales}

        **Required JSON Structure:**
        ```json
        {{
            "weekly_sales_trends": {{
                "total_sales": <int>,
                "growth_rate": <float>,
                "sales_by_category": {{"category1": <int>, "category2": <int>}},
                "sales_by_region": {{"region1": <int>, "region2": <int>}}
            }},
            "monthly_sales_trends": {{
                "total_sales": <int>,
                "growth_rate": <float>,
                "sales_by_category": {{"category1": <int>, "category2": <int>}},
                "sales_by_region": {{"region1": <int>, "region2": <int>}}
            }},
            "yearly_sales_trends": {{
                "total_sales": <int>,
                "growth_rate": <float>,
                "sales_by_category": {{"category1": <int>, "category2": <int>}},
                "sales_by_region": {{"region1": <int>, "region2": <int>}}
            }}
        }}
        ```

        **Key Considerations:**
        - Extract important sales trends, including total revenue and growth rates.
        - Identify top-selling products and most profitable categories.
        - Provide regional sales distribution for better market understanding.
        - Ensure the JSON structure remains consistent for easy visualization.

        Only return the JSON response without additional explanations.
        """)
    ]

    response = llm.invoke(messages) 
    return response.content.strip() 


tools = [
    Tool(
        name="fetch_sales_data",
        func=lambda _: fetch_sales_data(),  
        description=("Fetches sales data for the last 7 days (weekly), current month (monthly), "
            "and current year (yearly) from the PostgreSQL database in a single execution. "
            "setting three global variable of sales data in the format: "
            "{'weekly_sales': [...], 'monthly_sales': [...], 'yearly_sales': [...]}.")
    ),
    Tool(
        name="analyze_sales_report_text",
        func=lambda _: generate_sales_report1(),
        description=(
            "Analyzes sales data for the last 7 days (weekly), current month (monthly), "
            "and current year (yearly) getting   and generates a structured sales report in text format using an LLM ."
        ),
    ),
    Tool(
        name="generate_sales_report_json",
        func=lambda _:generate_sales_report2(),
        description=(
            "Processes sales data for the last 7 days (weekly), current month (monthly), and current year (yearly) "
            "and generates graph data points in JSON format using an LLM."
        ),
    ),
]

prompt_template = """
You are a sales forecasting expert with deep expertise in data analysis and trend identification. 
Your objective is to systematically analyze sales data and produce both structured visualizations and actionable insights.

### Mandatory Tool Usage Sequence:
1. fetch_sales_data (REQUIRED)
2. generate_sales_report_json (REQUIRED)
3. analyze_sales_report_text (REQUIRED)

### Strict Execution Flow:
1. **Data Retrieval Phase**:
   - Immediately invoke `fetch_sales_data` to get raw sales records
   - Validate data structure matches:
     ```python
     {{
         'weekly_sales': [timeframe, revenue, units],
         'monthly_sales': [period, revenue, growth_rate],
         'yearly_sales': [year, revenue, avg_monthly]
     }}
     ```

2. **Visualization Preparation Phase**:
   - Process raw data with `generate_sales_report_json` to create:
     - Time-series trends
     - Comparative period analyses
     - Revenue distribution charts
   - Ensure JSON output contains visualization-ready datapoints

3. **Insight Generation Phase**:
   - Feed JSON data to `analyze_sales_report_text` to produce:
     - Key performance highlights
     - Anomaly detection
     - Predictive insights
     - Actionable recommendations

This is a follow when you worked perfectly.    
responded: Okay, I understand. I will follow the prescribed sequence of tool usage to analyze the sales data, generate visualizations, and provide actionable insights.

Here's the plan:

1.  **Data Retrieval Phase:** I will start by calling the `fetch_sales_data` function to retrieve the sales data for the last 7 days (weekly), current month (monthly), and current year (yearly).
2.  **Visualization Preparation Phase:** Once I have the sales data, I will call the `generate_sales_report_json` function to process the data and generate graph data points in JSON format.
3.  **Insight Generation Phase:** After generating the JSON data, I will call the `analyze_sales_report_text` function to analyze the sales data and generate a structured sales report in text format.
4.  **Output:** Finally, I will combine the JSON data and the text report into a single dictionary and return it.

     


### Output Requirements:
- Final output MUST combine both tools' outputs:
```python
{{
    "json_data": {{  # From generate_sales_report_json
    }},
    "summary": "Full text analysis..."  # From analyze_sales_report_text
}}

Never proceed to analysis without completing data fetch

Never return partial outputs - both JSON and text MUST be present

Never modify data structure formats

{agent_scratchpad}
"""



prompt = PromptTemplate(
    input_variables=[],
    template=prompt_template
)


agent = create_openai_functions_agent(llm, prompt=prompt, tools=tools)

agent_executor = AgentExecutor(
    agent=agent,  
    tools=tools, 
    verbose=True    
)

def process_sales_analysis():
    """Fetch and analyze sales data using the agent."""
    response = agent_executor.invoke({})

    if isinstance(response, dict) and "output" in response:
       return response['output']
    
    return "Error: Could not generate the sales analysis report."

# # # Run script
# report = process_sales_analysis()  
# print(report)
