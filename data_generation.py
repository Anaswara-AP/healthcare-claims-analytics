import pandas as pd
import numpy as np
from faker import Faker
from cryptography.fernet import Fernet
import psycopg2
from sqlalchemy import create_engine, text
import random
import string
from datetime import datetime, timedelta, date
import warnings
warnings.filterwarnings('ignore')
 
synthetic_data = Faker('en_US')
Faker.seed(42)
np.random.seed(42)
random.seed(42)
 
# ============================================================
# HIPAA ENCRYPTION SETUP
# Fernet = AES-128 in CBC mode (symmetric encryption)
# Save this key securely — you need it to decrypt later
# ============================================================
ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)
 
print(f"ENCRYPTION KEY (save this securely): {ENCRYPTION_KEY.decode()}")
 
def encrypt(value: str) -> bytes:
    return cipher.encrypt(value.encode('utf-8'))
 
def decrypt(token: bytes) -> str:
    return cipher.decrypt(token).decode('utf-8')
 
# ============================================================
# DATABASE CONNECTION
# Update with your PostgreSQL credentials
# ============================================================
DB_CONFIG = {
    'host'    : 'localhost',
    'port'    : '5432',
    'database': 'HealthcareAnalysisDatabase',
    'user'    : 'postgres',
    'password': '[password]'
}
 
engine = create_engine(
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)
 
# ============================================================
# REFERENCE DATA
# ============================================================
HOSPITAL_TYPES  = ['General', 'Specialty', 'Teaching', 'Children', 'Rehabilitation']
SPECIALTIES     = ['Oncology', 'Orthopedics', 'Cardiology', 'Neurology', 'Pediatrics',
                   'Surgery', 'ICU', 'Emergency', 'Radiology', 'Dermatology']
DEPT_NAMES      = ['Oncology', 'Orthopedics', 'ICU', 'Surgery', 'Cardiology',
                   'Neurology', 'Pediatrics', 'Emergency', 'Radiology', 'Dermatology',
                   'Pharmacy', 'Laboratory', 'Physical Therapy', 'Billing', 'Administration']
PROVIDER_TYPES  = ['Physician', 'Nurse Practitioner', 'Physician Assistant',
                   'Lab Technician', 'Radiologist', 'Therapist']
PAYER_NAMES     = ['Medicare', 'Medicaid', 'UnitedHealthcare', 'Aetna', 'Cigna',
                   'Blue Cross Blue Shield', 'Humana', 'Elevance Health',
                   'Oscar Health', 'Health Net', 'Molina Healthcare',
                   'WellCare', 'Centene', 'Kaiser Permanente',
                   'CVS Health', 'Anthem', 'Magellan Health',
                   'AmeriHealth', 'Highmark', 'Tufts Health Plan']
PAYER_TYPES     = {'Medicare': 'Public', 'Medicaid': 'Public',
                   'UnitedHealthcare': 'Private', 'Aetna': 'Private',
                   'Cigna': 'Private', 'Blue Cross Blue Shield': 'Private',
                   'Humana': 'Private', 'Elevance Health': 'Private',
                   'Oscar Health': 'Private', 'Health Net': 'Private',
                   'Molina Healthcare': 'Public', 'WellCare': 'Public',
                   'Centene': 'Private', 'Kaiser Permanente': 'Private',
                   'CVS Health': 'Private', 'Anthem': 'Private',
                   'Magellan Health': 'Private', 'AmeriHealth': 'Private',
                   'Highmark': 'Private', 'Tufts Health Plan': 'Private'}
COVERAGE_TYPES  = ['HMO', 'PPO', 'EPO', 'POS', 'HDHP']
VISIT_TYPES     = ['In-Patient', 'Out-Patient', 'Emergency']
CLAIM_TYPES     = ['Professional', 'Institutional']
CLAIM_STATUSES  = ['Approved', 'Denied', 'Pending', 'Submitted', 'Acknowledged', 'Resubmitted']
DENIAL_CODES    = ['CO-4', 'CO-11', 'CO-16', 'CO-22', 'CO-50',
                   'PR-1', 'PR-2', 'PR-27', 'OA-23', 'PI-4']
DENIAL_REASONS  = ['Wrong CPT Code', 'Treatment not covered', 'Policy not active',
                   'Missing documentation', 'Duplicate claim',
                   'Not a licensed provider', 'Prior authorization required',
                   'Incorrect patient details', 'Coordination of benefits',
                   'Service not medically necessary']
