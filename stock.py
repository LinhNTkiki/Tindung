import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Credit Score Prediction",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for enhanced styling
st.markdown("""
    <style>
        /* Main title styling */
        .main-title {
            font-size: 48px;
            font-weight: bold;
            color: #FFFFFF; /* White for contrast */
            text-align: center;
        }

        /* Sidebar styling */
        .sidebar .sidebar-content {
            background-color: #001F3F; /* Dark blue */
            color: #FFFFFF; /* White text for contrast */
        }

        /* Button styling */
        .stButton>button {
            background-color: #FF6F61; /* Coral for buttons */
            color: white;
            font-size: 18px;
            width: 100%;
            border-radius: 8px;
        }
        .stButton>button:hover {
            background-color: #E05A47; /* Slightly darker coral on hover */
        }

        /* Welcome text styling */
        .welcome-text {
            font-size: 20px;
            color: #FFFFFF; /* White for contrast */
            margin-bottom: 30px;
        }

        /* Background styling */
        .stApp {
            background-color: #001F3F; /* Dark blue background */
            color: #FFFFFF; /* White text for the app */
        }
    </style>
""", unsafe_allow_html=True)

# Home page content
def home_page():
    st.markdown("<h1 class='main-title'>Credit Score Prediction App</h1>", unsafe_allow_html=True)
    st.markdown("<p class='welcome-text'>This app provides credit score predictions based on customer details. Use the sidebar to input customer information, then click 'Predict' to view the credit score.</p>", unsafe_allow_html=True)

# Load the dataset
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("credit_data.csv")
    except FileNotFoundError:
        st.error("The dataset 'credit_data.csv' was not found. Please check the file path.")
        st.stop()
   
    # Encoding categorical columns (excluding Credit_Mix)
    label_encoders = {}
    categorical_cols = ["Occupation"]
    for col in categorical_cols:
        if col in data.columns:
            le = LabelEncoder()
            data[col] = le.fit_transform(data[col].astype(str))
            label_encoders[col] = le
        else:
            st.error(f"Column '{col}' not found in the dataset.")
            st.stop()

    # Encode the target variable with pre-initialized LabelEncoder for Credit_Score
    credit_score_categories = ["Poor", "Standard", "Good"]
    credit_score_encoder = LabelEncoder()
    credit_score_encoder.fit(credit_score_categories)
    data['Credit_Score'] = credit_score_encoder.transform(data['Credit_Score'])
   
    # Drop the specified columns
    data.drop(columns=['Age', 'Num_Credit_Inquiries', 'Num_of_Loan', 'Payment_of_Min_Amount', 'Payment_Behaviour', "Credit_Mix"], inplace=True)
    return data, label_encoders, credit_score_encoder

# Main application function
def main():
    home_page()  # Show the homepage content

    # Sidebar for user input
    st.sidebar.title('📋 Input Customer Details')

    # Customer data input fields
    col1, col2 = st.sidebar.columns(2)
    with col1:
        occupation = st.selectbox("Occupation", ["Scientist", "Engineer", "Architect", "Other", 'Lawyer', 'Mechanic', 'Entrepreneur', 'Teacher', 'Accountant', 'Doctor', 'Media_Manager', 'Developer', 'Musician', 'Journalist', 'Writer', 'Manager'], help="Customer's occupation type")
        annual_income = st.number_input("Annual Income", min_value=0.0, step=500.0, value=50000.0, help="Total yearly income of the customer")
        monthly_salary = st.number_input("Monthly Inhand Salary", min_value=0.0, step=50.0, value=3000.0, help="Monthly salary received after deductions")
        interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, step=0.1, value=5.0, help="Annual interest rate in percentage")

    with col2:
        delay_due_date = st.number_input("Days Delayed from Due Date", min_value=0, step=1, value=0, help="Number of days payment is delayed from due date")
        delayed_payments = st.number_input("Number of Delayed Payments", min_value=0, step=1, value=0, help="Total count of delayed payments")
        outstanding_debt = st.number_input("Outstanding Debt", min_value=0.0, step=100.0, value=1000.0, help="Total amount of debt yet to be paid")
        credit_utilization = st.number_input("Credit Utilization Ratio", min_value=0.0, max_value=100.0, step=0.1, value=50.0, help="Percentage of credit used against total credit available")

    emi_per_month = st.sidebar.number_input("Total EMI per Month", min_value=0.0, step=10.0, value=200.0, help="Total EMI amount to be paid per month")
    amount_invested = st.sidebar.number_input("Amount Invested Monthly", min_value=0.0, step=10.0, value=500.0, help="Monthly investment amount")
    monthly_balance = st.sidebar.number_input("Monthly Balance", min_value=0.0, step=10.0, value=1000.0, help="Remaining balance at the end of the month")
    credit_history_age = st.sidebar.number_input("Credit History Age (Months)", min_value=0, step=1, value=12, help="Length of credit history in months")

    # Load data and label encoders
    data, label_encoders, credit_score_encoder = load_data()

    # Prepare feature and target variables
    X = data.drop(columns=["Credit_Score"])
    y = data["Credit_Score"]

    # Apply SMOTE for balancing
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)

    # Split resampled data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

    # Train the model
    @st.cache_resource
    def train_model():
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)
        return model
   
    # Save the model in session state
    st.session_state.model = train_model()

    # Encode input categorical variables
    input_encoded = {
        'Occupation': label_encoders['Occupation'].transform([occupation])[0],
        'Annual_Income': annual_income,
        'Monthly_Inhand_Salary': monthly_salary,
        'Interest_Rate': interest_rate,
        'Delay_from_due_date': delay_due_date,
        'Num_of_Delayed_Payment': delayed_payments,
        'Outstanding_Debt': outstanding_debt,
        'Credit_Utilization_Ratio': credit_utilization,
        'Total_EMI_per_month': emi_per_month,
        'Amount_invested_monthly': amount_invested,
        'Monthly_Balance': monthly_balance,
        'Credit_History_Age_in_Months': credit_history_age
    }

    # Prediction function
    def predict_credit_score(input_data):
        if 'model' not in st.session_state:
            st.warning("Please train the model first.")
            return None
        prediction = st.session_state.model.predict(input_data)
        return prediction[0]

    # Predict button with updated gauge chart
    if st.sidebar.button("Predict Credit Score"):
        input_data = pd.DataFrame([input_encoded])
        prediction_encoded = predict_credit_score(input_data)

        if prediction_encoded is not None:
            prediction = credit_score_encoder.inverse_transform([prediction_encoded])[0]
            gauge_labels = ["Poor", "Standard", "Good"]
            gauge_colors = ["#ff4d4d", "#ffa500", "#32cd32"]
            gauge_index = gauge_labels.index(prediction)
            gauge_position = gauge_index * 50 + 25

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=gauge_position,
                title={'text': "Credit Score"},
                gauge={
                    'axis': {'range': [0, 150], 'tickvals': [25, 75, 125], 'ticktext': gauge_labels},
                    'bar': {'color': gauge_colors[gauge_index]},
                    'steps': [
                        {'range': [0, 50], 'color': gauge_colors[0]},
                        {'range': [50, 100], 'color': gauge_colors[1]},
                        {'range': [100, 150], 'color': gauge_colors[2]},
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': gauge_position
                    }
                }
            ))
            st.plotly_chart(fig)
            st.success(f"**Predicted Credit Score Category:** {prediction}")

# Run the app
if __name__ == "__main__":
    main()
