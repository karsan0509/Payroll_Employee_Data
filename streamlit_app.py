import streamlit as st
import pandas as pd
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime

# -------------------------
# Config / Excel file setup
# -------------------------
EXCEL_FILE = "Payroll_Management_Data.xlsx"
os.makedirs(os.path.dirname(EXCEL_FILE) or ".", exist_ok=True)

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

# -------------------------
# Load data
# -------------------------
df = pd.read_excel(EXCEL_FILE)

# -------------------------
# Utility functions
# -------------------------
def save_df(df_local):
    df_local.to_excel(EXCEL_FILE, index=False)

def calculate_net(basic, hra, special, bonus, pf, tax, snacks, bus, loan):
    total_earnings = basic + hra + special + bonus
    total_deductions = pf + tax + snacks + bus + loan
    net = total_earnings - total_deductions
    return total_earnings, total_deductions, net

def generate_salary_pdf(emp_info):
    """
    emp_info: dict with all required keys (strings, numbers)
    returns BytesIO with PDF content
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    W, H = A4

    # Convert mm coordinates for nicer spacing if needed (reportlab uses points)
    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2.0, H - 40, "GLA University")

    # Subheading - small gap
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2.0, H - 60, "")  # optional

    # Employee Info - two columns
    left_x = 40
    right_x = W / 2 + 20
    y = H - 100
    line_height = 16

    # Left column
    c.setFont("Helvetica", 11)
    c.drawString(left_x, y, f"Employee Code: {emp_info.get('Employee Code','')}")
    c.drawString(right_x, y, f"Employee Name: {emp_info.get('Name','')}")
    y -= line_height
    doj_str = emp_info.get("DOJ")
    if isinstance(doj_str, (pd.Timestamp, datetime)):
        doj_str = doj_str.strftime("%d.%m.%Y")
    c.drawString(left_x, y, f"Date of Joining: {doj_str}")
    c.drawString(right_x, y, f"PF Number: {emp_info.get('PF Number','')}")
    y -= line_height
    # Location may be long; wrap minimally
    location = emp_info.get("Location","")
    c.drawString(left_x, y, f"Location: {location}")
    total_days = emp_info.get("Total Days", "")
    c.drawString(right_x, y, f"Total Days: {total_days}")
    y -= line_height
    absent = emp_info.get("Absent Days", "")
    salary_month = emp_info.get("Salary Month","")
    salary_year = emp_info.get("Salary Year","")
    c.drawString(left_x, y, f"Absent Days: {absent}")
    c.drawString(right_x, y, f"Salary Month/Year: {salary_month} {salary_year}")

    # Horizontal line separator
    y -= (line_height + 6)
    c.line(30, y, W - 30, y)
    y -= 18

    # Earnings (left) and Deductions (right)
    col_left_x = left_x
    col_right_x = right_x
    c.setFont("Helvetica-Bold", 11)
    c.drawString(col_left_x, y, "Earnings")
    c.drawString(col_right_x, y, "Deductions")
    y -= line_height

    c.setFont("Helvetica", 11)
    # Earnings list
    basic = float(emp_info.get("Basic", 0))
    hra = float(emp_info.get("HRA", 0))
    special = float(emp_info.get("Special Allowance", 0))
    bonus = float(emp_info.get("Bonus", 0))
    pf = float(emp_info.get("PF", 0))
    tax = float(emp_info.get("Pro Tax", 0))
    snacks = float(emp_info.get("Snacks", 0))
    bus = float(emp_info.get("Bus", 0))
    loan = float(emp_info.get("Loan", 0))

    c.drawString(col_left_x, y, f"Basic Salary: Rs.{basic:,.2f}")
    c.drawString(col_right_x, y, f"PF: Rs.{pf:,.2f}")
    y -= line_height
    c.drawString(col_left_x, y, f"HRA: Rs.{hra:,.2f}")
    c.drawString(col_right_x, y, f"Professional Tax: Rs.{tax:,.2f}")
    y -= line_height
    c.drawString(col_left_x, y, f"Special Allowance: Rs.{special:,.2f}")
    c.drawString(col_right_x, y, f"Snacks: Rs.{snacks:,.2f}")
    y -= line_height
    c.drawString(col_left_x, y, f"Bonus: Rs.{bonus:,.2f}")
    c.drawString(col_right_x, y, f"Bus: Rs.{bus:,.2f}")
    y -= line_height
    # space for loan on right if more lines
    c.drawString(col_right_x, y, f"Loan: Rs.{loan:,.2f}")
    y -= (line_height + 6)

    # Totals
    total_earnings, total_deductions, net_salary = calculate_net(basic, hra, special, bonus, pf, tax, snacks, bus, loan)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(col_left_x, y, f"Total Earnings: Rs.{total_earnings:,.2f}")
    c.drawString(col_right_x, y, f"Total Deductions: Rs.{total_deductions:,.2f}")
    y -= (line_height + 10)

    # Net Salary emphasized
    c.setFont("Helvetica-Bold", 12)
    c.drawString(col_left_x, y, f"Net Salary: Rs.{net_salary:,.2f}")

    # Signature line (bottom right-ish)
    sign_y = 70
    c.line(W - 220, sign_y, W - 60, sign_y)
    c.setFont("Helvetica", 10)
    c.drawString(W - 205, sign_y - 12, "Authorized Signature")

    # Finish
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Payroll - Salary Slip", layout="wide")
st.title("Payroll Management System — PDF Salary Slip (GLA style)")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Search / Edit Employee")
    search_code = st.text_input("Enter Employee Code to search", value="")
    if search_code:
        record = df[df["Employee Code"].astype(str) == str(search_code)]
        if record.empty:
            st.warning("No record found for this Employee Code.")
            record = pd.DataFrame()
    else:
        record = pd.DataFrame()

    # If found, prefill values, else provide blank form to add/edit
    if not record.empty:
        row = record.iloc[0]
        st.info(f"Loaded record for: {row['Name']} (Code: {row['Employee Code']})")
        name = st.text_input("Employee Name", value=row.get("Name",""))
        gender = st.selectbox("Gender", ["Male","Female","Other"], index=["Male","Female","Other"].index(row.get("Gender","Male")) if row.get("Gender","Male") in ["Male","Female","Other"] else 0)
        dob = st.date_input("DOB", value=pd.to_datetime(row.get("DOB")).date() if pd.notna(row.get("DOB")) else datetime(1990,1,1).date())
        doj = st.date_input("DOJ", value=pd.to_datetime(row.get("DOJ")).date() if pd.notna(row.get("DOJ")) else datetime(2010,1,1).date())
        dept = st.text_input("Department", value=row.get("Department",""))
        bank = st.text_input("Bank Name", value=row.get("Bank Name",""))
        acc = st.text_input("Account No.", value=row.get("Account No.",""))
        pan = st.text_input("PAN", value=row.get("PAN",""))
        uan = st.text_input("UAN", value=row.get("UAN",""))
        location = st.text_input("Location", value=row.get("Location",""))
        pf_no = st.text_input("PF Number", value=row.get("PF Number",""))
        total_days = st.number_input("Total Days", min_value=0, max_value=31, value=int(row.get("Total Days",30)))
        absent_days = st.number_input("Absent Days", min_value=0, max_value=31, value=int(row.get("Absent Days",0)))
        salary_month = st.selectbox("Salary Month", ["January","February","March","April","May","June","July","August","September","October","November","December"], index=int(row.get("Salary Month",1))-1 if str(row.get("Salary Month","1")).isdigit() else 0)
        salary_year = st.number_input("Salary Year", min_value=2000, max_value=2100, value=int(row.get("Salary Year", datetime.now().year)))

        # Salary numeric fields (safe max)
        basic = st.number_input("Basic", min_value=0, max_value=10_000_000, value=float(row.get("Basic",0)))
        hra = st.number_input("HRA", min_value=0, max_value=10_000_000, value=float(row.get("HRA",0)))
        special = st.number_input("Special Allowance", min_value=0, max_value=10_000_000, value=float(row.get("Special Allowance",0)))
        bonus = st.number_input("Bonus", min_value=0, max_value=10_000_000, value=float(row.get("Bonus",0)))
        pf = st.number_input("PF", min_value=0, max_value=10_000_000, value=float(row.get("PF",0)))
        tax = st.number_input("Pro Tax", min_value=0, max_value=10_000_000, value=float(row.get("Pro Tax",0)))
        snacks = st.number_input("Snacks", min_value=0, max_value=10_000_000, value=float(row.get("Snacks",0)))
        bus = st.number_input("Bus", min_value=0, max_value=10_000_000, value=float(row.get("Bus",0)))
        loan = st.number_input("Loan", min_value=0, max_value=10_000_000, value=float(row.get("Loan",0)))

        # Buttons: Calculate, Save, Generate PDF
        calc_col1, calc_col2, calc_col3 = st.columns(3)
        with calc_col1:
            if st.button("Calculate Net Salary"):
                te, td, net = calculate_net(basic, hra, special, bonus, pf, tax, snacks, bus, loan)
                st.success(f"Total Earnings: Rs.{te:,.2f} | Total Deductions: Rs.{td:,.2f} | Net Salary: Rs.{net:,.2f}")

        with calc_col2:
            if st.button("Save / Update Record"):
                idx = df[df["Employee Code"].astype(str) == str(search_code)].index
                new_row = {
                    "Employee Code": search_code, "Name": name, "Gender": gender, "DOB": dob,
                    "DOJ": doj, "Department": dept, "Bank Name": bank, "Account No.": acc,
                    "PAN": pan, "UAN": uan, "Location": location, "PF Number": pf_no,
                    "Total Days": total_days, "Absent Days": absent_days,
                    "Salary Month": salary_month, "Salary Year": salary_year,
                    "Basic": basic, "HRA": hra, "Special Allowance": special, "Bonus": bonus,
                    "PF": pf, "Pro Tax": tax, "Snacks": snacks, "Bus": bus, "Loan": loan,
                    "Net Salary": calculate_net(basic, hra, special, bonus, pf, tax, snacks, bus, loan)[2]
                }
                if len(idx) > 0:
                    df.loc[idx[0]] = new_row
                else:
                    df.loc[len(df)] = new_row
                save_df(df)
                st.success("Record saved to Excel.")

        with calc_col3:
            if st.button("Generate Salary Slip (PDF)"):
                emp_info = {
                    "Employee Code": search_code,
                    "Name": name,
                    "DOJ": doj,
                    "PF Number": pf_no,
                    "Location": location,
                    "Total Days": total_days,
                    "Absent Days": absent_days,
                    "Salary Month": salary_month,
                    "Salary Year": salary_year,
                    "Basic": basic,
                    "HRA": hra,
                    "Special Allowance": special,
                    "Bonus": bonus,
                    "PF": pf,
                    "Pro Tax": tax,
                    "Snacks": snacks,
                    "Bus": bus,
                    "Loan": loan
                }
                pdf_buf = generate_salary_pdf(emp_info)
                st.download_button(
                    "⬇ Download Salary Slip (PDF)",
                    data=pdf_buf,
                    file_name=f"SalarySlip_{search_code}.pdf",
                    mime="application/pdf"
                )
    else:
        st.info("No employee loaded. You can add new employee in the right panel.")

with col2:
    st.subheader("Add New Employee")
    with st.form("add_new"):
        new_code = st.text_input("Employee Code")
        new_name = st.text_input("Name")
        new_gender = st.selectbox("Gender", ["Male","Female","Other"])
        new_dob = st.date_input("DOB", value=datetime(1990,1,1))
        new_doj = st.date_input("DOJ", value=datetime(2015,1,1))
        new_dept = st.text_input("Department")
        new_bank = st.text_input("Bank Name")
        new_acc = st.text_input("Account No.")
        new_pan = st.text_input("PAN")
        new_uan = st.text_input("UAN")
        new_loc = st.text_input("Location")
        new_pfno = st.text_input("PF Number")
        new_total_days = st.number_input("Total Days", min_value=0, max_value=31, value=30)
        new_absent = st.number_input("Absent Days", min_value=0, max_value=31, value=0)
        new_month = st.selectbox("Salary Month", ["January","February","March","April","May","June","July","August","September","October","November","December"])
        new_year = st.number_input("Salary Year", min_value=2000, max_value=2100, value=datetime.now().year)
        submitted = st.form_submit_button("Save New Employee")
        if submitted:
            if new_code == "" or new_name == "":
                st.error("Please provide at least Employee Code and Name.")
            else:
                df.loc[len(df)] = [
                    new_code, new_name, new_gender, new_dob, new_doj, new_dept,
                    new_bank, new_acc, new_pan, new_uan, new_loc, new_pfno,
                    new_total_days, new_absent, new_month, new_year,
                    0,0,0,0,0,0,0,0,0,0
                ]
                save_df(df)
                st.success("New employee record added.")

# Bottom: Download full Excel
st.markdown("---")
st.caption("Download full payroll Excel data:")
excel_buf = BytesIO()
df.to_excel(excel_buf, index=False)
st.download_button("📥 Download Payroll Data (Excel)", data=excel_buf.getvalue(), file_name="Payroll_Management_Data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