APPEAL_STATUSES = ['Not Appealed', 'In Appeal', 'Overturned', 'Upheld']
DECISIONS       = ['Approved', 'Denied', 'Partially Approved']
PAYMENT_METHODS = ['EFT', 'Check', 'ACH', 'Wire Transfer']
INSURANCE_TYPES = ['Public', 'Private', 'Self-Pay', 'Charity']
GENDERS         = ['Male', 'Female', 'Other']
US_STATES       = ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI',
                   'NJ', 'VA', 'WA', 'AZ', 'MA', 'TN', 'IN', 'MO', 'MD', 'WI']
ICD10_CODES     = ['Z00.00', 'I10', 'E11.9', 'J18.9', 'M54.5',
                   'K21.0', 'F32.9', 'N18.3', 'C34.10', 'S72.001A']
CPT_CODES       = ['99213', '99214', '99232', '93000', '71046',
                   '27447', '70553', '80053', '36415', '43239']
 
# ============================================================
# RECORD COUNTS
# ============================================================
N_HOSPITALS     = 50
N_DEPARTMENTS   = 200
N_PROVIDERS     = 500
N_DOCTORS       = 1_000
N_PAYERS        = 20
N_PATIENTS      = 100_000
N_POLICIES      = 150_000
N_APPOINTMENTS  = 300_000
N_CLAIMS        = 500_000
N_CLAIM_STATUS  = 500_000
N_PAYMENTS      = 350_000
N_DENIALS       = 75_000
N_ADJUDICATIONS = 500_000
# TOTAL         ~ 2,026,770
 
def random_date(start_year=2018, end_year=2024):
    start = date(start_year, 1, 1)
    end   = date(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))
 
# Global NPI pool — guaranteed unique across ALL tables
_used_npis = set()

def unique_npi():
    while True:
        npi = ''.join(random.choices(string.digits, k=10))
        if npi not in _used_npis:
            _used_npis.add(npi)
            return npi
 
def unique_license():
    return synthetic_data.bothify(text='??######').upper()
 
def batch_insert(df, table_name, engine, batch_size=10_000):
    total = len(df)
    for i in range(0, total, batch_size):
        batch = df.iloc[i:i+batch_size]
        batch.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"  {table_name}: inserted {min(i+batch_size, total):,} / {total:,}")
 
# ============================================================
# 1. HOSPITALS  (50 records)
# ============================================================
print("\n[1/13] Generating hospitals...")
hospitals = []
for i in range(N_HOSPITALS):
    hospitals.append({
        'hospital_name' : f"{synthetic_data.last_name()} {random.choice(['Medical Center','Hospital','Health System','Clinic','Regional Hospital'])}",
        'hptl_location' : synthetic_data.street_address(),
        'hptl_state'    : random.choice(US_STATES),
        'city'          : synthetic_data.city(),
        'zip_code'      : synthetic_data.zipcode(),
        'bed_count'     : random.randint(50, 800),
    })
df_hospitals = pd.DataFrame(hospitals)
batch_insert(df_hospitals, 'hospitals', engine)
hospital_ids = pd.read_sql("SELECT hospital_id FROM hospitals", engine)['hospital_id'].tolist()
print(f"  Done: {len(hospital_ids)} hospitals")
 
# ============================================================
# 2. DEPARTMENTS  (200 records)
# ============================================================
print("\n[2/13] Generating departments...")
departments = []
used_dept_codes = set()
for i in range(N_DEPARTMENTS):
    code = synthetic_data.bothify(text='DEPT-###')
    while code in used_dept_codes:
        code = synthetic_data.bothify(text='DEPT-###')
    used_dept_codes.add(code)
    departments.append({
        'dept_name'   : random.choice(DEPT_NAMES),
        'dept_code'   : code,
        'hospital_id' : random.choice(hospital_ids),
        'dept_head'   : synthetic_data.name(),
    })
df_departments = pd.DataFrame(departments)
batch_insert(df_departments, 'departments', engine)
dept_ids = pd.read_sql("SELECT department_id FROM departments", engine)['department_id'].tolist()
print(f"  Done: {len(dept_ids)} departments")
 
# ============================================================
# 3. PROVIDERS  (500 records)
# ============================================================
print("\n[3/13] Generating providers...")
providers = []
for i in range(N_PROVIDERS):
    providers.append({
        'provider_name' : synthetic_data.name(),
        'provider_type' : random.choice(PROVIDER_TYPES),
        'npi_number'    : unique_npi(), 
        'hospital_id'   : random.choice(hospital_ids),
        'specialty'     : random.choice(SPECIALTIES),
    })
