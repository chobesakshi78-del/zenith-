from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from backend.data.database import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(String(32), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    city = Column(String(64), nullable=False)
    state = Column(String(64), default="Maharashtra")

    employees = relationship("Employee", back_populates="branch")
    customers = relationship("Customer", back_populates="home_branch")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(String(32), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False)
    role = Column(String(64), nullable=False)  # Customer Service Officer, Teller, Loan Officer, Branch Manager
    branch_id = Column(String(32), ForeignKey("branches.id"), nullable=False)
    authorized_customer_range = Column(String(64), default="")

    branch = relationship("Branch", back_populates="employees")
    access_rights = relationship("EmployeeAccessRight", back_populates="employee")
    access_logs = relationship("AccessLog", back_populates="employee")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(32), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    phone = Column(String(32), nullable=False)
    email = Column(String(128), nullable=False)
    home_branch_id = Column(String(32), ForeignKey("branches.id"), nullable=False)
    risk_rating = Column(String(16), default="LOW")  # LOW, MEDIUM, HIGH
    occupation = Column(String(64), default="Salaried")

    home_branch = relationship("Branch", back_populates="customers")
    accounts = relationship("Account", back_populates="customer")
    access_logs = relationship("AccessLog", back_populates="customer")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String(32), primary_key=True, index=True)
    customer_id = Column(String(32), ForeignKey("customers.id"), nullable=False)
    account_type = Column(String(32), default="SAVINGS")  # SAVINGS, CURRENT
    balance = Column(Float, default=100000.0)
    status = Column(String(16), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="accounts")


class EmployeeAccessRight(Base):
    __tablename__ = "employee_access_rights"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(32), ForeignKey("employees.id"), nullable=False)
    authorized_branch_id = Column(String(32), ForeignKey("branches.id"), nullable=False)
    customer_id_start = Column(String(32), default="")
    customer_id_end = Column(String(32), default="")
    allowed_actions = Column(String(128), default="LOGIN,VIEW_ACCOUNT,MODIFY_DETAILS,VIEW_TRANSACTIONS")

    employee = relationship("Employee", back_populates="access_rights")


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(String(32), primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    employee_id = Column(String(32), ForeignKey("employees.id"), nullable=False, index=True)
    customer_id = Column(String(32), ForeignKey("customers.id"), nullable=True, index=True)
    action = Column(String(64), nullable=False)  # LOGIN, VIEW_ACCOUNT, MODIFY_DETAILS, VIEW_TRANSACTIONS
    ip_address = Column(String(45), default="10.14.2.100")
    service_ticket_id = Column(String(64), nullable=True)  # Populated for approved cross-branch access
    is_after_hours = Column(Boolean, default=False)

    employee = relationship("Employee", back_populates="access_logs")
    customer = relationship("Customer", back_populates="access_logs")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(32), primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    from_account_id = Column(String(32), ForeignKey("accounts.id"), nullable=False, index=True)
    to_account_id = Column(String(32), ForeignKey("accounts.id"), nullable=False, index=True)
    from_customer_id = Column(String(32), ForeignKey("customers.id"), nullable=False, index=True)
    to_customer_id = Column(String(32), ForeignKey("customers.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    txn_type = Column(String(32), default="TRANSFER")  # TRANSFER, SALARY, BILL_PAYMENT, BUSINESS, LOAN_DISBURSEMENT, LOAN_REPAYMENT, REFUND
    channel = Column(String(16), default="IMPS")  # IMPS, NEFT, RTGS, UPI
    description = Column(String(255), default="")


class GroundTruth(Base):
    __tablename__ = "ground_truth"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(String(64), unique=True, nullable=False)
    label = Column(String(16), nullable=False)  # SUSPICIOUS, BENIGN
    employee_id = Column(String(32), nullable=True)
    primary_customer_id = Column(String(32), nullable=True)
    involved_customers = Column(Text, default="[]")  # JSON list
    involved_transactions = Column(Text, default="[]")  # JSON list
    involved_access_logs = Column(Text, default="[]")  # JSON list
    pattern_type = Column(String(64), nullable=False)
    description = Column(Text, nullable=False)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(32), primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    employee_id = Column(String(32), ForeignKey("employees.id"), nullable=True, index=True)
    customer_id = Column(String(32), ForeignKey("customers.id"), nullable=False, index=True)
    alert_type = Column(String(64), nullable=False)
    risk_score = Column(Float, nullable=False)  # 0 to 100
    risk_level = Column(String(16), nullable=False)  # Low, Medium, High
    status = Column(String(16), default="Open")  # Open, In Review, Escalated, Closed
    signals_json = Column(Text, default="[]")  # JSON list of signal metrics
    explanation_narrative = Column(Text, default="")
    counterfactual_summary = Column(Text, default="")
    similar_cases_count = Column(Integer, default=0)
    involved_accounts = Column(Text, default="[]")
    involved_customers = Column(Text, default="[]")
    involved_transactions = Column(Text, default="[]")
    involved_access_logs = Column(Text, default="[]")
    lead_reason = Column(String(255), default="")


class Case(Base):
    __tablename__ = "cases"

    id = Column(String(32), primary_key=True, index=True)
    alert_id = Column(String(32), ForeignKey("alerts.id"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(32), default="Open")  # Open, In Review, Escalated, Closed
    assigned_investigator = Column(String(128), default="Unassigned")
    priority = Column(String(16), default="High")  # Low, Medium, High, Critical
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    summary = Column(Text, default="")


class CaseNote(Base):
    __tablename__ = "case_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(32), ForeignKey("cases.id"), nullable=False, index=True)
    author = Column(String(128), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    note_text = Column(Text, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(32), nullable=True, index=True)
    actor = Column(String(128), nullable=False)
    action = Column(String(64), nullable=False)
    details = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip_address = Column(String(45), default="127.0.0.1")
