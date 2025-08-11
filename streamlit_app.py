import streamlit as st
import pandas as pd
import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Excel file path
EXCEL_FILE = "employee_data.xlsx"

# Initialize Excel file if not exists
if not os.path.exists(EXCEL_FILE):
    df_init = pd.DataFrame(columns=[
        "Employee Code", "Employee Name", "Date of Joining", "PF Number", "Location",
        "Total Days", "Absent Days", "Basic", "HRA", "Special Allowance", "Bonus",
        "PF", "Professional Tax", "Snacks", "Bus"
    ])
    df_init.to_excel(EXCEL_FILE, index=False)

# Load data
df = pd.read_excel(EXCEL_FILE)

st.title("Payroll Management System")

# Form to add employee data
with st.form("employee_form"):
    emp_code = st.text_input("Employee Code")
    emp_name = st.text_input("Employee Name")
    doj = st.date_input(
        "Date of Joining",
        value=datetime.date(2000, 1, 1),
        min_value=datetime.date(1960, 1, 1),
        max_value=datetime.date(2050, 12, 31)
    )
    pf_number = st.text_input("PF Number")
    location = st.text_input("Location")
    total_days = st.number_input("Total Days", min_value=0, max_value=31, value=30)
    absent_days = st.number_input("Absent Days", min_value=0, max_value=31, value=0)

    basic = st.number_input("Basic", min_value=0, max_value=10_000_000, value=int(0))
    hra = st.number_input("HRA", min_value=0, max_value=10_000_000, value=int(0))
    allowance = st.number_input("Special Allowance", min_value=0, max_value=10_000_000, value=int(0))
    bonus = st.number_input("Bonus", min_value=0, max_value=10_000_000, value=int(0))

    pf = st.number_input("PF", min_value=0, max_value=10_000_000, value=int(0))
    pro_tax = st.number_input("Professional Tax", min_value=0, max_value=10_000_000, value=int(0))
    snacks = st.number_input("Snacks", min_value=0, max_value=10_000_000, value=int(0))
    bus = st.number_input("Bus", min_value=0, max_value=10_000_000, value=int(0))

    submitted = st.form_submit_button("Save Data")

if submitted:
    new_data = {
        "Employee Code": emp_code,
        "Employee Name": emp_name,
        "Date of Joining": doj.strftime("%d.%m.%Y"),
        "PF Number": pf_number,
        "Location": location,
        "Total Days": total_days,
        "Absent Days": absent_days,
        "Basic": basic,
        "HRA": hra,
        "Special Allowance": allowance,
        "Bonus": bonus,
        "PF": pf,
        "Professional Tax": pro_tax,
        "Snacks": snacks,
        "Bus": bus
    }
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    st.success("Data saved successfully!")

# Function to generate PDF Salary Slip
def generate_salary_slip(data):
    pdf_file = f"SalarySlip_{data['Employee Code']}.pdf"
    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 50, "GLA University")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, f"Employee Code: {data['Employee Code']}")
    c.drawString(50, height - 95, f"Date of Joining: {data['Date of Joining']}")
    c.drawString(50, height - 110, f"Location: {data['Location']}")
    c.drawString(50, height - 125, f"Absent Days: {data['Absent Days']}")

    c.drawString(300, height - 80, f"Employee Name: {data['Employee Name']}")
    c.drawString(300, height - 95, f"PF Number: {data['PF Number']}")
    c.drawString(300, height - 110, f"Total Days: {data['Total Days']}")
    c.drawString(300, height - 125, f"Salary Month/Year: {datetime.date.today().strftime('%B %Y')}")

    c.line(50, height - 140, width - 50, height - 140)

    y = height - 160
    c.drawString(50, y, f"Basic Salary: Rs.{data['Basic']}")
    c.drawString(50, y - 15, f"HRA: Rs.{data['HRA']}")
    c.drawString(50, y - 30, f"Special Allowance: Rs.{data['Special Allowance']}")
    c.drawString(50, y - 45, f"Bonus: Rs.{data['Bonus']}")

    c.drawString(300, y, f"PF: Rs.{data['PF']}")
    c.drawString(300, y - 15, f"Professional Tax: Rs.{data['Professional Tax']}")
    c.drawString(300, y - 30, f"Snacks: Rs.{data['Snacks']}")
    c.drawString(300, y - 45, f"Bus: Rs.{data['Bus']}")

    total_earnings = data['Basic'] + data['HRA'] + data['Special Allowance'] + data['Bonus']
    total_deductions = data['PF'] + data['Professional Tax'] + data['Snacks'] + data['Bus']
    net_salary = total_earnings - total_deductions

    c.drawString(50, y - 75, f"Total Earnings: Rs.{total_earnings:.2f}")
    c.drawString(300, y - 75, f"Total Deductions: Rs.{total_deductions:.2f}")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y - 95, f"Net Salary: Rs.{net_salary:.2f}")

    c.save()
    return pdf_file

# Select employee for salary slip
st.subheader("Generate Salary Slip")
emp_list = df["Employee Code"].astype(str) + " - " + df["Employee Name"]
selected_emp = st.selectbox("Select Employee", emp_list)

if st.button("Generate PDF"):
    emp_code_selected = selected_emp.split(" - ")[0]
    emp_data = df[df["Employee Code"] == emp_code_selected].iloc[0].to_dict()
    pdf_path = generate_salary_slip(emp_data)
    with open(pdf_path, "rb") as f:
        st.download_button("Download Salary Slip", f, file_name=pdf_path)