df_providers = pd.DataFrame(providers)
batch_insert(df_providers, 'providers', engine)
print(f"  Done: {N_PROVIDERS} providers")
 
# ============================================================
# 4. DOCTORS  (1,000 records)
# ============================================================
print("\n[4/13] Generating doctors...")
doctors = []
used_doc_npi     = set()
used_doc_license = set()
for i in range(N_DOCTORS):
    npi = unique_npi()
    while npi in used_doc_npi:
        npi = unique_npi()
    used_doc_npi.add(npi)
    lic = unique_license()
    while lic in used_doc_license:
        lic = unique_license()
    used_doc_license.add(lic)
    h_id = random.choice(hospital_ids)
    doctors.append({
        'doctor_name'    : synthetic_data.name(),
        'specialty'      : random.choice(SPECIALTIES),
        'license_number' : lic,
        'npi_number'     : npi,
        'department_id'  : random.choice(dept_ids),
        'hospital_id'    : h_id,
        'years_exp'      : random.randint(1, 35),
    })
df_doctors = pd.DataFrame(doctors)
batch_insert(df_doctors, 'doctors', engine)
doctor_ids = pd.read_sql("SELECT doctor_id FROM doctors", engine)['doctor_id'].tolist()
print(f"  Done: {len(doctor_ids)} doctors")
 
# ============================================================
# 5. INSURANCE_PAYERS  (20 records)
# ============================================================
print("\n[5/13] Generating insurance_payers...")
payers = []
for name in PAYER_NAMES:
    payers.append({
        'payer_name'    : name,
        'payer_type'    : PAYER_TYPES.get(name, 'Private'),
        'payer_code'    : name[:3].upper() + str(random.randint(100, 999)),
        'payer_state'   : random.choice(US_STATES),
        'contact_phone' : synthetic_data.phone_number()[:20],
        'contact_email' : synthetic_data.company_email(),
    })
df_payers = pd.DataFrame(payers)
batch_insert(df_payers, 'insurance_payers', engine)
payer_ids = pd.read_sql("SELECT payer_id FROM insurance_payers", engine)['payer_id'].tolist()
print(f"  Done: {len(payer_ids)} payers")
 
# ============================================================
# 6. PATIENTS  (100,000 records) — HIPAA encrypted
# ============================================================
print("\n[6/13] Generating patients (HIPAA encrypted)...")
patients = []
for i in range(N_PATIENTS):
    patients.append({
        'name_encrypted'  : encrypt(synthetic_data.name()),
        'phone_encrypted' : encrypt(synthetic_data.phone_number()),
        'dob'             : synthetic_data.date_of_birth(minimum_age=18, maximum_age=90),
        'gender'          : random.choice(GENDERS),
        'address'         : synthetic_data.street_address(),
        'city'            : synthetic_data.city(),
        'zip_code'        : synthetic_data.zipcode(),
        'insurance_type'  : random.choice(INSURANCE_TYPES),
    })
    if (i+1) % 10_000 == 0:
        print(f"  Encrypting patients: {i+1:,} / {N_PATIENTS:,}")
 
df_patients = pd.DataFrame(patients)
batch_insert(df_patients, 'patients', engine)
patient_ids = pd.read_sql("SELECT patient_id FROM patients", engine)['patient_id'].tolist()
print(f"  Done: {len(patient_ids)} patients")
 
# ============================================================
# 7. POLICIES  (150,000 records)
# ============================================================
print("\n[7/13] Generating policies...")
policies = []
used_policy_numbers = set()
for i in range(N_POLICIES):
    pol_num = 'POL' + ''.join(random.choices(string.digits, k=8))
    while pol_num in used_policy_numbers:
        pol_num = 'POL' + ''.join(random.choices(string.digits, k=8))
    used_policy_numbers.add(pol_num)
    start = random_date(2018, 2023)
    end   = start + timedelta(days=365)
    policies.append({
        'patient_id'        : random.choice(patient_ids),
        'payer_id'          : random.choice(payer_ids),
        'policy_number'     : pol_num,
        'coverage_type'     : random.choice(COVERAGE_TYPES),
        'start_date'        : start,
        'end_date'          : end,
        'premium_amount'    : round(random.uniform(150, 1200), 2),
        'deductible_amount' : round(random.uniform(500, 5000), 2),
        'copay_amount'      : round(random.uniform(10, 100), 2),
        'is_active'         : random.choice([True, True, True, False]),
    })
