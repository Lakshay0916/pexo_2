#!/usr/bin/env python3
"""Regenerates seed_dummy_data.sql with the original 5 named demo employees
(E001-E005, unchanged — their login accounts/contracts/payslips stay exactly
as they were) plus EMPLOYEE_COUNT-5 additional synthetic employees with
proportional bank accounts, contracts, attendance, and PTO allocations.

Run: python3 scripts/generate_seed_data.py > seed_dummy_data.sql
"""
import random
import uuid
from datetime import date, timedelta

random.seed(42)  # reproducible output

EMPLOYEE_COUNT = 200
NEW_COUNT = EMPLOYEE_COUNT - 5

FIRST_NAMES = [
    'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Ayaan', 'Krishna', 'Ishaan',
    'Rohan', 'Karan', 'Dev', 'Aryan', 'Kabir', 'Yash', 'Rudra', 'Shaurya', 'Advait', 'Ansh',
    'Ananya', 'Diya', 'Saanvi', 'Aadhya', 'Kiara', 'Myra', 'Anika', 'Navya', 'Riya', 'Ira',
    'Priya', 'Neha', 'Pooja', 'Sneha', 'Kavya', 'Isha', 'Meera', 'Tara', 'Zara', 'Aisha',
    'James', 'John', 'Michael', 'David', 'Daniel', 'Matthew', 'Andrew', 'Joshua', 'Ryan', 'Nathan',
    'Emma', 'Olivia', 'Sophia', 'Isabella', 'Mia', 'Charlotte', 'Amelia', 'Harper', 'Evelyn', 'Abigail',
]
LAST_NAMES = [
    'Sharma', 'Verma', 'Gupta', 'Mehta', 'Patel', 'Shah', 'Kumar', 'Singh', 'Rao', 'Reddy',
    'Iyer', 'Nair', 'Menon', 'Pillai', 'Chatterjee', 'Banerjee', 'Mukherjee', 'Das', 'Bose', 'Ghosh',
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis', 'Garcia', 'Wilson', 'Anderson',
    'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris', 'Clark', 'Lewis',
]
BANKS = [
    ('HDFC Bank', 'HDFC'), ('ICICI Bank', 'ICIC'), ('State Bank of India', 'SBIN'),
    ('Axis Bank', 'UTIB'), ('Kotak Mahindra Bank', 'KKBK'), ('Yes Bank', 'YESB'),
    ('Punjab National Bank', 'PUNB'), ('IDFC First Bank', 'IDFB'),
]

# department_id -> (job_position_ids pool, working_schedule weight, manager employee_id, wage range)
DEPARTMENTS = {
    'd0000000-0000-0000-0000-000000000001': {  # Engineering
        'jobs': [
            ('00000000-0000-0000-0000-000000000001', 'Engineering Lead', (110000, 140000)),
            ('00000000-0000-0000-1000-000000000001', 'Engineering Manager', (95000, 115000)),
        ],
        'manager': 'e0000000-0000-0000-0000-000000000003',  # Charlie
    },
    'd0000000-0000-0000-0000-000000000002': {  # Software Development
        'jobs': [
            ('00000000-0000-0000-0000-000000000002', 'Senior Software Engineer', (80000, 100000)),
            ('00000000-0000-0000-1000-000000000002', 'Software Engineer', (55000, 75000)),
            ('00000000-0000-0000-1000-000000000003', 'Associate Software Engineer', (35000, 50000)),
        ],
        'manager': 'e0000000-0000-0000-0000-000000000004',  # David
    },
    'd0000000-0000-0000-0000-000000000003': {  # Quality Assurance
        'jobs': [
            ('00000000-0000-0000-0000-000000000003', 'QA Automation Engineer', (60000, 80000)),
            ('00000000-0000-0000-1000-000000000004', 'QA Engineer', (40000, 58000)),
        ],
        'manager': 'e0000000-0000-0000-0000-000000000005',  # Eva
    },
    'd0000000-0000-0000-0000-000000000004': {  # Human Resources
        'jobs': [
            ('00000000-0000-0000-0000-000000000004', 'HR Manager', (75000, 90000)),
            ('00000000-0000-0000-1000-000000000005', 'HR Executive', (40000, 55000)),
            ('00000000-0000-0000-1000-000000000006', 'Talent Acquisition Specialist', (45000, 60000)),
        ],
        'manager': 'e0000000-0000-0000-0000-000000000001',  # Alice
    },
    'd0000000-0000-0000-0000-000000000005': {  # Finance & Payroll
        'jobs': [
            ('00000000-0000-0000-0000-000000000005', 'Payroll Specialist', (65000, 80000)),
            ('00000000-0000-0000-1000-000000000007', 'Financial Analyst', (55000, 70000)),
            ('00000000-0000-0000-1000-000000000008', 'Accounts Executive', (38000, 52000)),
        ],
        'manager': 'e0000000-0000-0000-0000-000000000002',  # Bob
    },
}
FULL_TIME_SCHEDULE = '00000000-0000-0000-0001-000000000001'
PART_TIME_SCHEDULE = '00000000-0000-0000-0001-000000000002'
SALARY_STRUCTURE = '00000000-0000-0000-0002-000000000001'
PTO_TYPE = '00000000-0000-0000-0003-000000000001'


