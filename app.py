import streamlit as st

from agents.data_ingestor import ingest_documents
from agents.financial_agent import extract_financial_data
from agents.research_agent import research_company
from agents.risk_agent import calculate_risk
from agents.recommendation_agent import recommend_loan
from agents.cam_generator import generate_cam

st.title("Intelli-Credit AI")

company = st.text_input("Company Name")

files = st.file_uploader("Upload Documents", accept_multiple_files=True)

if st.button("Analyze"):

    paths = []

    for f in files:
        path = f.name
        with open(path, "wb") as file:
            file.write(f.getbuffer())
        paths.append(path)

    # ---------- Document Processing ----------
    docs = ingest_documents(paths)

    # ---------- Financial Extraction ----------
    financials = extract_financial_data(docs)

    # ---------- Company Research ----------
    news = research_company(company)

    # ---------- Risk Calculation ----------
    score, risk = calculate_risk(financials, news)

    st.subheader("Risk Analysis")

    st.metric("Risk Percentage", f"{score}%")
    st.success(risk)

    # ---------- Loan Recommendation ----------
    recommendation = recommend_loan(financials, score)

    # ---------- Generate CAM Report ----------
    generate_cam(company, financials, risk, recommendation)

    # ---------- Financial Section ----------
    st.subheader("Financial Analysis")

    st.metric("Revenue", f"₹{financials['revenue']}")
    st.metric("Profit", f"₹{financials['profit']}")

    # ---------- News Section ----------
    st.subheader("Latest News")

    if news:
        for n in news:
            st.write("•", n)
    else:
        st.write("No news found")

    # ---------- Risk ----------
    st.subheader("Risk Level")
    st.success(risk)

    # ---------- Recommendation ----------
    st.subheader("Loan Recommendation")

    st.write("Decision:", recommendation["decision"])
    st.write("Loan Amount: ₹", recommendation["loan_amount"])

    # ---------- Download CAM ----------
    st.subheader("Download Credit Report")

    with open("CAM_Report.docx", "rb") as file:
        st.download_button(
            label="Download Credit Appraisal Memo",
            data=file,
            file_name="CAM_Report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )