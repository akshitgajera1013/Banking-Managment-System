# Modern Streamlit UI for Bank Management System
# User + Admin Portal (Admin = holder name "Admin")

import streamlit as st
from main import BankSystem, Audit
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Bank",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    .block-container {padding-top: 2rem;}
    .stMetric {background: #0e1117; padding: 20px; border-radius: 12px;}
    .card {
        background: #161b22;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .title {font-size: 28px; font-weight: 700;}
    .subtitle {color: #9ca3af;}
</style>
""", unsafe_allow_html=True)

# ---------------- INIT ----------------
bank = BankSystem()

if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.account = None
    st.session_state.pin = None

# ---------------- HELPERS ----------------
def logout():
    st.session_state.auth = False
    st.session_state.account = None
    st.session_state.pin = None
    st.success("Logged out successfully")

def is_admin(account):
    return account and account.get_name() == "Admin"

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🏦 Smart Bank")
    st.caption("Secure Banking System")

    if not st.session_state.auth:
        page = st.radio("Navigation", ["Home", "Create Account", "Login"])
    else:
        if is_admin(st.session_state.account):
            page = st.radio(
                "Navigation",
                [
                    "Admin Dashboard",
                    "All Audit Logs",
                    "Single Account Logs",
                    "Clear Audit Logs",
                    "Logout"
                ]
            )
        else:
            page = st.radio(
                "Navigation",
                [
                    "Dashboard",
                    "Deposit",
                    "Withdraw",
                    "Transaction History",
                    "Update Profile",
                    "Change PIN",
                    "Delete Account",
                    "Logout"
                ]
            )

# ---------------- HOME ----------------
if page == "Home":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='title'>Welcome to Smart Bank</div>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Modern, Secure & Reliable Banking System</p>", unsafe_allow_html=True)
    st.markdown("""
    ✔ Account Creation  
    ✔ Secure Login  
    ✔ Deposit & Withdraw  
    ✔ Audit Logs  
    ✔ PostgreSQL Backend  
    ✔ Streamlit Modern UI
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- CREATE ACCOUNT ----------------
elif page == "Create Account":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🆕 Create New Account")

    name = st.text_input("Full Name")
    pin = st.text_input("4 Digit PIN", type="password", max_chars=4)
    cpin = st.text_input("Confirm PIN", type="password", max_chars=4)

    if st.button("Create Account", use_container_width=True):
        if not name or not pin:
            st.error("All fields required")
        elif pin != cpin:
            st.error("PIN mismatch")
        else:
            acc = bank.create_account(name, pin)
            if acc:
                st.success("Account created successfully")
                st.code(acc.get_account_number())
            else:
                st.error("Account creation failed")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
elif page == "Login":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🔐 Login")

    acc_no = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password", max_chars=4)

    if st.button("Login", use_container_width=True):
        acc = bank.read_account(acc_no, pin)
        if acc:
            st.session_state.auth = True
            st.session_state.account = acc
            st.session_state.pin = pin
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)

# ================= USER PAGES =================

elif page == "Dashboard":
    acc = st.session_state.account
    bal = bank.get_account_balance(acc.get_account_number(), st.session_state.pin)

    c1, c2, c3 = st.columns(3)
    c1.metric("Account Holder", acc.get_name())
    c2.metric("Account Number", acc.get_account_number())
    c3.metric("Balance", f"₹ {bal:.2f}")

elif page == "Deposit":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 💰 Deposit")

    amount = st.number_input("Amount", min_value=1.0)
    if st.button("Deposit", use_container_width=True):
        if bank.deposite(st.session_state.account.get_account_number(), st.session_state.pin, amount):
            st.success("Deposit successful")
        else:
            st.error("Deposit failed")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Withdraw":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 💸 Withdraw")

    amount = st.number_input("Amount", min_value=1.0)
    if st.button("Withdraw", use_container_width=True):
        if bank.withdraw(st.session_state.account.get_account_number(), st.session_state.pin, amount):
            st.success("Withdrawal successful")
        else:
            st.error("Insufficient balance")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Transaction History":
    logs = bank.get_single_audit_logs(st.session_state.account.get_account_number())
    if logs:
        df = pd.DataFrame(logs)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No transactions found")

elif page == "Update Profile":
    new_name = st.text_input("New Name")
    if st.button("Update Name", use_container_width=True):
        st.session_state.account.set_name(new_name)
        bank.update_account(st.session_state.account)
        Audit.log_action(
            st.session_state.account.get_account_number(),
            new_name,
            "Name Updated",
            0.0
        )
        st.success("Name updated")

elif page == "Change PIN":
    old = st.text_input("Old PIN", type="password")
    new = st.text_input("New PIN", type="password")
    cnew = st.text_input("Confirm New PIN", type="password")

    if st.button("Change PIN", use_container_width=True):
        if old != st.session_state.pin:
            st.error("Wrong PIN")
        elif new != cnew:
            st.error("PIN mismatch")
        else:
            st.session_state.account.set_pin(new)
            bank.update_account(st.session_state.account)
            Audit.log_action(
                st.session_state.account.get_account_number(),
                st.session_state.account.get_name(),
                "PIN Updated",
                0.0
            )
            logout()

elif page == "Delete Account":
    st.error("⚠ This action is permanent")
    confirm = st.text_input("Type DELETE to confirm")

    if st.button("Delete Account", use_container_width=True):
        if confirm == "DELETE":
            bank.delete_account(
                st.session_state.account.get_account_number(),
                st.session_state.pin
            )
            logout()
        else:
            st.error("Confirmation failed")

# ================= ADMIN PAGES =================

elif page == "Admin Dashboard":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🛡️ Admin Dashboard")
    logs = bank.get_all_audit_logs()
    st.metric("Total Audit Logs", len(logs) if logs else 0)
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "All Audit Logs":
    logs = bank.get_all_audit_logs()
    if logs:
        df = pd.DataFrame(logs)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No audit logs found")

elif page == "Single Account Logs":
    acc_no = st.text_input("Account Number")
    if st.button("Fetch Logs"):
        logs = bank.get_single_audit_logs(acc_no)
        if logs:
            df = pd.DataFrame(logs)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No logs found")

elif page == "Clear Audit Logs":
    st.error("⚠ Danger Zone")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Clear ALL Logs"):
            bank.clear_all_audit_logs()
            st.success("All audit logs cleared")

    with col2:
        acc_no = st.text_input("Account Number to Clear")
        if st.button("Clear Selected Logs"):
            bank.clear_single_audit_logs(acc_no)
            st.success("Selected account logs cleared")

# ---------------- LOGOUT ----------------
elif page == "Logout":
    logout()
