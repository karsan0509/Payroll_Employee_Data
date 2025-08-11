import streamlit as st
import pandas as pd
import os
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Excel file path
EXCEL_FILE = "data/employee_data.xlsx"

# Create directory if it doesn't exist
os.makedirs(os.path.dirname(EXCEL_FILE), exist_ok=True)

# Initialize Excel if it doesn't exist
if not os.path.exists(EXCEL_FILE):
    df_init = pd.DataFrame(columns=[
        "Employee Code", "Name", "Joining Date", "Basic", "HRA", "Allowances", "Deductions"
    ])
    df_init.to_excel(EXCEL_FILE, index=False)

# Load employee data
df = pd.read_excel(EXCEL_FILE)

# Streamlit UI
st.title("Payroll Management System")
menu = ["Add Employee", "Generate Salary Slip"]
choice = st.sidebar.selectbox("Menu", menu)

# PDF generation function
def generate_salary_slip(emp_data):
    file_name = f"salary_slip_{emp_data['Employee Code']}.pdf"
    c = canvas.Canvas(file_name, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 800, "Salary Slip")
    
    c.setFont("Helvetica", 12)
    y = 770
    for key, value in emp_data.items():
        c.drawString(50, y, f"{key}: {value}")
        y -= 20
    
    c.save()
    return file_name

if choice == "Add Employee":
    st.subheader("Add Employee Data")
    emp_code = st.text_input("Employee Code")
    name = st.text_input("Employee Name")
    joining_date = st.date_input("Joining Date", min_value=date(1960, 1, 1), max_value=date(2050, 12, 31))
    basic = st.number_input("Basic", min_value=0, max_value=10_000_000, value=0, step=1)
    hra = st.number_input("HRA", min_value=0, max_value=10_000_000, value=0, step=1)
    allowances = st.number_input("Allowances", min_value=0, max_value=10_000_000, value=0, step=1)
    deductions = st.number_input("Deductions", min_value=0, max_value=10_000_000, value=0, step=1)

    if st.button("Save"):
        new_data = pd.DataFrame([{
            "Employee Code": emp_code,
            "Name": name,
            "Joining Date": joining_date,
            "Basic": basic,
            "HRA": hra,
            "Allowances": allowances,
            "Deductions": deductions
        }])
        updated_df = pd.concat([df, new_data], ignore_index=True)
        updated_df.to_excel(EXCEL_FILE, index=False)
        st.success("Employee added successfully!")

elif choice == "Generate Salary Slip":
    st.subheader("Generate Salary Slip")
    if df.empty:
        st.warning("No employee data found.")
    else:
        employee_list = [f"{row['Employee Code']} - {row['Name']}" for _, row in df.iterrows()]
        selected_emp = st.selectbox("Select Employee", employee_list)
        
        if st.button("Generate PDF"):
            emp_code_selected = selected_emp.split(" - ")[0]
            emp_row = df[df["Employee Code"].astype(str) == str(emp_code_selected)]
            
            if not emp_row.empty:
                emp_data = emp_row.iloc[0].to_dict()
                pdf_path = generate_salary_slip(emp_data)
                with open(pdf_path, "rb") as f:
                    st.download_button("Download Salary Slip", f, file_name=pdf_path)
            else:
                st.error("Selected employee data not found. Please check Employee Code.")
