import joblib

# Load trained model
model = joblib.load("models/credit_risk_model.pkl")

def calculate_risk(financials, news):

    revenue = financials["revenue"]
    profit = financials["profit"]
    debt = financials["debt"]

    data = [[revenue, profit, debt]]

    # Predict probability
    probability = model.predict_proba(data)[0][1]

    risk_percentage = round(probability * 100, 2)

    if risk_percentage < 30:
        risk_level = "Low Risk"
    elif risk_percentage < 60:
        risk_level = "Medium Risk"
    else:
        risk_level = "High Risk"

    return risk_percentage, risk_level