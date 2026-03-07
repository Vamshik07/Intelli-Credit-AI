def recommend_loan(financials, score):

    revenue = int(financials["revenue"])
    profit = int(financials["profit"])

    # Default loan amount
    loan_amount = 0
    decision = "Reject"

    if score < 20 and profit > 10000000:
        decision = "Approve"
        loan_amount = revenue * 0.2

    elif score < 40:
        decision = "Approve with Conditions"
        loan_amount = revenue * 0.1

    else:
        decision = "Reject"
        loan_amount = 0

    return {
        "decision": decision,
        "loan_amount": int(loan_amount)
    }