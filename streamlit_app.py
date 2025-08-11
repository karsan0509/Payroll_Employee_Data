# streamlit_app.py
import streamlit as st
import pandas as pd
import os
import datetime
from io import BytesIO

# reportlab imports for nicer table-based PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
)

# -------------------------
# Config / Excel file setup
# -------------------------
DATA_DIR = "data"
EXCEL_FILE = os.path.join(DATA_DIR, "Payroll_Management_Data.xlsx")
os.makedirs(DATA_DIR, exist_ok=True)

COLUMNS = [
    "Employee Code", "Name", "Gender", "DOB", "DOJ", "Department",
    "Bank Name", "Account No.", "PAN", "UAN", "Location", "PF Number",
    "Total Days", "Absent Days", "Salary Month", "Salary Year",
    "Basic", "HRA", "Special Allowance", "Bonus",
    "PF", "Pro Tax", "Snacks", "Bus", "Loan",
    "Net Salary"
]

if not os.path.exists(EXCEL_FILE):
    pd.DataFrame(columns=COLUMNS).to_excel(EXCEL_FILE, index=False)

# load
df = pd.read_excel(EXCEL_FILE)

# helper to coerce numeric fields safely
def safe_int(val, default=0):
    try:
        if pd.isna(val):
            return default
        # floats that are integer-like -> int
        return int(float(val))
    except Exception:
        return default

def calculate_totals(rowvals):
    basic = safe_int(rowvals.get("Basic", 0))
    hra = safe_int(rowvals.get("HRA", 0))
    special = safe_int(rowvals.get("Special Allowance", 0))
    bonus = safe_int(rowvals.get("Bonus", 0))
    pf = safe_int(rowvals.get("PF", 0))
    tax = safe_int(rowvals.get("Pro Tax", 0))
    snacks = safe_int(rowvals.get("Snacks", 0))
    bus = safe_int(rowvals.get("Bus", 0))
    loan = safe_int(rowvals.get("Loan", 0))

    total_earnings = basic + hra + special + bonus
    total_deductions = pf + tax + snacks + bus + loan
    net_salary = total_earnings - total_deductions
    return total_earnings, total_deductions, net_salary

def save_df(local_df):
    local_df.to_excel(EXCEL_FILE, index=False)