df_policies = pd.DataFrame(policies)
batch_insert(df_policies, 'policies', engine)
policy_ids = pd.read_sql("SELECT policy_id FROM policies", engine)['policy_id'].tolist()
print(f"  Done: {len(policy_ids)} policies")
 
# ============================================================
# 8. APPOINTMENTS  (300,000 records)
# ============================================================
print("\n[8/13] Generating appointments...")
appointments = []
for i in range(N_APPOINTMENTS):
    appt_date = random_date(2020, 2024)
    appointments.append({
        'patient_id'       : random.choice(patient_ids),
        'doctor_id'        : random.choice(doctor_ids),
        'appointment_date' : appt_date,
        'appointment_time' : f"{random.randint(8,17):02d}:{random.choice(['00','15','30','45'])}",
        'visit_type'       : random.choice(VISIT_TYPES),
        'department_id'    : random.choice(dept_ids),
        'diagnosis_code'   : random.choice(ICD10_CODES),
        'procedure_code'   : random.choice(CPT_CODES),
        'status'           : random.choice(['Completed', 'Completed', 'Completed', 'Cancelled', 'No-Show']),
        'notes'            : synthetic_data.sentence(nb_words=8),
    })
df_appointments = pd.DataFrame(appointments)
batch_insert(df_appointments, 'appointments', engine)
appointment_ids = pd.read_sql("SELECT appointment_id FROM appointments", engine)['appointment_id'].tolist()
print(f"  Done: {len(appointment_ids)} appointments")
 
# ============================================================
# 9. CLAIMS  (500,000 records) — central fact table
# ============================================================
print("\n[9/13] Generating claims...")
claims = []
used_claim_numbers = set()
# Realistic distribution based on requirements doc:
# Denial rate: 13.6%, First Pass Rate: ~53%
status_weights = [0.53, 0.136, 0.15, 0.10, 0.054, 0.03]
 
for i in range(N_CLAIMS):
    cl_num = 'CLM' + ''.join(random.choices(string.digits, k=9))
    while cl_num in used_claim_numbers:
        cl_num = 'CLM' + ''.join(random.choices(string.digits, k=9))
    used_claim_numbers.add(cl_num)
    svc_date = random_date(2020, 2024)
    sub_date = svc_date + timedelta(days=random.randint(1, 5))
    status   = random.choices(CLAIM_STATUSES, weights=status_weights)[0]
    claims.append({
        'patient_id'      : random.choice(patient_ids),
        'doctor_id'       : random.choice(doctor_ids),
        'payer_id'        : random.choice(payer_ids),
        'policy_id'       : random.choice(policy_ids),
        'appointment_id'  : random.choice(appointment_ids),
        'department_id'   : random.choice(dept_ids),
        'claim_number'    : cl_num,
        'submission_date' : sub_date,
        'service_date'    : svc_date,
        'billed_amount'   : round(random.uniform(500, 150_000), 2),
        'diagnosis_code'  : random.choice(ICD10_CODES),
        'procedure_code'  : random.choice(CPT_CODES),
        'claim_type'      : random.choice(CLAIM_TYPES),
        'claim_status'    : status,
        'is_first_pass'   : status == 'Approved',
    })
df_claims = pd.DataFrame(claims)
batch_insert(df_claims, 'claims', engine)
claim_ids = pd.read_sql("SELECT claim_id, payer_id FROM claims", engine)
print(f"  Done: {N_CLAIMS} claims")
 
# ============================================================
# 10. CLAIM_STATUS  (500,000 records)
# ============================================================
print("\n[10/13] Generating claim_status...")
status_records = []
status_codes   = ['A1', 'D1', 'P1', 'S1', 'ACK', 'R1']
status_descs   = ['Approved by payer', 'Denied by payer', 'Pending review',
                  'Submitted to payer', 'Acknowledged by clearinghouse', 'Resubmitted']
for i in range(N_CLAIM_STATUS):
    idx = random.randint(0, len(status_codes)-1)
    status_records.append({
        'claim_id'          : int(claim_ids['claim_id'].iloc[i % len(claim_ids)]),
        'status_code'       : status_codes[idx],
        'status_description': status_descs[idx],
        'status_date'       : random_date(2020, 2024),
        'updated_by'        : synthetic_data.name(),
    })
df_claim_status = pd.DataFrame(status_records)
batch_insert(df_claim_status, 'claim_status', engine)
print(f"  Done: {N_CLAIM_STATUS} claim status records")
 
