🏦 Banking Management System

A secure and feature-rich Banking Management System built using Python and PostgreSQL.
This project simulates real-world banking operations such as account creation, transactions, and audit tracking using a Command Line Interface (CLI).

🚀 Features
👤 Account Management

Create new bank accounts

Update account details (name & PIN)

Delete/close accounts securely

🔐 Security

PIN-based authentication

Secure PIN storage using SHA-256 hashing

Verification system for login

💰 Banking Operations

Deposit money

Withdraw money

Check account balance

Transaction history tracking

📜 Audit & Logging System

Every action is logged (deposit, withdraw, login, etc.)

View:

Individual account logs

All system logs (Admin)

Clear logs (Admin control)

👨‍💼 Admin Features

Special Admin account access

View all audit logs

Clear logs globally or per user

🛠️ Tech Stack

Language: Python

Database: PostgreSQL

Database Connector: psycopg2

Security: hashlib (SHA-256 encryption)

📂 Project Structure

Banking-Management-System/

    ├── main.py              # Main CLI application
    ├── database.py          # Database connection
    ├── requirements.txt     # Dependencies
    └── README.md            # Project Documentation

🗄️ Database Design
📌 Tables
1. accounts

account_number (Primary Key)

name

pin (hashed)

balance

created_at

2. audit_table

id (Primary Key)

account_number (Foreign Key)

holder_name

action

amount

timestamp

🔐 Security Implementation

PIN is never stored in plain text

Uses:

hashlib.sha256(pin.encode()).hexdigest()

Secure login verification system