# ---- PDF generator using reportlab platypus (table layout) ----
def generate_salary_pdf_bytes(emp):
    """
    emp: dict-like with keys used in COLUMNS
    returns BytesIO with PDF content
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=18*mm, bottomMargin=18*mm)

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    heading = ParagraphStyle("Heading", parent=styles["Heading1"], alignment=1, fontSize=16)
    small_center = ParagraphStyle("small_center", parent=styles["Normal"], alignment=1, fontSize=10)
    bold = ParagraphStyle("Bold", parent=styles["Normal"], fontSize=10, leading=12)

    elements = []

    # Header
    elements.append(Paragraph("GLA University", heading))
    elements.append(Paragraph(f"Salary Slip - {emp.get('Salary Month','')} {emp.get('Salary Year','')}", small_center))
    elements.append(Spacer(1, 6))

    # Employee Info table (2 columns)
    doj_val = emp.get("DOJ", "")
    if isinstance(doj_val, pd.Timestamp):
        doj_val = doj_val.strftime("%d-%m-%Y")
    elif isinstance(doj_val, datetime.date):
        doj_val = doj_val.strftime("%d-%m-%Y")

    emp_info_data = [
        ["Employee Code", str(emp.get("Employee Code", "")), "Employee Name", str(emp.get("Name", ""))],
        ["Date of Joining", str(doj_val), "PF Number", str(emp.get("PF Number", ""))],
        ["Location", str(emp.get("Location", "")), "Department", str(emp.get("Department", ""))],
        ["Total Days", str(emp.get("Total Days", "")), "Absent Days", str(emp.get("Absent Days", ""))],
    ]
    table_emp = Table(emp_info_data, colWidths=[60*mm, 60*mm, 60*mm, 60*mm])
    table_emp.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("LINEBELOW", (0,0), (-1,-1), 0.25, colors.gray),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9)
    ]))
    elements.append(table_emp)
    elements.append(Spacer(1, 10))

    # Earnings and Deductions columns side-by-side
    # Build rows with labels and values
    basic = safe_int(emp.get("Basic", 0))
    hra = safe_int(emp.get("HRA", 0))
    special = safe_int(emp.get("Special Allowance", 0))
    bonus = safe_int(emp.get("Bonus", 0))
    pf = safe_int(emp.get("PF", 0))
    tax = safe_int(emp.get("Pro Tax", 0))
    snacks = safe_int(emp.get("Snacks", 0))
    bus = safe_int(emp.get("Bus", 0))
    loan = safe_int(emp.get("Loan", 0))

    earnings = [
        ["Basic", f"Rs. {basic:,.2f}"],
        ["HRA", f"Rs. {hra:,.2f}"],
        ["Special Allowance", f"Rs. {special:,.2f}"],
        ["Bonus", f"Rs. {bonus:,.2f}"],
    ]
    deductions = [
        ["PF", f"Rs. {pf:,.2f}"],
        ["Professional Tax", f"Rs. {tax:,.2f}"],
        ["Snacks", f"Rs. {snacks:,.2f}"],
        ["Bus", f"Rs. {bus:,.2f}"],
        ["Loan", f"Rs. {loan:,.2f}"],
    ]

    # Prepare combined table with headers
    max_rows = max(len(earnings), len(deductions))
    table_body = [["Earnings", "Amount", "Deductions", "Amount"]]
    for i in range(max_rows):
        left = earnings[i] if i < len(earnings) else ["", ""]
        right = deductions[i] if i < len(deductions) else ["", ""]
        table_body.append([left[0], left[1], right[0], right[1]])

    # Totals row
    total_earnings, total_deductions, net_salary = calculate_totals(emp)
    table_body.append(["", "", "", ""])
    table_body.append(["Total Earnings", f"Rs. {total_earnings:,.2f}", "Total Deductions", f"Rs. {total_deductions:,.2f}"])
    table_body.append(["Net Salary", f"Rs. {net_salary:,.2f}", "", ""])

    table_widths = [60*mm, 30*mm, 60*mm, 30*mm]
    table_main = Table(table_body, colWidths=table_widths, repeatRows=1)
    table_main.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (3,0), colors.HexColor("#e6f0ff")),  # header bg
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("LINEBELOW", (0,0), (-1,0), 1, colors.black),
        ("LINEBELOW", (0,1), (-1,-3), 0.25, colors.grey),
        ("BOX", (0,0), (-1,-1), 0.5, colors.black),
        ("GRID", (0,0), (-1,-4), 0.25, colors.grey),
        ("SPAN", (0,-1), (1,-1)),  # Net Salary span left two cols
        ("BACKGROUND", (0,-2), (3,-2), colors.whitesmoke),
        ("ALIGN", (1,1), (1,-1), "RIGHT"),
        ("ALIGN", (3,1), (3,-1), "RIGHT"),
    ]))

    elements.append(table_main)
    elements.append(Spacer(1, 18))

    # Footer: generated on and signature placeholder
    gen_on = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    footer_table = [
        [f"Generated On: {gen_on}", "", "Authorised Signatory", ""],
        ["", "", "", ""],
        ["", "", "", ""],
    ]
    tbl_footer = Table(footer_table, colWidths=[70*mm, 20*mm, 60*mm, 20*mm])
    tbl_footer.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (2,0), (2,0), "CENTER"),
    ]))
    elements.append(tbl_footer)

    doc.build(elements)
    buf.seek(0)
    return buf

# ---- Streamlit UI ----
st.set_page_config(page_title="Payroll Management — Professional UI", layout="wide")
st.title("Payroll Management System")

menu = st.sidebar.selectbox("Choose action", ["Dashboard", "Add / Edit Employee", "Generate Salary Slip", "Download Excel"])

# Dashboard
if menu == "Dashboard":
    st.subheader("Employee Records")
    st.markdown("Quick view of employee records saved in Excel.")
    if df.empty:
        st.info("No records yet. Go to 'Add / Edit Employee' to create records.")
    else:
        st.dataframe(df[COLUMNS].fillna(""), use_container_width=True)

# Add / Edit
elif menu == "Add / Edit Employee":
    st.subheader("Add or Edit Employee")
    col1, col2 = st.columns([1, 1])
    with col1:
        search_code = st.text_input("Search by Employee Code (to edit)", value="")
        if st.button("Load"):
            if search_code.strip() == "":
                st.warning("Enter an Employee Code to load.")
            else:
                record = df[df["Employee Code"].astype(str) == str(search_code.strip())]
                if record.empty:
                    st.warning("No record found — you can add a new one below.")
                else:
                    row = record.iloc[0]
                    st.session_state["loaded"] = True
                    # store loaded values in session_state for prefill
                    for col in COLUMNS:
                        st.session_state[f"_{col}"] = row.get(col, "")
                    st.success("Record loaded. Scroll down to edit and Save.")

    # Prefilled form values using session_state or defaults
    def get_pref(key, default=""):
        return st.session_state.get(f"_{key}", default)

    with st.form("employee_form", clear_on_submit=False):
        code = st.text_input("Employee Code", value=get_pref("Employee Code", ""))
        name = st.text_input("Name", value=get_pref("Name", ""))
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0 if get_pref("Gender", "Male") not in ["Male","Female","Other"] else ["Male","Female","Other"].index(get_pref("Gender","Male")))
        dob = st.date_input("DOB", value=(pd.to_datetime(get_pref("DOB")).date() if (get_pref("DOB") not in [None,""]) and pd.notna(get_pref("DOB")) else datetime.date(1990,1,1)), min_value=datetime.date(1960,1,1), max_value=datetime.date(2050,12,31))
        doj = st.date_input("DOJ", value=(pd.to_datetime(get_pref("DOJ")).date() if (get_pref("DOJ") not in [None,""]) and pd.notna(get_pref("DOJ")) else datetime.date(2010,1,1)), min_value=datetime.date(1960,1,1), max_value=datetime.date(2050,12,31))
        dept = st.text_input("Department", value=get_pref("Department",""))
        bank = st.text_input("Bank Name", value=get_pref("Bank Name",""))
        acc = st.text_input("Account No.", value=get_pref("Account No.",""))
        pan = st.text_input("PAN", value=get_pref("PAN",""))
        uan = st.text_input("UAN", value=get_pref("UAN",""))
        location = st.text_input("Location", value=get_pref("Location",""))
        pf_no = st.text_input("PF Number", value=get_pref("PF Number",""))

        colA, colB = st.columns(2)
        with colA:
            total_days = st.number_input("Total Days", min_value=0, max_value=31, value=safe_int(get_pref("Total Days",30)), step=1)
            absent_days = st.number_input("Absent Days", min_value=0, max_value=31, value=safe_int(get_pref("Absent Days",0)), step=1)
            salary_month = st.selectbox("Salary Month", ["January","February","March","April","May","June","July","August","September","October","November","December"], index=0 if get_pref("Salary Month","January") not in ["January","February","March","April","May","June","July","August","September","October","November","December"] else ["January","February","March","April","May","June","July","August","September","October","November","December"].index(get_pref("Salary Month","January")))
            salary_year = st.number_input("Salary Year", min_value=1960, max_value=2050, value=safe_int(get_pref("Salary Year", datetime.datetime.now().year)), step=1)

        with colB:
            basic = st.number_input("Basic", min_value=0, max_value=10_000_000, value=safe_int(get_pref("Basic",0)), step=1)
            hra = st.number_input("HRA", min_value=0, max_value=10_000_000, value=safe_int(get_pref("HRA",0)), step=1)
            special = st.number_input("Special Allowance", min_value=0, max_value=10_000_000, value=safe_int(get_pref("Special Allowance",0)), step=1)
            bonus = st.number_input("Bonus", min_value=0, max_value=10_000_000, value=safe_int(get_pref("Bonus",0)), step=1)
            pf = st.number_input("PF", min_value=0, max_value=10_000_000, value=safe_int(get_pref("PF",0)), step=1)
            pro_tax = st.number_input("Pro Tax", min_value=0, max_value=10_000_000, value=safe_int(get_pref("Pro Tax",0)), step=1)
            snacks = st.number_input("Snacks", min_value=0, max_value=10_000_000, value=safe_int(get_pref("Snacks",0)), step=1)
            bus = st.number_input("Bus", min_value=0, max_value=10_000_000, value=safe_int(get_pref("Bus",0)), step=1)
            loan = st.number_input("Loan", min_value=0, max_value=10_000_000, value=safe_int(get_pref("Loan",0)), step=1)

        save_btn = st.form_submit_button("Save / Update")

        if save_btn:
            if code.strip() == "" or name.strip() == "":
                st.error("Employee Code and Name are required.")
            else:
                # prepare row
                new_row = {
                    "Employee Code": str(code).strip(),
                    "Name": name.strip(),
                    "Gender": gender,
                    "DOB": dob,
                    "DOJ": doj,
                    "Department": dept.strip(),
                    "Bank Name": bank.strip(),
                    "Account No.": acc.strip(),
                    "PAN": pan.strip(),
                    "UAN": uan.strip(),
                    "Location": location.strip(),
                    "PF Number": pf_no.strip(),
                    "Total Days": int(total_days),
                    "Absent Days": int(absent_days),
                    "Salary Month": salary_month,
                    "Salary Year": int(salary_year),
                    "Basic": int(basic),
                    "HRA": int(hra),
                    "Special Allowance": int(special),
                    "Bonus": int(bonus),
                    "PF": int(pf),
                    "Pro Tax": int(pro_tax),
                    "Snacks": int(snacks),
                    "Bus": int(bus),
                    "Loan": int(loan),
                    "Net Salary": 0  # will compute below
                }
                te, td, net = calculate_totals(new_row)
                new_row["Net Salary"] = int(net)

                # update if exists else append
                idx = df[df["Employee Code"].astype(str) == str(code).strip()].index
                if len(idx) > 0:
                    df.loc[idx[0], list(new_row.keys())] = list(new_row.values())
                    save_df(df)
                    st.success("Record updated.")
                else:
                    df.loc[len(df)] = new_row
                    save_df(df)
                    st.success("Record added.")

# Generate Salary Slip
elif menu == "Generate Salary Slip":
    st.subheader("Generate Salary Slip (PDF)")
    if df.empty:
        st.info("No employee data available. Add employees first.")
    else:
        # show searchable selectbox with code - name
        display_list = df["Employee Code"].astype(str) + " — " + df["Name"].astype(str)
        selected = st.selectbox("Select Employee", options=display_list)
        if st.button("Generate & Download PDF"):
            code_selected = selected.split(" — ")[0].strip()
            emp_row = df[df["Employee Code"].astype(str) == str(code_selected)]
            if emp_row.empty:
                st.error("Selected employee not found in data.")
            else:
                emp = emp_row.iloc[0].to_dict()
                # ensure numeric types are ints
                for k in ["Basic","HRA","Special Allowance","Bonus","PF","Pro Tax","Snacks","Bus","Loan","Total Days","Absent Days","Salary Year"]:
                    emp[k] = safe_int(emp.get(k, 0))
                pdf_bytes = generate_salary_pdf_bytes(emp)
                st.download_button(
                    label="⬇ Download Salary Slip (PDF)",
                    data=pdf_bytes.getvalue(),
                    file_name=f"SalarySlip_{code_selected}.pdf",
                    mime="application/pdf"
                )

# Download Excel
elif menu == "Download Excel":
    st.subheader("Download current payroll Excel")
    excel_buf = BytesIO()
    df.to_excel(excel_buf, index=False)
    excel_buf.seek(0)
    st.download_button("📥 Download Excel", data=excel_buf.getvalue(), file_name="Payroll_Management_Data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