def sql_str(value):
    return "'" + str(value).replace("'", "''") + "'"


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def business_days(month_start: date, count: int):
    days = []
    d = month_start
    while len(days) < count:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    return days


def main():
    out = []
    w = out.append

    w("-- =====================================================================")
    w("-- Pexo — Comprehensive Seed & Dummy Data Script")
    w("-- Built for PostgreSQL 15+ / Neon DB")
    w(f"-- {EMPLOYEE_COUNT} employees total: E001-E005 are the original named demo")
    w("-- accounts (unchanged, Password@123 logins), E006+ are generated.")
    w("-- Regenerate with: python3 scripts/generate_seed_data.py > seed_dummy_data.sql")
    w("-- =====================================================================")
    w("")
    w("BEGIN;")
    w("")
    w("-- ---------------------------------------------------------------------")
    w("-- 0. CLEANUP (TRUNCATE ALL DATA RESPECTING FK CONSTRAINTS)")
    w("-- ---------------------------------------------------------------------")
    w("TRUNCATE ")
    w("  audit_log, payslip_line, payslip, payrun, time_off_request, ")
    w("  time_off_allocation, time_off_type, attendance, contract, ")
    w("  salary_structure_rule, salary_rule, salary_structure, ")
    w("  employee_bank_account, user_role, app_user, employee, ")
    w("  job_position, department, working_schedule_line, working_schedule ")
    w("RESTART IDENTITY CASCADE;")
    w("")

    # ---- 1. Working schedules ----
    w("-- ---------------------------------------------------------------------")
    w("-- 1. WORKING SCHEDULES & SCHEDULE LINES")
    w("-- ---------------------------------------------------------------------")
    w("INSERT INTO working_schedule (id, name, schedule_type, total_weekly_hours)")
    w("VALUES ")
    w("  ('00000000-0000-0000-0001-000000000001', 'Standard Full-Time (40h)', 'FULL_TIME', 40.00),")
    w("  ('00000000-0000-0000-0001-000000000002', 'Flexible Part-Time (20h)', 'PART_TIME', 20.00);")
    w("")
    w("INSERT INTO working_schedule_line (id, working_schedule_id, day, start_time, end_time, break_minutes)")
    w("VALUES")
    w("  -- Standard 40h (Mon-Fri 09:00 - 18:00 with 60 min break = 8h/day)")
    w("  (gen_random_uuid(), '00000000-0000-0000-0001-000000000001', 'MON', '09:00:00', '18:00:00', 60),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0001-000000000001', 'TUE', '09:00:00', '18:00:00', 60),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0001-000000000001', 'WED', '09:00:00', '18:00:00', 60),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0001-000000000001', 'THU', '09:00:00', '18:00:00', 60),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0001-000000000001', 'FRI', '09:00:00', '18:00:00', 60),")
    w("  -- Part-time 20h (Mon-Fri 09:00 - 13:00 with 0 min break = 4h/day)")
    w("  (gen_random_uuid(), '00000000-0000-0000-0001-000000000002', 'MON', '09:00:00', '13:00:00', 0),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0001-000000000002', 'TUE', '09:00:00', '13:00:00', 0),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0001-000000000002', 'WED', '09:00:00', '13:00:00', 0),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0001-000000000002', 'THU', '09:00:00', '13:00:00', 0),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0001-000000000002', 'FRI', '09:00:00', '13:00:00', 0);")
    w("")

    # ---- 2. Departments ----
    w("-- ---------------------------------------------------------------------")
    w("-- 2. DEPARTMENTS")
    w("-- ---------------------------------------------------------------------")
    w("INSERT INTO department (id, name, parent_department_id)")
    w("VALUES ")
    w("  ('d0000000-0000-0000-0000-000000000001', 'Engineering', NULL),")
    w("  ('d0000000-0000-0000-0000-000000000002', 'Software Development', 'd0000000-0000-0000-0000-000000000001'),")
    w("  ('d0000000-0000-0000-0000-000000000003', 'Quality Assurance', 'd0000000-0000-0000-0000-000000000001'),")
    w("  ('d0000000-0000-0000-0000-000000000004', 'Human Resources', NULL),")
    w("  ('d0000000-0000-0000-0000-000000000005', 'Finance & Payroll', NULL);")
    w("")

    # ---- 3. Job positions (original 5 + new variety) ----
    w("-- ---------------------------------------------------------------------")
    w("-- 3. JOB POSITIONS")
    w("-- ---------------------------------------------------------------------")
    w("INSERT INTO job_position (id, title, department_id)")
    w("VALUES")
    job_rows = []
    for dept_id, info in DEPARTMENTS.items():
        for job_id, title, _wage in info['jobs']:
            job_rows.append(f"  ({sql_str(job_id)}, {sql_str(title)}, {sql_str(dept_id)})")
    w(",\n".join(job_rows) + ";")
    w("")

    # ---- 4. Employees (5 original, unchanged, + generated) ----
    w("-- ---------------------------------------------------------------------")
    w(f"-- 4. EMPLOYEES ({EMPLOYEE_COUNT} total — E001-E005 original, E006+ generated)")
    w("-- ---------------------------------------------------------------------")
    w("INSERT INTO employee (")
    w("  id, employee_code, first_name, last_name, email, phone, date_of_birth, gender,")
    w("  date_joined, department_id, job_position_id, default_working_schedule_id, employment_status")
    w(") VALUES")

    emp_rows = []
    emp_rows.append("  ('e0000000-0000-0000-0000-000000000001', 'E001', 'Alice', 'Smith', 'alice.smith@Pexo.com', '+15550101', '1988-03-15', 'Female', '2022-01-10', 'd0000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000004', '00000000-0000-0000-0001-000000000001', 'ACTIVE')")
    emp_rows.append("  ('e0000000-0000-0000-0000-000000000002', 'E002', 'Bob', 'Johnson', 'bob.johnson@Pexo.com', '+15550102', '1990-07-22', 'Male', '2022-03-01', 'd0000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0001-000000000001', 'ACTIVE')")
    emp_rows.append("  ('e0000000-0000-0000-0000-000000000003', 'E003', 'Charlie', 'Davis', 'charlie.davis@Pexo.com', '+15550103', '1985-11-05', 'Male', '2021-06-15', 'd0000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0001-000000000001', 'ACTIVE')")
    emp_rows.append("  ('e0000000-0000-0000-0000-000000000004', 'E004', 'David', 'Miller', 'david.miller@Pexo.com', '+15550104', '1993-02-18', 'Male', '2023-01-09', 'd0000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0001-000000000001', 'ACTIVE')")
    emp_rows.append("  ('e0000000-0000-0000-0000-000000000005', 'E005', 'Eva', 'Wilson', 'eva.wilson@Pexo.com', '+15550105', '1995-09-30', 'Female', '2023-05-20', 'd0000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0001-000000000001', 'ACTIVE')")

    dept_ids = list(DEPARTMENTS.keys())
    used_emails = set()
    generated = []  # (emp_id, code, first, last, dept_id, job_id, wage_lo, wage_hi, schedule_id, status)

    for i in range(NEW_COUNT):
        emp_num = i + 6
        code = f"E{emp_num:03d}"
        emp_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"pexo-employee-{emp_num}"))
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        email_base = f"{first.lower()}.{last.lower()}"
        email = f"{email_base}@Pexo.com"
        suffix = 1
        while email in used_emails:
            suffix += 1
            email = f"{email_base}{suffix}@Pexo.com"
        used_emails.add(email)

        dept_id = random.choice(dept_ids)
        info = DEPARTMENTS[dept_id]
        job_id, _title, (wage_lo, wage_hi) = random.choice(info['jobs'])
        schedule_id = FULL_TIME_SCHEDULE if random.random() < 0.85 else PART_TIME_SCHEDULE
        status = random.choices(['ACTIVE', 'ON_LEAVE', 'INACTIVE'], weights=[90, 6, 4])[0]
        dob = random_date(date(1978, 1, 1), date(2002, 12, 31))
        joined = random_date(date(2022, 1, 1), date(2026, 7, 1))
        gender = random.choice(['Male', 'Female'])
        phone = f"+1555{1000 + emp_num:04d}"

        generated.append({
            'id': emp_id, 'code': code, 'first': first, 'last': last, 'email': email,
            'dept_id': dept_id, 'job_id': job_id, 'wage_lo': wage_lo, 'wage_hi': wage_hi,
            'schedule_id': schedule_id, 'status': status, 'manager': info['manager'],
            'joined': joined,
        })

        emp_rows.append(
            f"  ({sql_str(emp_id)}, {sql_str(code)}, {sql_str(first)}, {sql_str(last)}, "
            f"{sql_str(email)}, {sql_str(phone)}, {sql_str(dob.isoformat())}, {sql_str(gender)}, "
            f"{sql_str(joined.isoformat())}, {sql_str(dept_id)}, {sql_str(job_id)}, "
            f"{sql_str(schedule_id)}, {sql_str(status)})"
        )

    w(",\n".join(emp_rows) + ";")
    w("")
    w("-- Set Manager Relationships (originals)")
    w("UPDATE employee SET manager_id = 'e0000000-0000-0000-0000-000000000003' WHERE id IN ('e0000000-0000-0000-0000-000000000004', 'e0000000-0000-0000-0000-000000000005');")
    w("")
    w("UPDATE department SET manager_employee_id = 'e0000000-0000-0000-0000-000000000001' WHERE id = 'd0000000-0000-0000-0000-000000000004';")
    w("UPDATE department SET manager_employee_id = 'e0000000-0000-0000-0000-000000000002' WHERE id = 'd0000000-0000-0000-0000-000000000005';")
    w("UPDATE department SET manager_employee_id = 'e0000000-0000-0000-0000-000000000003' WHERE id IN ('d0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000002', 'd0000000-0000-0000-0000-000000000003');")
    w("")
    w("-- Manager relationships (generated employees -> department lead)")
    mgr_updates = {}
    for e in generated:
        mgr_updates.setdefault(e['manager'], []).append(e['id'])
    for mgr_id, emp_ids in mgr_updates.items():
        ids_sql = ", ".join(sql_str(i) for i in emp_ids)
        w(f"UPDATE employee SET manager_id = {sql_str(mgr_id)} WHERE id IN ({ids_sql});")
    w("")

    # ---- 5. App users (unchanged — only the original 6 logins) ----
    w("-- ---------------------------------------------------------------------")
    w("-- 5. APP USERS & USER ROLES (Password for all users: Password@123)")
    w("-- Only the original demo accounts get logins — the 195 generated")
    w("-- employees are data-only (no app_user row), consistent with a real")
    w("-- HR system where not every employee record has portal access yet.")
    w("-- ---------------------------------------------------------------------")
    w("INSERT INTO app_user (id, email, password_hash, is_active, employee_id)")
    w("VALUES")
    w("  ('a0000000-0000-0000-0000-000000000000', 'admin@Pexo.com', crypt('Password@123', gen_salt('bf')), TRUE, NULL),")
    w("  ('a0000000-0000-0000-0000-000000000001', 'alice.hr@Pexo.com', crypt('Password@123', gen_salt('bf')), TRUE, 'e0000000-0000-0000-0000-000000000001'),")
    w("  ('a0000000-0000-0000-0000-000000000002', 'bob.payroll@Pexo.com', crypt('Password@123', gen_salt('bf')), TRUE, 'e0000000-0000-0000-0000-000000000002'),")
    w("  ('a0000000-0000-0000-0000-000000000003', 'charlie.lead@Pexo.com', crypt('Password@123', gen_salt('bf')), TRUE, 'e0000000-0000-0000-0000-000000000003'),")
    w("  ('a0000000-0000-0000-0000-000000000004', 'david.dev@Pexo.com', crypt('Password@123', gen_salt('bf')), TRUE, 'e0000000-0000-0000-0000-000000000004'),")
    w("  ('a0000000-0000-0000-0000-000000000005', 'eva.qa@Pexo.com', crypt('Password@123', gen_salt('bf')), TRUE, 'e0000000-0000-0000-0000-000000000005');")
    w("")
    w("-- Map roles to app_users")
    w("INSERT INTO user_role (user_id, role_id) SELECT 'a0000000-0000-0000-0000-000000000000', id FROM role WHERE name = 'ADMIN';")
    w("INSERT INTO user_role (user_id, role_id) SELECT 'a0000000-0000-0000-0000-000000000001', id FROM role WHERE name = 'HR_MANAGER';")
    w("INSERT INTO user_role (user_id, role_id) SELECT 'a0000000-0000-0000-0000-000000000002', id FROM role WHERE name = 'HR_PAYROLL_MANAGER';")
    w("INSERT INTO user_role (user_id, role_id) SELECT 'a0000000-0000-0000-0000-000000000003', id FROM role WHERE name = 'EMPLOYEE';")
    w("INSERT INTO user_role (user_id, role_id) SELECT 'a0000000-0000-0000-0000-000000000004', id FROM role WHERE name = 'EMPLOYEE';")
    w("INSERT INTO user_role (user_id, role_id) SELECT 'a0000000-0000-0000-0000-000000000005', id FROM role WHERE name = 'EMPLOYEE';")
    w("")

    # ---- 6. Bank accounts ----
    w("-- ---------------------------------------------------------------------")
    w("-- 6. EMPLOYEE BANK ACCOUNTS (One primary per employee)")
    w("-- ---------------------------------------------------------------------")
    w("INSERT INTO employee_bank_account (id, employee_id, account_holder_name, account_number, ifsc_code, bank_name, is_primary)")
    w("VALUES")
    bank_rows = [
        "  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000001', 'Alice Smith', '998877665501', 'HDFC0001234', 'HDFC Bank', TRUE)",
        "  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000002', 'Bob Johnson', '998877665502', 'ICIC0005678', 'ICICI Bank', TRUE)",
        "  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000003', 'Charlie Davis', '998877665503', 'SBIN0009999', 'State Bank of India', TRUE)",
        "  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000004', 'David Miller', '998877665504', 'UTIB0004321', 'Axis Bank', TRUE)",
        "  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000005', 'Eva Wilson', '998877665505', 'KKBK0008888', 'Kotak Mahindra Bank', TRUE)",
    ]
    for e in generated:
        bank_name, ifsc_prefix = random.choice(BANKS)
        acct_no = f"99887766{random.randint(10000, 99999)}"
        ifsc = f"{ifsc_prefix}0{random.randint(100000, 999999)}"
        bank_rows.append(
            f"  (gen_random_uuid(), {sql_str(e['id'])}, {sql_str(e['first'] + ' ' + e['last'])}, "
            f"{sql_str(acct_no)}, {sql_str(ifsc)}, {sql_str(bank_name)}, TRUE)"
        )
    w(",\n".join(bank_rows) + ";")
    w("")

    # ---- 7. Salary structures & rules (unchanged) ----
    w("-- ---------------------------------------------------------------------")
    w("-- 7. SALARY STRUCTURES & SALARY RULES")
    w("-- ---------------------------------------------------------------------")
    w("INSERT INTO salary_structure (id, name, code, description, is_active)")
    w("VALUES")
    w("  ('00000000-0000-0000-0002-000000000001', 'Standard Corporate Salary Structure', 'STD_SAL_2026', 'Default salary structure for regular full-time employees', TRUE);")
    w("")
    w("-- Insert rules in order of computation")
    w("INSERT INTO salary_rule (id, code, name, category, computation_type, fixed_amount, percentage_of_rule_code, percentage_value, formula_expression, is_active)")
    w("VALUES")
    w("  ('00000000-0000-0000-0002-000000000011', 'BASIC', 'Basic Salary', 'BASIC', 'FIXED', 50000.00, NULL, NULL, NULL, TRUE),")
    w("  ('00000000-0000-0000-0002-000000000012', 'HRA', 'House Rent Allowance', 'ALLOWANCE', 'PERCENTAGE', NULL, 'BASIC', 40.000, NULL, TRUE),")
    w("  ('00000000-0000-0000-0002-000000000013', 'CONVEYANCE', 'Conveyance Allowance', 'ALLOWANCE', 'FIXED', 3000.00, NULL, NULL, NULL, TRUE),")
    w("  ('00000000-0000-0000-0002-000000000014', 'GROSS', 'Gross Total', 'GROSS', 'FORMULA', NULL, NULL, NULL, 'BASIC + HRA + CONVEYANCE', TRUE),")
    w("  ('00000000-0000-0000-0002-000000000015', 'PF', 'Provident Fund Deduction', 'DEDUCTION', 'PERCENTAGE', NULL, 'BASIC', 12.000, NULL, TRUE),")
    w("  ('00000000-0000-0000-0002-000000000016', 'TAX', 'Income Tax Deduction', 'DEDUCTION', 'FIXED', 2500.00, NULL, NULL, NULL, TRUE),")
    w("  ('00000000-0000-0000-0002-000000000017', 'NET', 'Net Payable Salary', 'NET', 'FORMULA', NULL, NULL, NULL, 'GROSS - PF - TAX', TRUE);")
    w("")
    w("-- Attach rules to salary structure with strictly ordered sequence")
    w("INSERT INTO salary_structure_rule (id, salary_structure_id, salary_rule_id, sequence)")
    w("VALUES")
    w("  (gen_random_uuid(), '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0002-000000000011', 10),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0002-000000000012', 20),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0002-000000000013', 30),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0002-000000000014', 40),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0002-000000000015', 50),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0002-000000000016', 60),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0002-000000000017', 70);")
    w("")

    # ---- 8. Contracts ----
    w("-- ---------------------------------------------------------------------")
    w("-- 8. CONTRACTS")
    w("-- ---------------------------------------------------------------------")
    w("-- Enforces: Single ACTIVE contract per employee across overlapping date ranges")
    w("INSERT INTO contract (")
    w("  id, employee_id, contract_type, start_date, end_date, wage_amount, wage_type,")
    w("  salary_structure_id, working_schedule_id, department_id, job_position_id, status, signed_date")
    w(") VALUES")
    contract_rows = [
        "  ('c0000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 'PERMANENT', '2026-01-01', NULL, 85000.00, 'MONTHLY', '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0001-000000000001', 'd0000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000004', 'ACTIVE', '2025-12-28')",
        "  ('c0000000-0000-0000-0000-000000000002', 'e0000000-0000-0000-0000-000000000002', 'PERMANENT', '2026-01-01', NULL, 75000.00, 'MONTHLY', '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0001-000000000001', 'd0000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000005', 'ACTIVE', '2025-12-29')",
        "  ('c0000000-0000-0000-0000-000000000003', 'e0000000-0000-0000-0000-000000000003', 'PERMANENT', '2026-01-01', NULL, 120000.00, 'MONTHLY', '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0001-000000000001', 'd0000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'ACTIVE', '2025-12-20')",
        "  ('c0000000-0000-0000-0000-000000000004', 'e0000000-0000-0000-0000-000000000004', 'PERMANENT', '2026-01-01', NULL, 90000.00, 'MONTHLY', '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0001-000000000001', 'd0000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000002', 'ACTIVE', '2025-12-30')",
        "  ('c0000000-0000-0000-0000-000000000099', 'e0000000-0000-0000-0000-000000000004', 'PROBATION', '2025-01-01', '2025-12-31', 70000.00, 'MONTHLY', '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0001-000000000001', 'd0000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000002', 'EXPIRED', '2024-12-28')",
        "  ('c0000000-0000-0000-0000-000000000005', 'e0000000-0000-0000-0000-000000000005', 'FIXED_TERM', '2026-01-01', '2026-12-31', 70000.00, 'MONTHLY', '00000000-0000-0000-0002-000000000001', '00000000-0000-0000-0001-000000000001', 'd0000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000003', 'ACTIVE', '2025-12-29')",
    ]
    for e in generated:
        wage = round(random.uniform(e['wage_lo'], e['wage_hi']), -2)
        signed = e['joined'] - timedelta(days=random.randint(1, 5))
        contract_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"pexo-contract-{e['code']}"))
        contract_rows.append(
            f"  ({sql_str(contract_id)}, {sql_str(e['id'])}, 'PERMANENT', {sql_str(e['joined'].isoformat())}, NULL, "
            f"{wage:.2f}, 'MONTHLY', {sql_str(SALARY_STRUCTURE)}, {sql_str(e['schedule_id'])}, "
            f"{sql_str(e['dept_id'])}, {sql_str(e['job_id'])}, 'ACTIVE', {sql_str(signed.isoformat())})"
        )
    w(",\n".join(contract_rows) + ";")
    w("")

    # ---- 9. Attendance ----
    w("-- ---------------------------------------------------------------------")
    w("-- 9. ATTENDANCE RECORDS")
    w("-- ---------------------------------------------------------------------")
    w("INSERT INTO attendance (id, employee_id, work_date, check_in, check_out, worked_hours, status, is_manual_correction, corrected_by_user_id, correction_reason)")
    w("VALUES")
    attendance_rows = [
        "  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000004', '2026-08-03', '2026-08-03 09:00:00+00', '2026-08-03 18:00:00+00', 8.00, 'PRESENT', FALSE, NULL, NULL)",
        "  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000004', '2026-08-04', '2026-08-04 09:15:00+00', '2026-08-04 18:00:00+00', 7.75, 'LATE', FALSE, NULL, NULL)",
        "  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000004', '2026-08-05', '2026-08-05 09:00:00+00', '2026-08-05 18:00:00+00', 8.00, 'PRESENT', TRUE, 'a0000000-0000-0000-0000-000000000001', 'Employee forgot to tap badge; verified via manager')",
        "  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000005', '2026-08-03', '2026-08-03 08:55:00+00', '2026-08-03 18:00:00+00', 8.00, 'PRESENT', FALSE, NULL, NULL)",
        "  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000005', '2026-08-04', '2026-08-04 09:00:00+00', '2026-08-04 18:00:00+00', 8.00, 'PRESENT', FALSE, NULL, NULL)",
    ]
    aug_days = business_days(date(2026, 8, 3), 10)
    for e in generated:
        if e['status'] == 'INACTIVE':
            continue  # no attendance for inactive employees
        for d in aug_days:
            if random.random() < 0.05:
                continue  # occasional absence, no row
            is_pt = e['schedule_id'] == PART_TIME_SCHEDULE
            start_hour, start_min = (9, random.choice([0, 0, 0, 5, 10, 15]))
            late = start_min >= 15
            end_hour = 13 if is_pt else 18
            worked = round((end_hour * 60 - (start_hour * 60 + start_min)) / 60, 2)
            status = 'LATE' if late else 'PRESENT'
            check_in = f"{d.isoformat()} {start_hour:02d}:{start_min:02d}:00+00"
            check_out = f"{d.isoformat()} {end_hour:02d}:00:00+00"
            attendance_rows.append(
                f"  (gen_random_uuid(), {sql_str(e['id'])}, {sql_str(d.isoformat())}, "
                f"{sql_str(check_in)}, {sql_str(check_out)}, {worked:.2f}, {sql_str(status)}, FALSE, NULL, NULL)"
            )
    w(",\n".join(attendance_rows) + ";")
    w("")

    # ---- 10. Time off types, allocations, requests ----
    w("-- ---------------------------------------------------------------------")
    w("-- 10. TIME OFF TYPES, ALLOCATIONS, AND REQUESTS")
    w("-- ---------------------------------------------------------------------")
    w("INSERT INTO time_off_type (id, name, unit, requires_allocation, requires_approval, affects_payroll, color)")
    w("VALUES")
    w("  ('00000000-0000-0000-0003-000000000001', 'Paid Time Off (PTO)', 'DAYS', TRUE, TRUE, TRUE, '#3B82F6'),")
    w("  ('00000000-0000-0000-0003-000000000002', 'Sick Leave', 'DAYS', TRUE, TRUE, FALSE, '#EF4444'),")
    w("  ('00000000-0000-0000-0003-000000000003', 'Unpaid Leave', 'DAYS', FALSE, TRUE, TRUE, '#6B7280');")
    w("")
    w("-- Allocations (remaining_amount is GENERATED ALWAYS AS (allocated_amount - taken_amount))")
    w("INSERT INTO time_off_allocation (id, employee_id, time_off_type_id, allocated_amount, taken_amount, valid_from, valid_to, approval_status)")
    w("VALUES")
    alloc_rows = [
        "  ('00000000-0000-0000-0003-000000000101', 'e0000000-0000-0000-0000-000000000004', '00000000-0000-0000-0003-000000000001', 20.00, 3.00, '2026-01-01', '2026-12-31', 'APPROVED')",
        "  ('00000000-0000-0000-0003-000000000102', 'e0000000-0000-0000-0000-000000000004', '00000000-0000-0000-0003-000000000002', 10.00, 0.00, '2026-01-01', '2026-12-31', 'APPROVED')",
        "  ('00000000-0000-0000-0003-000000000103', 'e0000000-0000-0000-0000-000000000005', '00000000-0000-0000-0003-000000000001', 20.00, 0.00, '2026-01-01', '2026-12-31', 'APPROVED')",
    ]
    for e in generated:
        if e['status'] == 'INACTIVE':
            continue
        alloc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"pexo-alloc-{e['code']}"))
        taken = round(random.uniform(0, 8), 2)
        alloc_rows.append(
            f"  ({sql_str(alloc_id)}, {sql_str(e['id'])}, {sql_str(PTO_TYPE)}, 20.00, {taken:.2f}, "
            f"'2026-01-01', '2026-12-31', 'APPROVED')"
        )
    w(",\n".join(alloc_rows) + ";")
    w("")
    w("-- Time Off Requests (original demo requests only)")
    w("INSERT INTO time_off_request (id, employee_id, time_off_type_id, allocation_id, start_date, end_date, duration, status, approved_by_user_id, reason)")
    w("VALUES")
    w("  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000004', '00000000-0000-0000-0003-000000000001', '00000000-0000-0000-0003-000000000101', '2026-08-10', '2026-08-12', 3.00, 'APPROVED', 'a0000000-0000-0000-0000-000000000001', 'Summer Vacation'),")
    w("  (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000005', '00000000-0000-0000-0003-000000000001', '00000000-0000-0000-0003-000000000103', '2026-09-15', '2026-09-16', 2.00, 'SUBMITTED', NULL, 'Personal errands');")
    w("")

    # ---- 11. Payrun / payslip (original demo only) ----
    w("-- ---------------------------------------------------------------------")
    w("-- 11. PAYRUN, PAYSLIP, AND PAYSLIP LINES (original 5 named employees only)")
    w("-- ---------------------------------------------------------------------")
    w("INSERT INTO payrun (id, name, period_start, period_end, salary_structure_id, status, created_by_user_id, computed_at, validated_at, paid_at)")
    w("VALUES")
    w("  ('00000000-0000-0000-0004-000000000001', 'August 2026 Monthly Payroll', '2026-08-01', '2026-08-31', '00000000-0000-0000-0002-000000000001', 'PAID', 'a0000000-0000-0000-0000-000000000002', '2026-08-28 10:00:00+00', '2026-08-29 14:00:00+00', '2026-08-31 09:00:00+00');")
    w("")
    w("INSERT INTO payslip (id, payrun_id, employee_id, contract_id, period_start, period_end, worked_days, status, gross_amount, net_amount, has_warning, warning_notes)")
    w("VALUES")
    w("  ('00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0004-000000000001', 'e0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', '2026-08-01', '2026-08-31', 22.00, 'PAID', 73000.00, 64500.00, FALSE, NULL),")
    w("  ('00000000-0000-0000-0004-000000000102', '00000000-0000-0000-0004-000000000001', 'e0000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000002', '2026-08-01', '2026-08-31', 22.00, 'PAID', 73000.00, 64500.00, FALSE, NULL),")
    w("  ('00000000-0000-0000-0004-000000000103', '00000000-0000-0000-0004-000000000001', 'e0000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0000-000000000003', '2026-08-01', '2026-08-31', 22.00, 'PAID', 73000.00, 64500.00, FALSE, NULL),")
    w("  ('00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0004-000000000001', 'e0000000-0000-0000-0000-000000000004', 'c0000000-0000-0000-0000-000000000004', '2026-08-01', '2026-08-31', 22.00, 'PAID', 73000.00, 64500.00, FALSE, NULL),")
    w("  ('00000000-0000-0000-0004-000000000105', '00000000-0000-0000-0004-000000000001', 'e0000000-0000-0000-0000-000000000005', 'c0000000-0000-0000-0000-000000000005', '2026-08-01', '2026-08-31', 22.00, 'PAID', 73000.00, 64500.00, FALSE, NULL);")
    w("")
    w("INSERT INTO payslip_line (id, payslip_id, salary_rule_id, salary_rule_code, sequence, amount, computation_detail)")
    w("VALUES")
    w("  (gen_random_uuid(), '00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0002-000000000011', 'BASIC', 10, 50000.00, '{\"type\": \"FIXED\", \"value\": 50000.00}'::jsonb),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0002-000000000012', 'HRA', 20, 20000.00, '{\"type\": \"PERCENTAGE\", \"pct\": 40.0, \"base\": 50000.00}'::jsonb),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0002-000000000013', 'CONVEYANCE', 30, 3000.00, '{\"type\": \"FIXED\", \"value\": 3000.00}'::jsonb),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0002-000000000014', 'GROSS', 40, 73000.00, '{\"type\": \"FORMULA\", \"expression\": \"BASIC + HRA + CONVEYANCE\"}'::jsonb),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0002-000000000015', 'PF', 50, 6000.00, '{\"type\": \"PERCENTAGE\", \"pct\": 12.0, \"base\": 50000.00}'::jsonb),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0002-000000000016', 'TAX', 60, 2500.00, '{\"type\": \"FIXED\", \"value\": 2500.00}'::jsonb),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0004-000000000101', '00000000-0000-0000-0002-000000000017', 'NET', 70, 64500.00, '{\"type\": \"FORMULA\", \"expression\": \"GROSS - PF - TAX\"}'::jsonb),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0002-000000000011', 'BASIC', 10, 50000.00, '{\"type\": \"FIXED\", \"value\": 50000.00}'::jsonb),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0002-000000000012', 'HRA', 20, 20000.00, '{\"type\": \"PERCENTAGE\", \"pct\": 40.0, \"base\": 50000.00}'::jsonb),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0002-000000000013', 'CONVEYANCE', 30, 3000.00, '{\"type\": \"FIXED\", \"value\": 3000.00}'::jsonb),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0002-000000000014', 'GROSS', 40, 73000.00, '{\"type\": \"FORMULA\", \"expression\": \"BASIC + HRA + CONVEYANCE\"}'::jsonb),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0002-000000000015', 'PF', 50, 6000.00, '{\"type\": \"PERCENTAGE\", \"pct\": 12.0, \"base\": 50000.00}'::jsonb),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0002-000000000016', 'TAX', 60, 2500.00, '{\"type\": \"FIXED\", \"value\": 2500.00}'::jsonb),")
    w("  (gen_random_uuid(), '00000000-0000-0000-0004-000000000104', '00000000-0000-0000-0002-000000000017', 'NET', 70, 64500.00, '{\"type\": \"FORMULA\", \"expression\": \"GROSS - PF - TAX\"}'::jsonb);")
    w("")

    # ---- 12. Audit log ----
    w("-- ---------------------------------------------------------------------")
    w("-- 12. AUDIT LOGS")
    w("-- ---------------------------------------------------------------------")
    w("INSERT INTO audit_log (id, user_id, entity_name, entity_id, action, field_changes, reason)")
    w("VALUES")
    w("  (gen_random_uuid(), 'a0000000-0000-0000-0000-000000000001', 'contract', 'c0000000-0000-0000-0000-000000000004', 'APPROVE', '{\"status\": {\"old\": \"DRAFT\", \"new\": \"ACTIVE\"}}'::jsonb, 'Approved initial employee contract'),")
    w("  (gen_random_uuid(), 'a0000000-0000-0000-0000-000000000001', 'time_off_request', '00000000-0000-0000-0003-000000000101', 'APPROVE', '{\"status\": {\"old\": \"SUBMITTED\", \"new\": \"APPROVED\"}}'::jsonb, 'Approved summer vacation leave request'),")
    w("  (gen_random_uuid(), 'a0000000-0000-0000-0000-000000000002', 'payrun', '00000000-0000-0000-0004-000000000001', 'UPDATE', '{\"status\": {\"old\": \"VALIDATED\", \"new\": \"PAID\"}}'::jsonb, 'Executed monthly salary payout');")
    w("")
    w("COMMIT;")

    print("\n".join(out))


if __name__ == '__main__':
    main()
