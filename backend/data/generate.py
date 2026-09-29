import os
import sys
import json
import random
from datetime import datetime, timedelta
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.data.database import engine, SessionLocal, Base
from backend.data.models import (
    Branch, Employee, Customer, Account, EmployeeAccessRight,
    AccessLog, Transaction, GroundTruth, Alert, Case, CaseNote, AuditLog
)

CSV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "csv")
os.makedirs(CSV_DIR, exist_ok=True)

# Fixed seed for reproducibility
random.seed(42)

FIRST_NAMES = [
    "Aarav", "Ananya", "Rohan", "Pooja", "Vikram", "Sneha", "Aditya", "Neha",
    "Kavita", "Suresh", "Priya", "Rahul", "Deepak", "Sunita", "Rajesh", "Meera",
    "Amit", "Swati", "Nikhil", "Divya", "Gaurav", "Anil", "Sanjay", "Tanvi",
    "Manish", "Shilpa", "Kunal", "Ritu", "Alok", "Preeti", "Sachin", "Jyoti"
]
LAST_NAMES = [
    "Sharma", "Patel", "Kulkarni", "Deshmukh", "Joshi", "Verma", "Shinde",
    "Pawar", "Mehta", "Chavan", "Shah", "Gupta", "Bhosale", "More", "Bhat",
    "Trivedi", "Iyer", "Nair", "Reddy", "Choudhury", "Gadkari", "Thakur"
]

ROLES = [
    "Customer Service Officer",
    "Teller",
    "Loan Officer",
    "Branch Manager"
]

BRANCH_DEFS = [
    {"id": "BR_PUNE", "name": "Pune Shivajinagar Branch", "city": "Pune", "state": "Maharashtra"},
    {"id": "BR_MUMBAI", "name": "Mumbai Nariman Point Branch", "city": "Mumbai", "state": "Maharashtra"},
    {"id": "BR_NAGPUR", "name": "Nagpur Civil Lines Branch", "city": "Nagpur", "state": "Maharashtra"},
]


