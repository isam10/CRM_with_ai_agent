import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
import os
import pickle
import json
import requests
import psycopg2
from dotenv import load_dotenv
from celery import shared_task
load_dotenv()

@shared_task
def predictions():
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")


    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    MODEL_PATH = os.getenv('MODEL_PATH')


    connection = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )

    query = "SELECT * FROM predict_customers"
    df = pd.read_sql_query(query, connection)

    df_original = df.copy()

    connection.close()

      
      

    df['tenure'].fillna(df['tenure'].median(), inplace=True)
    df['warehousetohome'].fillna(df['warehousetohome'].median(), inplace=True)
    df['hourspendonapp'].fillna(df['hourspendonapp'].median(), inplace=True)
    df['orderamounthikefromlastyear'].fillna(df['orderamounthikefromlastyear'].median(), inplace=True)
    df['couponused'].fillna(df['couponused'].median(), inplace=True)
    df['ordercount'].fillna(df['ordercount'].median(), inplace=True)
    df['daysincelastorder'].fillna(df['daysincelastorder'].median(), inplace=True)


    label_encoders = {}
    Customer_IDs = df['customerid']
    for col in df.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le

    scaler = StandardScaler()

    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns.drop(['churn', 'customerid'])  
    df[numerical_cols] = scaler.fit_transform(df[numerical_cols])


    X = df.drop(columns=['churn', 'customerid'])
    y = df['churn']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
          
          
          
    # if not os.path.exists(MODEL_PATH):
    #     raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

    # with open(MODEL_PATH, "rb") as file:
    #    model = pickle.load(file)


    # saved model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    with open(MODEL_PATH, "wb") as file:
        pickle.dump(model, file)

    # Make predictions
    y_pred = model.predict(X_test)

        
    X_test_original = X_test.copy()
    X_test_original[numerical_cols] = scaler.inverse_transform(X_test[numerical_cols])

    X_test_original['customerid'] = Customer_IDs.loc[X_test.index].values

    y_pred_series = pd.Series(y_pred, index=X_test.index, name="predicted")
    X_test_original['predicted'] = y_pred_series

    filtered_X_test = X_test_original[X_test_original["predicted"] == 1]


    churn_indices = X_test.index[y_pred == 1]

    churn_customers = df_original.loc[churn_indices]

    churn_customers = churn_customers.head(10)


    churn_customers_json = churn_customers.to_dict(orient="records")
          
          
          
    prompt = f"""
    You are a marketing AI expert generating personalized notifications for customers at high risk of churn.

    ### **Task:**
    You will receive structured customer data in JSON format with the following attributes:
      - **CustomerID** (Unique ID)
      - **Churn** (Churn status)
      - **Tenure**, **PreferredLoginDevice**, **CityTier**, **WarehouseToHome**
      - **PreferredPaymentMode**, **Gender**, **HourSpendOnApp**
      - **NumberOfDeviceRegistered**, **PreferedOrderCat**, **SatisfactionScore**
      - **MaritalStatus**, **NumberOfAddress**, **Complain**, **Order Trends**
      - **CouponUsed**, **OrderCount**, **DaySinceLastOrder**, **CashbackAmount**
      
    Based on the given data, craft **tailored promotional notifications**.

    ### **Personalization Guidelines:**
    -  **Cashback Offers**: Offer exclusive cashback for frequent users or those with **high order amounts**.
    -  **Category Discounts**: Provide discounts on **favorite order categories** for customers with **reduced spending**.
    -  **Complaint Handling**: Address customer **complaints** with **targeted retention offers**.
    -  **Loyalty Rewards**: Highlight **loyalty rewards** for **long-tenure** customers.
    -  **Re-engagement**: Encourage **repeat purchases** for customers **inactive for many days**.

    ---

    ### **Expected JSON Output Format:**
    Ensure the response is **strictly in JSON format**, with separate entries for each customer.

    ```json
    
      {{
        "customerid": "12345",
        "Notification": "Hi John! 🎉 We've noticed you love ordering electronics. Enjoy an exclusive 20% discount on your next purchase! Use code TECH20 at checkout. Limited time offer!"
      }},
      {{
        "customerid": "67890",
        "Notification": "Hey Sarah! We miss you! 💖 Your last order was 45 days ago. Get ₹300 cashback on your next purchase. Come back and shop with us today!"
      }}
      
    ```
    Now, generate tailored notifications for each customer based on the given JSON data. JSON data {json.dumps(churn_customers_json, indent=2)}""" 
      

    response = llm.invoke([
            SystemMessage(content="You are an AI that provides image captions and metadata for architecture and interior design."),
            HumanMessage(content=[
                {"type": "text", "text": prompt},
            ])
        ])

    json_text= response.content

    json_text_clean = json_text.strip("```json").strip("```")

    print(json_text_clean)

    customer_notifications = json.loads(json_text_clean)

    return customer_notifications

# Extract the required fields
# formatted_notifications = [
#     {"id": customer["CustomerID"], "notification": customer["Notification"]}
#     for customer in customer_notificatio ns
# ]

# # Print or use the formatted JSON
# print(json.dumps(formatted_notifications, indent=2))