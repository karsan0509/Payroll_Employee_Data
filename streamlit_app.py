import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os
import base64

EXCEL_FILE = "C:/Users/Administrator/Desktop/Project Sem-3/Payroll_Management_Data.xlsx"

if not os.path.exists(EXCEL_FILE):
    df_init = pd.DataFrame(columns=[
        "Employee Code", "Name", "Gender", "DOB", "DOJ", "Department",
        "Bank Name", "Account No.", "PAN", "UAN", "Location", "PF Number",
        "Total Days", "Absent Days", "Salary Month", "Salary Year",
        "Basic", "HRA", "Special Allowance", "Bonus",
        "PF", "Pro Tax", "Snacks", "Bus", "Loan",
        "Net Salary"
    ])
    df_init.to_excel(EXCEL_FILE, index=False)

st.set_page_config(layout="wide")
st.title("Payroll Management System")

# Load Excel data once to reuse
df = pd.read_excel(EXCEL_FILE)

# Handle search before form to set default values
emp_code_default = ""
fields = {
    "name": "",
    "gender": "Male",
    "dob": datetime(1990, 1, 1).date(),
    "doj": datetime(2010, 1, 1).date(),
    "dept": "",
    "bank": "",
    "acc": "",
    "pan": "",
    "uan": "",
    "location": "",
    "pf_no": "",
    "total_days": 30,
    "absent_days": 0,
    "month": "January",
    "year": datetime.now().year,
    "basic": 0,
    "hra": 0,
    "special": 0,
    "bonus": 0,
    "pf": 0,
    "tax": 0,
    "snacks": 0,
    "bus": 0,
    "loan": 0,
}

search_clicked = False
emp_code = st.text_input("Employee Code")
search_button = st.button("Search")
if search_button and emp_code:
    search_clicked = True
    record = df[df["Employee Code"].astype(str) == str(emp_code)]
    if not record.empty:
        row = record.iloc[0]
        fields = {
            "name": row["Name"],
            "gender": row["Gender"],
            "dob": pd.to_datetime(row["DOB"]).date(),
            "doj": pd.to_datetime(row["DOJ"]).date(),
            "dept": row["Department"],
            "bank": row["Bank Name"],
            "acc": row["Account No."],
            "pan": row["PAN"],
            "uan": row["UAN"],
            "location": row["Location"],
            "pf_no": row["PF Number"],
            "total_days": row["Total Days"],
            "absent_days": row["Absent Days"],
            "month": row["Salary Month"],
            "year": row["Salary Year"],
            "basic": row["Basic"],
            "hra": row["HRA"],
            "special": row["Special Allowance"],
            "bonus": row["Bonus"],
            "pf": row["PF"],
            "tax": row["Pro Tax"],
            "snacks": row["Snacks"],
            "bus": row["Bus"],
            "loan": row["Loan"],
        }

with st.form("payroll_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Employee Name", value=fields["name"])
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(fields["gender"]))
        dob = st.date_input("DOB", value=fields["dob"], min_value=datetime(1960, 1, 1))
        doj = st.date_input("DOJ", value=fields["doj"], min_value=datetime(1960, 1, 1))
        dept = st.text_input("Department", value=fields["dept"])
        bank = st.text_input("Bank Name", value=fields["bank"])
        acc = st.text_input("Account No.", value=fields["acc"])
        pan = st.text_input("PAN", value=fields["pan"])
        uan = st.text_input("UAN", value=fields["uan"])
    with col2:
        location = st.text_input("Location", value=fields["location"])
        pf_no = st.text_input("PF Number", value=fields["pf_no"])
        total_days = st.number_input("Total Days", 0, 31, value=int(fields["total_days"]))
        absent_days = st.number_input("Absent Days", 0, 31, value=int(fields["absent_days"]))
        month = st.selectbox("Salary Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], index=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"].index(fields["month"]))
        year = st.number_input("Salary Year", 2000, 2100, value=int(fields["year"]))
        basic = st.number_input("Basic", 0, None, value=int(fields["basic"]))
        hra = st.number_input("HRA", 0, None, value=int(fields["hra"]))
        special = st.number_input("Special Allowance", 0, None, value=int(fields["special"]))
        bonus = st.number_input("Bonus", 0, None, value=int(fields["bonus"]))
        pf = st.number_input("PF", 0, None, value=int(fields["pf"]))
        tax = st.number_input("Pro Tax", 0, None, value=int(fields["tax"]))
        snacks = st.number_input("Snacks", 0, None, value=int(fields["snacks"]))
        bus = st.number_input("Bus", 0, None, value=int(fields["bus"]))
        loan = st.number_input("Loan", 0, None, value=int(fields["loan"]))

    calculate = st.form_submit_button("Calculate")
    save = st.form_submit_button("Save")

if calculate:
    earnings = basic + hra + special + bonus
    deductions = pf + tax + snacks + bus + loan
    net = earnings - deductions
    net_salary = f"{net:.2f}"
    st.success(f"Net Salary: Rs. {net_salary}")

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 16)
            self.cell(0, 10, "GLA University", ln=True, align="C")
            self.set_font("Arial", "", 12)
            self.cell(0, 10, f"Salary Slip - {month} {year}", ln=True, align="C")
            self.ln(5)

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Employee Code: {emp_code}", ln=True)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"DOJ: {doj}", ln=True)
    pdf.cell(0, 10, f"PF Number: {pf_no}", ln=True)
    pdf.cell(0, 10, f"Location: {location}", ln=True)
    pdf.cell(0, 10, f"Total Days: {total_days} | Absent Days: {absent_days}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Earnings", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Basic: Rs. {basic}", ln=True)
    pdf.cell(0, 10, f"HRA: Rs. {hra}", ln=True)
    pdf.cell(0, 10, f"Special Allowance: Rs. {special}", ln=True)
    pdf.cell(0, 10, f"Bonus: Rs. {bonus}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Deductions", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"PF: Rs. {pf}", ln=True)
    pdf.cell(0, 10, f"Pro Tax: Rs. {tax}", ln=True)
    pdf.cell(0, 10, f"Snacks: Rs. {snacks}", ln=True)
    pdf.cell(0, 10, f"Bus: Rs. {bus}", ln=True)
    pdf.cell(0, 10, f"Loan: Rs. {loan}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Net Salary: Rs. {net_salary}", ln=True)

    pdf_output = pdf.output(dest="S").encode("latin1")
    b64 = base64.b64encode(pdf_output).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="SalarySlip_{emp_code}.pdf" target="_blank">📄 Download Salary Slip PDF</a>'
    st.markdown(href, unsafe_allow_html=True)

if save:
    net_salary = f"{basic + hra + special + bonus - (pf + tax + snacks + bus + loan):.2f}" if calculate else ""
    new_row = {
        "Employee Code": emp_code, "Name": name, "Gender": gender, "DOB": dob,
        "DOJ": doj, "Department": dept, "Bank Name": bank, "Account No.": acc,
        "PAN": pan, "UAN": uan, "Location": location, "PF Number": pf_no,
        "Total Days": total_days, "Absent Days": absent_days,
        "Salary Month": month, "Salary Year": year,
        "Basic": basic, "HRA": hra, "Special Allowance": special, "Bonus": bonus,
        "PF": pf, "Pro Tax": tax, "Snacks": snacks, "Bus": bus, "Loan": loan,
        "Net Salary": net_salary
    }
    df = df[df["Employee Code"].astype(str) != str(emp_code)]
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    st.success("Record saved to Excel.")