def generate_all_data():
    print("[*] Recreating database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    base_time = datetime(2026, 9, 28, 9, 0, 0)

    # 1. Branches
    print("[*] Generating Branches...")
    branches = []
    for b in BRANCH_DEFS:
        branch = Branch(id=b["id"], name=b["name"], city=b["city"], state=b["state"])
        db.add(branch)
        branches.append(branch)
    db.commit()

    # 2. Employees (40 total)
    print("[*] Generating Employees & Access Rights...")
    employees = []
    # Explicit Hero Employee E102
    e102 = Employee(
        id="E102",
        name="Anil Kulkarni",
        email="anil.kulkarni@zenithguard.bank",
        role="Customer Service Officer",
        branch_id="BR_PUNE",
        authorized_customer_range="C100-C180"
    )
    db.add(e102)
    employees.append(e102)

    # Collusion ring employees: E108 and E115
    e108 = Employee(
        id="E108",
        name="Sanjay Pawar",
        email="sanjay.pawar@zenithguard.bank",
        role="Customer Service Officer",
        branch_id="BR_MUMBAI",
        authorized_customer_range="C200-C270"
    )
    db.add(e108)
    employees.append(e108)

    e115 = Employee(
        id="E115",
        name="Gaurav Mehta",
        email="gaurav.mehta@zenithguard.bank",
        role="Teller",
        branch_id="BR_MUMBAI",
        authorized_customer_range="C200-C270"
    )
    db.add(e115)
    employees.append(e115)

    # Bulk snooper: E124
    e124 = Employee(
        id="E124",
        name="Sunita Deshmukh",
        email="sunita.deshmukh@zenithguard.bank",
        role="Loan Officer",
        branch_id="BR_NAGPUR",
        authorized_customer_range="C320-C400"
    )
    db.add(e124)
    employees.append(e124)

    # Approved cross-branch employee: E105
    e105 = Employee(
        id="E105",
        name="Pooja Verma",
        email="pooja.verma@zenithguard.bank",
        role="Customer Service Officer",
        branch_id="BR_PUNE",
        authorized_customer_range="C100-C180"
    )
    db.add(e105)
    employees.append(e105)

    # Generate remaining 35 employees (total 40)
    created_ids = {"E102", "E108", "E115", "E124", "E105"}
    emp_idx = 101
    while len(employees) < 40:
        emp_id = f"E{emp_idx}"
        emp_idx += 1
        if emp_id in created_ids:
            continue
        branch = random.choice(branches)
        role = random.choice(ROLES)
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        email = f"{name.lower().replace(' ', '.')}@zenithguard.bank"
        if branch.id == "BR_PUNE":
            auth_range = "C100-C199"
        elif branch.id == "BR_MUMBAI":
            auth_range = "C200-C319"
        else:
            auth_range = "C320-C499"
        emp = Employee(
            id=emp_id,
            name=name,
            email=email,
            role=role,
            branch_id=branch.id,
            authorized_customer_range=auth_range
        )
        db.add(emp)
        employees.append(emp)
    db.commit()

    # Employee Access Rights Table
    access_rights = []
    for emp in employees:
        parts = emp.authorized_customer_range.split("-")
        c_start = parts[0] if len(parts) == 2 else "C100"
        c_end = parts[1] if len(parts) == 2 else "C499"
        ear = EmployeeAccessRight(
            employee_id=emp.id,
            authorized_branch_id=emp.branch_id,
            customer_id_start=c_start,
            customer_id_end=c_end,
            allowed_actions="LOGIN,VIEW_ACCOUNT,MODIFY_DETAILS,VIEW_TRANSACTIONS"
        )
        db.add(ear)
        access_rights.append(ear)
    db.commit()

    # 3. Customers (400 customers C100..C499) + ensure C731 exists for the hero cycle
    print("[*] Generating Customers and Accounts...")
    customers = []
    accounts = []
    customer_ids = [f"C{i}" for i in range(100, 500)]
    if "C731" not in customer_ids:
        customer_ids.append("C731")

    # Map customers to branches
    # C100-C199: Pune, C200-C319: Mumbai, C320-C499: Nagpur, C731: Mumbai
    cust_branch_map = {}
    for cid in customer_ids:
        num = int(cid[1:])
        if num < 200:
            b_id = "BR_PUNE"
        elif num < 320:
            b_id = "BR_MUMBAI"
        elif num < 500:
            b_id = "BR_NAGPUR"
        else:
            b_id = "BR_MUMBAI"  # C731 Mumbai
        cust_branch_map[cid] = b_id

    # Hero special customers
    # C417: Mumbai customer
    cust_branch_map["C417"] = "BR_MUMBAI"
    # C208: Mumbai customer
    cust_branch_map["C208"] = "BR_MUMBAI"
    # C731: Mumbai customer
    cust_branch_map["C731"] = "BR_MUMBAI"

    occupations = ["Salaried Software Engineer", "Business Owner", "Doctor", "Chartered Accountant", "Teacher", "Retail Merchant"]

    acc_idx = 1001
    for cid in customer_ids:
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if cid == "C417":
            name = "Kavita Shah"
        elif cid == "C208":
            name = "Rohan Deshmukh"
        elif cid == "C731":
            name = "Sunita Pawar"
        elif cid == "C142":
            name = "Deepak Verma"
        elif cid == "C250":
            name = "Vikram Reddy"
        elif cid == "C310":
            name = "Tanvi Gadkari"
        elif cid == "C350":
            name = "Nikhil Joshi"
        elif cid == "C160":
            name = "Sachin Gupta"
        elif cid == "C161":
            name = "Meera Gupta"
        elif cid == "C162":
            name = "Suresh Gupta"
        elif cid == "C220":
            name = "Shree Enterprises (Prop: Alok More)"
        elif cid == "C180":
            name = "Rajesh Bhat"

        c = Customer(
            id=cid,
            name=name,
            phone=f"+91 98{random.randint(10000000, 99999999)}",
            email=f"{cid.lower()}@{name.split()[0].lower()}corp.in",
            home_branch_id=cust_branch_map[cid],
            risk_rating="HIGH" if cid in ["C417", "C208", "C731", "C142", "C250"] else "LOW",
            occupation=random.choice(occupations) if not cid == "C220" else "Commercial Trading"
        )
        db.add(c)
        customers.append(c)

        # 1-2 accounts per customer (~600 accounts total)
        num_accs = 2 if random.random() < 0.5 or cid in ["C417", "C208", "C731", "C220"] else 1
        for j in range(num_accs):
            acc = Account(
                id=f"ACC_{cid}_{j+1}",
                customer_id=cid,
                account_type="SAVINGS" if j == 0 else "CURRENT",
                balance=round(random.uniform(50000, 500000), 2),
                status="ACTIVE",
                created_at=base_time - timedelta(days=random.randint(100, 1000))
            )
            db.add(acc)
            accounts.append(acc)
    db.commit()

    # Create account lookup map: customer_id -> primary_account_id
    cust_to_acc = {}
    for acc in accounts:
        if acc.customer_id not in cust_to_acc:
            cust_to_acc[acc.customer_id] = acc.id

    # 4. Standard Access Logs (~4,800 normal access logs across 30 days)
    print("[*] Generating baseline normal Access Logs (~4,800 events)...")
    access_logs = []
    log_idx = 10000

    start_date = base_time - timedelta(days=30)
    for _ in range(4800):
        log_idx += 1
        emp = random.choice(employees)
        # 96% authorized access within employee's branch customer pool
        if random.random() < 0.96:
            valid_cids = [c.id for c in customers if c.home_branch_id == emp.branch_id]
            cid = random.choice(valid_cids) if valid_cids else random.choice(customers).id
        else:
            # 4% accidental cross-branch query (benign noise)
            cid = random.choice(customers).id

        day_offset = random.randint(0, 29)
        # Mostly business hours 9am to 6pm
        if random.random() < 0.92:
            hour = random.randint(9, 17)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            is_after = False
        else:
            hour = random.choice([7, 8, 19, 20, 21])
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            is_after = True

        log_time = start_date + timedelta(days=day_offset, hours=hour, minutes=minute, seconds=second)
        action = random.choices(
            ["LOGIN", "VIEW_ACCOUNT", "VIEW_TRANSACTIONS", "MODIFY_DETAILS"],
            weights=[0.3, 0.45, 0.20, 0.05]
        )[0]

        log = AccessLog(
            id=f"LOG_{log_idx}",
            timestamp=log_time,
            employee_id=emp.id,
            customer_id=cid,
            action=action,
            ip_address=f"10.14.{random.randint(1, 3)}.{random.randint(10, 250)}",
            service_ticket_id=None,
            is_after_hours=is_after
        )
        db.add(log)
        access_logs.append(log)

    # 5. Standard Normal Transactions (~7,900 baseline transactions)
    print("[*] Generating baseline normal Transactions (~7,900 events)...")
    transactions = []
    txn_idx = 10000

    txn_types = ["TRANSFER", "SALARY", "BILL_PAYMENT", "BUSINESS"]
    channels = ["IMPS", "NEFT", "UPI", "RTGS"]

    for _ in range(7900):
        txn_idx += 1
        c_from = random.choice(customers)
        c_to = random.choice(customers)
        while c_to.id == c_from.id:
            c_to = random.choice(customers)

        day_offset = random.randint(0, 29)
        hour = random.randint(8, 22)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        t_time = start_date + timedelta(days=day_offset, hours=hour, minutes=minute, seconds=second)

        # Baseline amount distribution (mostly under 30k, occasional high)
        if random.random() < 0.8:
            amt = round(random.uniform(500, 28000), 2)
        elif random.random() < 0.95:
            amt = round(random.uniform(30000, 75000), 2)
        else:
            amt = round(random.uniform(75000, 250000), 2)

        t_type = random.choice(txn_types)
        t = Transaction(
            id=f"TXN_{txn_idx}",
            timestamp=t_time,
            from_account_id=cust_to_acc[c_from.id],
            to_account_id=cust_to_acc[c_to.id],
            from_customer_id=c_from.id,
            to_customer_id=c_to.id,
            amount=amt,
            txn_type=t_type,
            channel=random.choice(channels),
            description=f"Standard {t_type.lower()} transfer"
        )
        db.add(t)
        transactions.append(t)

    db.commit()

    # 6. INJECT GROUND-TRUTH SCENARIOS
    print("[*] Injecting labelled test scenarios & ground truth...")
    ground_truths = []

    # -------------------------------------------------------------
    # SCENARIO 1: HERO CASE
    # Employee E102 (Anil, Pune CSO, authorized for C100-C180)
    # 2026-09-28:
    # 09:58 Login
    # 10:00 View C417 (Mumbai customer - UNAUTHORIZED)
    # 10:01 Modify details C417
    # 10:02 View transactions C417
    # 10:05 C417 -> C208 ₹49,000 (Lag: 5 mins after 10:00 view, 4 mins after modify)
    # 10:08 C208 -> C731 ₹48,500
    # 10:12 C731 -> C417 ₹47,900
    # (Circular, structured just under ₹50,000 threshold)
    # PLUS 2 similar earlier cases by E102 (14 days ago and 28 days ago)
    # -------------------------------------------------------------
    hero_date = datetime(2026, 9, 28)
    hero_logs = [
        AccessLog(id="LOG_HERO_01", timestamp=hero_date.replace(hour=9, minute=58, second=0), employee_id="E102", customer_id=None, action="LOGIN", ip_address="10.14.1.42", is_after_hours=False),
        AccessLog(id="LOG_HERO_02", timestamp=hero_date.replace(hour=10, minute=0, second=15), employee_id="E102", customer_id="C417", action="VIEW_ACCOUNT", ip_address="10.14.1.42", is_after_hours=False),
        AccessLog(id="LOG_HERO_03", timestamp=hero_date.replace(hour=10, minute=1, second=20), employee_id="E102", customer_id="C417", action="MODIFY_DETAILS", ip_address="10.14.1.42", is_after_hours=False),
        AccessLog(id="LOG_HERO_04", timestamp=hero_date.replace(hour=10, minute=2, second=45), employee_id="E102", customer_id="C417", action="VIEW_TRANSACTIONS", ip_address="10.14.1.42", is_after_hours=False),
    ]
    for hl in hero_logs:
        db.add(hl)
        access_logs.append(hl)

    hero_txns = [
        Transaction(id="TXN_HERO_01", timestamp=hero_date.replace(hour=10, minute=5, second=0), from_account_id=cust_to_acc["C417"], to_account_id=cust_to_acc["C208"], from_customer_id="C417", to_customer_id="C208", amount=49000.0, txn_type="TRANSFER", channel="IMPS", description="Urgent Settlement Ref 49A"),
        Transaction(id="TXN_HERO_02", timestamp=hero_date.replace(hour=10, minute=8, second=0), from_account_id=cust_to_acc["C208"], to_account_id=cust_to_acc["C731"], from_customer_id="C208", to_customer_id="C731", amount=48500.0, txn_type="TRANSFER", channel="IMPS", description="Interim Transfer Ref 48B"),
        Transaction(id="TXN_HERO_03", timestamp=hero_date.replace(hour=10, minute=12, second=0), from_account_id=cust_to_acc["C731"], to_account_id=cust_to_acc["C417"], from_customer_id="C731", to_customer_id="C417", amount=47900.0, txn_type="TRANSFER", channel="IMPS", description="Return Clearing Ref 47C"),
    ]
    for ht in hero_txns:
        db.add(ht)
        transactions.append(ht)

    # 2 Earlier similar cases for E102
    # Prior Case 1 (14 days ago): E102 accesses unauthorized C410 (Mumbai), modifies details, circular C410 -> C205 -> C731 -> C410 with ₹49,200 / ₹48,700 / ₹48,000
    p1_date = hero_date - timedelta(days=14)
    p1_logs = [
        AccessLog(id="LOG_PRIOR1_01", timestamp=p1_date.replace(hour=11, minute=10), employee_id="E102", customer_id="C410", action="VIEW_ACCOUNT", ip_address="10.14.1.42"),
        AccessLog(id="LOG_PRIOR1_02", timestamp=p1_date.replace(hour=11, minute=12), employee_id="E102", customer_id="C410", action="MODIFY_DETAILS", ip_address="10.14.1.42"),
    ]
    for pl in p1_logs:
        db.add(pl)
        access_logs.append(pl)
    p1_txns = [
        Transaction(id="TXN_PRIOR1_01", timestamp=p1_date.replace(hour=11, minute=17), from_account_id=cust_to_acc["C410"], to_account_id=cust_to_acc["C205"], from_customer_id="C410", to_customer_id="C205", amount=49200.0, txn_type="TRANSFER", channel="IMPS", description="Prior Batch Alpha 1"),
        Transaction(id="TXN_PRIOR1_02", timestamp=p1_date.replace(hour=11, minute=21), from_account_id=cust_to_acc["C205"], to_account_id=cust_to_acc["C731"], from_customer_id="C205", to_customer_id="C731", amount=48700.0, txn_type="TRANSFER", channel="IMPS", description="Prior Batch Alpha 2"),
        Transaction(id="TXN_PRIOR1_03", timestamp=p1_date.replace(hour=11, minute=26), from_account_id=cust_to_acc["C731"], to_account_id=cust_to_acc["C410"], from_customer_id="C731", to_customer_id="C410", amount=48000.0, txn_type="TRANSFER", channel="IMPS", description="Prior Batch Alpha 3"),
    ]
    for pt in p1_txns:
        db.add(pt)
        transactions.append(pt)

    # Prior Case 2 (28 days ago): E102 accesses unauthorized C412 (Mumbai), modifies details, circular C412 -> C210 -> C731 -> C412 with ₹49,500 / ₹48,900 / ₹48,200
    p2_date = hero_date - timedelta(days=28)
    p2_logs = [
        AccessLog(id="LOG_PRIOR2_01", timestamp=p2_date.replace(hour=14, minute=5), employee_id="E102", customer_id="C412", action="VIEW_ACCOUNT", ip_address="10.14.1.42"),
        AccessLog(id="LOG_PRIOR2_02", timestamp=p2_date.replace(hour=14, minute=7), employee_id="E102", customer_id="C412", action="MODIFY_DETAILS", ip_address="10.14.1.42"),
    ]
    for pl in p2_logs:
        db.add(pl)
        access_logs.append(pl)
    p2_txns = [
        Transaction(id="TXN_PRIOR2_01", timestamp=p2_date.replace(hour=14, minute=12), from_account_id=cust_to_acc["C412"], to_account_id=cust_to_acc["C210"], from_customer_id="C412", to_customer_id="C210", amount=49500.0, txn_type="TRANSFER", channel="IMPS", description="Prior Batch Beta 1"),
        Transaction(id="TXN_PRIOR2_02", timestamp=p2_date.replace(hour=14, minute=16), from_account_id=cust_to_acc["C210"], to_account_id=cust_to_acc["C731"], from_customer_id="C210", to_customer_id="C731", amount=48900.0, txn_type="TRANSFER", channel="IMPS", description="Prior Batch Beta 2"),
        Transaction(id="TXN_PRIOR2_03", timestamp=p2_date.replace(hour=14, minute=22), from_account_id=cust_to_acc["C731"], to_account_id=cust_to_acc["C412"], from_customer_id="C731", to_customer_id="C412", amount=48200.0, txn_type="TRANSFER", channel="IMPS", description="Prior Batch Beta 3"),
    ]
    for pt in p2_txns:
        db.add(pt)
        transactions.append(pt)

    gt_hero = GroundTruth(
        scenario_id="HERO_E102_C417",
        label="SUSPICIOUS",
        employee_id="E102",
        primary_customer_id="C417",
        involved_customers=json.dumps(["C417", "C208", "C731"]),
        involved_transactions=json.dumps(["TXN_HERO_01", "TXN_HERO_02", "TXN_HERO_03"]),
        involved_access_logs=json.dumps(["LOG_HERO_01", "LOG_HERO_02", "LOG_HERO_03", "LOG_HERO_04"]),
        pattern_type="HERO_INSIDER_CIRCULAR",
        description="Employee E102 outside branch accesses C417, modifies details, followed immediately by circular structured transfers C417->C208->C731->C417 below 50k threshold. 2 prior matching historical cases exist."
    )
    db.add(gt_hero)
    ground_truths.append(gt_hero)

    # -------------------------------------------------------------
    # SCENARIO 2: TRANSACTION SPLITTING / STRUCTURING
    # C142 makes 4 structured transfers within 3 hours just below ₹50,000 threshold
    # -------------------------------------------------------------
    split_date = hero_date - timedelta(days=2)
    split_txns = [
        Transaction(id="TXN_SPLIT_01", timestamp=split_date.replace(hour=11, minute=10), from_account_id=cust_to_acc["C142"], to_account_id=cust_to_acc["C201"], from_customer_id="C142", to_customer_id="C201", amount=49200.0, txn_type="TRANSFER", channel="UPI", description="Consulting installment 1"),
        Transaction(id="TXN_SPLIT_02", timestamp=split_date.replace(hour=11, minute=45), from_account_id=cust_to_acc["C142"], to_account_id=cust_to_acc["C202"], from_customer_id="C142", to_customer_id="C202", amount=49100.0, txn_type="TRANSFER", channel="UPI", description="Consulting installment 2"),
        Transaction(id="TXN_SPLIT_03", timestamp=split_date.replace(hour=12, minute=30), from_account_id=cust_to_acc["C142"], to_account_id=cust_to_acc["C203"], from_customer_id="C142", to_customer_id="C203", amount=48900.0, txn_type="TRANSFER", channel="UPI", description="Consulting installment 3"),
        Transaction(id="TXN_SPLIT_04", timestamp=split_date.replace(hour=13, minute=15), from_account_id=cust_to_acc["C142"], to_account_id=cust_to_acc["C204"], from_customer_id="C142", to_customer_id="C204", amount=49400.0, txn_type="TRANSFER", channel="UPI", description="Consulting installment 4"),
    ]
    for st in split_txns:
        db.add(st)
        transactions.append(st)

    gt_split = GroundTruth(
        scenario_id="SPLIT_C142",
        label="SUSPICIOUS",
        employee_id=None,
        primary_customer_id="C142",
        involved_customers=json.dumps(["C142", "C201", "C202", "C203", "C204"]),
        involved_transactions=json.dumps(["TXN_SPLIT_01", "TXN_SPLIT_02", "TXN_SPLIT_03", "TXN_SPLIT_04"]),
        involved_access_logs=json.dumps([]),
        pattern_type="TRANSACTION_SPLITTING",
        description="Repeated transfers clustered just below ₹50,000 threshold within a 3-hour window indicating structuring."
    )
    db.add(gt_split)
    ground_truths.append(gt_split)

    # -------------------------------------------------------------
    # SCENARIO 3: RAPID PASS-THROUGH
    # C250 receives ₹180,000 and sends ₹175,000 to C310 4 minutes later (>97% preserved)
    # Preceded by unauthorized inquiry from employee E110
    # -------------------------------------------------------------
    rapid_date = hero_date - timedelta(days=3)
    e110_log = AccessLog(id="LOG_RAPID_01", timestamp=rapid_date.replace(hour=14, minute=20), employee_id="E110", customer_id="C250", action="VIEW_ACCOUNT", ip_address="10.14.3.55")
    db.add(e110_log)
    access_logs.append(e110_log)

    rapid_txns = [
        Transaction(id="TXN_RAPID_01", timestamp=rapid_date.replace(hour=14, minute=25), from_account_id=cust_to_acc["C115"], to_account_id=cust_to_acc["C250"], from_customer_id="C115", to_customer_id="C250", amount=180000.0, txn_type="TRANSFER", channel="RTGS", description="Inbound escrow payment"),
        Transaction(id="TXN_RAPID_02", timestamp=rapid_date.replace(hour=14, minute=29), from_account_id=cust_to_acc["C250"], to_account_id=cust_to_acc["C310"], from_customer_id="C250", to_customer_id="C310", amount=175000.0, txn_type="TRANSFER", channel="RTGS", description="Fast forward remittance"),
    ]
    for rt in rapid_txns:
        db.add(rt)
        transactions.append(rt)

    gt_rapid = GroundTruth(
        scenario_id="RAPID_C250_C310",
        label="SUSPICIOUS",
        employee_id="E110",
        primary_customer_id="C250",
        involved_customers=json.dumps(["C115", "C250", "C310"]),
        involved_transactions=json.dumps(["TXN_RAPID_01", "TXN_RAPID_02"]),
        involved_access_logs=json.dumps(["LOG_RAPID_01"]),
        pattern_type="RAPID_MOVEMENT",
        description="Rapid movement of ₹175k forwarded 4 minutes after receipt (>97% preserved) following insider view."
    )
    db.add(gt_rapid)
    ground_truths.append(gt_rapid)

    # -------------------------------------------------------------
    # SCENARIO 4: COLLUSION RING
    # 2 employees (E108 and E115) repeatedly touch 4 accounts (C211, C212, C213, C214)
    # that execute circular trades among each other
    # -------------------------------------------------------------
    col_date = hero_date - timedelta(days=4)
    col_logs = [
        AccessLog(id="LOG_COL_01", timestamp=col_date.replace(hour=15, minute=0), employee_id="E108", customer_id="C211", action="MODIFY_DETAILS", ip_address="10.14.2.80"),
        AccessLog(id="LOG_COL_02", timestamp=col_date.replace(hour=15, minute=2), employee_id="E115", customer_id="C212", action="MODIFY_DETAILS", ip_address="10.14.2.81"),
        AccessLog(id="LOG_COL_03", timestamp=col_date.replace(hour=15, minute=5), employee_id="E108", customer_id="C213", action="VIEW_ACCOUNT", ip_address="10.14.2.80"),
        AccessLog(id="LOG_COL_04", timestamp=col_date.replace(hour=15, minute=7), employee_id="E115", customer_id="C214", action="VIEW_ACCOUNT", ip_address="10.14.2.81"),
    ]
    for cl in col_logs:
        db.add(cl)
        access_logs.append(cl)

    col_txns = [
        Transaction(id="TXN_COL_01", timestamp=col_date.replace(hour=15, minute=10), from_account_id=cust_to_acc["C211"], to_account_id=cust_to_acc["C212"], from_customer_id="C211", to_customer_id="C212", amount=85000.0, txn_type="TRANSFER", channel="NEFT", description="Ring leg 1"),
        Transaction(id="TXN_COL_02", timestamp=col_date.replace(hour=15, minute=16), from_account_id=cust_to_acc["C212"], to_account_id=cust_to_acc["C213"], from_customer_id="C212", to_customer_id="C213", amount=84200.0, txn_type="TRANSFER", channel="NEFT", description="Ring leg 2"),
        Transaction(id="TXN_COL_03", timestamp=col_date.replace(hour=15, minute=22), from_account_id=cust_to_acc["C213"], to_account_id=cust_to_acc["C214"], from_customer_id="C213", to_customer_id="C214", amount=83500.0, txn_type="TRANSFER", channel="NEFT", description="Ring leg 3"),
        Transaction(id="TXN_COL_04", timestamp=col_date.replace(hour=15, minute=30), from_account_id=cust_to_acc["C214"], to_account_id=cust_to_acc["C211"], from_customer_id="C214", to_customer_id="C211", amount=82900.0, txn_type="TRANSFER", channel="NEFT", description="Ring leg 4"),
    ]
    for ct in col_txns:
        db.add(ct)
        transactions.append(ct)

    gt_col = GroundTruth(
        scenario_id="COLLUSION_E108_E115",
        label="SUSPICIOUS",
        employee_id="E108,E115",
        primary_customer_id="C211",
        involved_customers=json.dumps(["C211", "C212", "C213", "C214"]),
        involved_transactions=json.dumps(["TXN_COL_01", "TXN_COL_02", "TXN_COL_03", "TXN_COL_04"]),
        involved_access_logs=json.dumps(["LOG_COL_01", "LOG_COL_02", "LOG_COL_03", "LOG_COL_04"]),
        pattern_type="COLLUSION_RING",
        description="Collusion ring: 2 employees (E108, E115) coordinated access across accounts C211-C214 followed by circular trading."
    )
    db.add(gt_col)
    ground_truths.append(gt_col)

    # -------------------------------------------------------------
    # SCENARIO 5: EXCESSIVE CUSTOMER DATA ACCESS (BULK / OFF-HOURS)
    # Employee E124 bulk viewing 45 distinct customers between 01:30 AM and 03:15 AM
    # -------------------------------------------------------------
    bulk_date = hero_date - timedelta(days=1)
    bulk_logs = []
    bulk_cids = [f"C{idx}" for idx in range(320, 365)]
    curr_t = bulk_date.replace(hour=1, minute=30)
    for idx, b_cid in enumerate(bulk_cids):
        curr_t += timedelta(minutes=random.randint(1, 2), seconds=random.randint(5, 30))
        b_log = AccessLog(
            id=f"LOG_BULK_{idx+1:03d}",
            timestamp=curr_t,
            employee_id="E124",
            customer_id=b_cid,
            action="VIEW_ACCOUNT",
            ip_address="192.168.10.45",
            is_after_hours=True
        )
        db.add(b_log)
        access_logs.append(b_log)
        bulk_logs.append(b_log.id)

    gt_bulk = GroundTruth(
        scenario_id="BULK_ACCESS_E124",
        label="SUSPICIOUS",
        employee_id="E124",
        primary_customer_id="C320",
        involved_customers=json.dumps(bulk_cids[:10]),
        involved_transactions=json.dumps([]),
        involved_access_logs=json.dumps(bulk_logs[:15]),
        pattern_type="BULK_OFF_HOURS",
        description="Employee E124 performed excessive off-hours customer record lookups (45 customer accounts accessed between 1:30 AM and 3:15 AM)."
    )
    db.add(gt_bulk)
    ground_truths.append(gt_bulk)

    # -------------------------------------------------------------
    # SCENARIO 6: LEGITIMATE LOOK-ALIKES (BENIGN GROUND TRUTH)
    # A) Approved cross-branch access with a service ticket
    # B) Salary credit followed by family transfers
    # C) High-frequency business owner payments
    # D) Legitimate circular loan disbursement and escrow refund
    # -------------------------------------------------------------
    legit_date = hero_date - timedelta(days=5)

    # 6A: Approved cross-branch with ticket
    tkt_log = AccessLog(
        id="LOG_LEGIT_TKT",
        timestamp=legit_date.replace(hour=11, minute=15),
        employee_id="E105",  # Pune CSO
        customer_id="C350",  # Nagpur Customer
        action="VIEW_ACCOUNT",
        ip_address="10.14.1.25",
        service_ticket_id="TKT-8921",
        is_after_hours=False
    )
    db.add(tkt_log)
    access_logs.append(tkt_log)

    gt_legit_tkt = GroundTruth(
        scenario_id="LEGIT_TICKET_C350",
        label="BENIGN",
        employee_id="E105",
        primary_customer_id="C350",
        involved_customers=json.dumps(["C350"]),
        involved_transactions=json.dumps([]),
        involved_access_logs=json.dumps(["LOG_LEGIT_TKT"]),
        pattern_type="APPROVED_SERVICE_TICKET",
        description="Cross-branch customer lookup authorized under IT Service Ticket TKT-8921 for KYC address update."
    )
    db.add(gt_legit_tkt)
    ground_truths.append(gt_legit_tkt)

    # 6B: Salary credit followed by family transfers
    sal_date = hero_date - timedelta(days=6)
    sal_txns = [
        Transaction(id="TXN_LEGIT_SAL_01", timestamp=sal_date.replace(hour=9, minute=30), from_account_id=cust_to_acc["C101"], to_account_id=cust_to_acc["C160"], from_customer_id="C101", to_customer_id="C160", amount=120000.0, txn_type="SALARY", channel="NEFT", description="Corporate Payroll Sept 2026"),
        Transaction(id="TXN_LEGIT_SAL_02", timestamp=sal_date.replace(hour=10, minute=15), from_account_id=cust_to_acc["C160"], to_account_id=cust_to_acc["C161"], from_customer_id="C160", to_customer_id="C161", amount=25000.0, txn_type="TRANSFER", channel="UPI", description="Monthly household transfer to spouse"),
        Transaction(id="TXN_LEGIT_SAL_03", timestamp=sal_date.replace(hour=10, minute=45), from_account_id=cust_to_acc["C160"], to_account_id=cust_to_acc["C162"], from_customer_id="C160", to_customer_id="C162", amount=15000.0, txn_type="TRANSFER", channel="UPI", description="Support allowance to father"),
    ]
    for st in sal_txns:
        db.add(st)
        transactions.append(st)

    gt_legit_sal = GroundTruth(
        scenario_id="LEGIT_SALARY_C160",
        label="BENIGN",
        employee_id=None,
        primary_customer_id="C160",
        involved_customers=json.dumps(["C160", "C161", "C162"]),
        involved_transactions=json.dumps(["TXN_LEGIT_SAL_01", "TXN_LEGIT_SAL_02", "TXN_LEGIT_SAL_03"]),
        involved_access_logs=json.dumps([]),
        pattern_type="SALARY_FAMILY",
        description="Legitimate corporate salary credit followed by routine family allowances within 2 hours."
    )
    db.add(gt_legit_sal)
    ground_truths.append(gt_legit_sal)

    # 6C: Business high-frequency merchant payments
    biz_date = hero_date - timedelta(days=7)
    biz_txns = [
        Transaction(id=f"TXN_LEGIT_BIZ_{i:02d}", timestamp=biz_date.replace(hour=10 + i, minute=random.randint(10, 50)), from_account_id=cust_to_acc["C220"], to_account_id=cust_to_acc[f"C{221+i}"], from_customer_id="C220", to_customer_id=f"C{221+i}", amount=round(random.uniform(15000, 45000), 2), txn_type="BUSINESS", channel="RTGS", description=f"Merchant supplier settlement #{i+101}")
        for i in range(5)
    ]
    for bt in biz_txns:
        db.add(bt)
        transactions.append(bt)

    gt_legit_biz = GroundTruth(
        scenario_id="LEGIT_BUSINESS_C220",
        label="BENIGN",
        employee_id=None,
        primary_customer_id="C220",
        involved_customers=json.dumps(["C220"] + [f"C{221+i}" for i in range(5)]),
        involved_transactions=json.dumps([t.id for t in biz_txns]),
        involved_access_logs=json.dumps([]),
        pattern_type="BUSINESS_HIGH_FREQ",
        description="Legitimate registered business owner executing routine supplier payments."
    )
    db.add(gt_legit_biz)
    ground_truths.append(gt_legit_biz)

    # 6D: Circular loan repayment / refund
    loan_date = hero_date - timedelta(days=8)
    loan_txns = [
        Transaction(id="TXN_LEGIT_LOAN_01", timestamp=loan_date.replace(hour=11, minute=0), from_account_id=cust_to_acc["C100"], to_account_id=cust_to_acc["C180"], from_customer_id="C100", to_customer_id="C180", amount=50000.0, txn_type="LOAN_DISBURSEMENT", channel="NEFT", description="Loan Advance Reference LN-5541"),
        Transaction(id="TXN_LEGIT_LOAN_02", timestamp=loan_date.replace(hour=11, minute=45), from_account_id=cust_to_acc["C180"], to_account_id=cust_to_acc["C100"], from_customer_id="C180", to_customer_id="C100", amount=50000.0, txn_type="REFUND", channel="NEFT", description="Cancellation and Refund Reference LN-5541"),
    ]
    for lt in loan_txns:
        db.add(lt)
        transactions.append(lt)

    gt_legit_loan = GroundTruth(
        scenario_id="LEGIT_LOAN_C180",
        label="BENIGN",
        employee_id=None,
        primary_customer_id="C180",
        involved_customers=json.dumps(["C180", "C100"]),
        involved_transactions=json.dumps(["TXN_LEGIT_LOAN_01", "TXN_LEGIT_LOAN_02"]),
        involved_access_logs=json.dumps([]),
        pattern_type="LOAN_ESCROW_REFUND",
        description="Legitimate loan advance disbursement promptly refunded due to client cancellation with matched reference."
    )
    db.add(gt_legit_loan)
    ground_truths.append(gt_legit_loan)

    db.commit()

    print("[*] Exporting CSV copies to backend/data/csv/...")
    export_tables_to_csv(db)

    db.close()
    print("[+] Phase 1 synthetic data generation complete!")
    print(f"    - Branches: {len(branches)}")
    print(f"    - Employees: {len(employees)}")
    print(f"    - Customers: {len(customers)}")
    print(f"    - Accounts: {len(accounts)}")
    print(f"    - Access Logs: {len(access_logs)}")
    print(f"    - Transactions: {len(transactions)}")
    print(f"    - Ground Truth Scenarios: {len(ground_truths)}")


def export_tables_to_csv(db):
    models = [
        ("branches", Branch),
        ("employees", Employee),
        ("customers", Customer),
        ("accounts", Account),
        ("employee_access_rights", EmployeeAccessRight),
        ("access_logs", AccessLog),
        ("transactions", Transaction),
        ("ground_truth", GroundTruth),
    ]
    for table_name, model_cls in models:
        records = db.query(model_cls).all()
        if not records:
            continue
        # Extract columns
        cols = [c.name for c in model_cls.__table__.columns]
        data = [{col: getattr(r, col) for col in cols} for r in records]
        df = pd.DataFrame(data)
        out_csv = os.path.join(CSV_DIR, f"{table_name}.csv")
        df.to_csv(out_csv, index=False)
        print(f"    Exported {len(df)} rows to {out_csv}")


if __name__ == "__main__":
    generate_all_data()