# ============================================================
# 11. PAYMENTS  (350,000 records)
# ============================================================
print("\n[11/13] Generating payments...")
payments = []
# Underpayment rate: ~11.4% from dashboard reference
for i in range(N_PAYMENTS):
    row         = claim_ids.iloc[i % len(claim_ids)]
    billed      = round(random.uniform(500, 150_000), 2)
    is_underpay = random.random() < 0.114
    paid        = round(billed * random.uniform(0.20, 0.60), 2) if is_underpay else round(billed * random.uniform(0.75, 1.0), 2)
    payments.append({
        'claim_id'          : int(row['claim_id']),
        'payer_id'          : int(row['payer_id']),
        'paid_amount'       : paid,
        'payment_date'      : random_date(2020, 2024),
        'payment_method'    : random.choice(PAYMENT_METHODS),
        'check_number'      : 'CHK' + ''.join(random.choices(string.digits, k=7)),
        'is_underpayment'   : is_underpay,
        'underpayment_amount': round(billed - paid, 2) if is_underpay else 0.00,
    })
df_payments = pd.DataFrame(payments)
batch_insert(df_payments, 'payments', engine)
print(f"  Done: {N_PAYMENTS} payments")
 
# ============================================================
# 12. DENIALS  (75,000 records)
# ============================================================
print("\n[12/13] Generating denials...")
denials = []
for i in range(N_DENIALS):
    denial_date = random_date(2020, 2024)
    appealed    = random.random() < 0.40
    denials.append({
        'claim_id'      : int(claim_ids['claim_id'].iloc[i % len(claim_ids)]),
        'denial_code'   : random.choice(DENIAL_CODES),
        'denial_reason' : random.choice(DENIAL_REASONS),
        'denial_date'   : denial_date,
        'appeal_status' : random.choice(APPEAL_STATUSES) if appealed else 'Not Appealed',
        'appeal_date'   : denial_date + timedelta(days=random.randint(5, 30)) if appealed else None,
        'appeal_outcome': random.choice(['Overturned', 'Upheld', 'Pending']) if appealed else None,
    })
df_denials = pd.DataFrame(denials)
batch_insert(df_denials, 'denials', engine)
print(f"  Done: {N_DENIALS} denials")
 
# ============================================================
# 13. ADJUDICATIONS  (500,000 records)
# ============================================================
print("\n[13/13] Generating adjudications...")
adjudications = []
decision_weights = [0.53, 0.136, 0.334]
for i in range(N_ADJUDICATIONS):
    row      = claim_ids.iloc[i % len(claim_ids)]
    billed   = round(random.uniform(500, 150_000), 2)
    decision = random.choices(DECISIONS, weights=decision_weights)[0]
    if decision == 'Approved':
        approved   = billed
        underpay   = 0.00
    elif decision == 'Partially Approved':
        approved   = round(billed * random.uniform(0.3, 0.8), 2)
        underpay   = round(billed - approved, 2)
    else:
        approved   = 0.00
        underpay   = billed
    adjudications.append({
        'claim_id'            : int(row['claim_id']),
        'payer_id'            : int(row['payer_id']),
        'adjudication_date'   : random_date(2020, 2024),
        'decision'            : decision,
        'approved_amount'     : approved,
        'billed_amount'       : billed,
        'underpayment_amount' : underpay,
        'adjudication_days'   : random.randint(1, 90),
        'adjudicator_id'      : 'ADJ' + ''.join(random.choices(string.digits, k=5)),
        'notes'               : synthetic_data.sentence(nb_words=6),
    })
df_adjudications = pd.DataFrame(adjudications)
batch_insert(df_adjudications, 'adjudications', engine)
print(f"  Done: {N_ADJUDICATIONS} adjudications")
 
# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*55)
print("DATA GENERATION COMPLETE")
print("="*55)
tables = ['hospitals','departments','providers','doctors',
          'insurance_payers','patients','policies','appointments',
          'claims','claim_status','payments','denials','adjudications']
total = 0
for t in tables:
    count = pd.read_sql(f"SELECT COUNT(*) as c FROM {t}", engine)['c'][0]
    print(f"  {t:<22} : {count:>10,} records")
    total += count
print(f"  {'TOTAL':<22} : {total:>10,} records")
print("="*55)
print(f"\nEncryption Key: {ENCRYPTION_KEY.decode()}")
print("Save this key — required to decrypt patient name & phone.")
