CREATE TABLE hospitals (
    hospital_id     SERIAL PRIMARY KEY,
    hospital_name   VARCHAR(150) NOT NULL,
    hptl_location   VARCHAR(200),
    hptl_state      VARCHAR(50),
    city            VARCHAR(100),
    zip_code        VARCHAR(10),
    bed_count       INT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE departments (
department_id SERIAL PRIMARY KEY,
dept_name VARCHAR(100) NOT NULL,
dept_code VARCHAR(20),
hospital_id INT NOT NULL REFERENCES hospitals(hospital_id),
dept_head VARCHAR(100),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE providers (
provider_id SERIAL PRIMARY KEY,
provider_name VARCHAR(150) NOT NULL,
provider_type VARCHAR(50),
npi_number VARCHAR(20) UNIQUE,
hospital_id INT NOT NULL REFERENCES hospitals(hospital_id),
specialty VARCHAR(100),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE doctors (
doctor_id SERIAL PRIMARY KEY,
doctor_name VARCHAR(150) NOT NULL,
specialty VARCHAR(100),
license_number VARCHAR(30) UNIQUE,
npi_number VARCHAR(20) UNIQUE,
department_id INT REFERENCES departments(department_id),
hospital_id INT NOT NULL REFERENCES hospitals(hospital_id),
years_exp INT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE insurance_payers (
    payer_id        SERIAL PRIMARY KEY,
    payer_name      VARCHAR(100) NOT NULL,
    payer_type      VARCHAR(50),
    payer_code      VARCHAR(20) UNIQUE,
    payer_state     VARCHAR(50),
    contact_phone   VARCHAR(60),
    contact_email   VARCHAR(100),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE patients (
    patient_id      SERIAL PRIMARY KEY,
    name_encrypted  BYTEA NOT NULL,
    phone_encrypted BYTEA NOT NULL,
    dob             DATE,
    gender          VARCHAR(10),
    address         VARCHAR(250),
    city            VARCHAR(100),
    zip_code        VARCHAR(10),
    insurance_type  VARCHAR(50),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE policies (
    policy_id           SERIAL PRIMARY KEY,
    patient_id          INT NOT NULL REFERENCES patients(patient_id),
    payer_id            INT NOT NULL REFERENCES insurance_payers(payer_id),
    policy_number       VARCHAR(30) UNIQUE,
    coverage_type       VARCHAR(50),
    start_date          DATE NOT NULL,
    end_date            DATE,
    premium_amount      DECIMAL(10,2),
    deductible_amount   DECIMAL(10,2),
    copay_amount        DECIMAL(10,2),
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE appointments (
appointment_id SERIAL PRIMARY KEY,
patient_id INT NOT NULL REFERENCES patients(patient_id),
doctor_id INT NOT NULL REFERENCES doctors(doctor_id),
appointment_date DATE NOT NULL,
appointment_time TIME,
visit_type VARCHAR(50),
department_id INT REFERENCES departments(department_id),
diagnosis_code VARCHAR(20),
procedure_code VARCHAR(20),
status VARCHAR(30),
notes TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE claims (
claim_id SERIAL PRIMARY KEY,
patient_id INT NOT NULL REFERENCES patients(patient_id),
doctor_id INT NOT NULL REFERENCES doctors(doctor_id),
payer_id INT NOT NULL REFERENCES insurance_payers(payer_id),
policy_id INT NOT NULL REFERENCES policies(policy_id),
appointment_id INT REFERENCES appointments(appointment_id),
department_id INT REFERENCES departments(department_id),
claim_number VARCHAR(30) UNIQUE,
submission_date DATE NOT NULL,
service_date DATE NOT NULL,
billed_amount DECIMAL(12,2) NOT NULL,
diagnosis_code VARCHAR(20),
procedure_code VARCHAR(20),
claim_type VARCHAR(30),
claim_status VARCHAR(30),
is_first_pass BOOLEAN,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE claim_status (
status_id SERIAL PRIMARY KEY,
claim_id INT NOT NULL REFERENCES claims(claim_id),
status_code VARCHAR(20) NOT NULL,
status_description VARCHAR(200),
status_date DATE NOT NULL,
updated_by VARCHAR(100),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE payments (
payment_id SERIAL PRIMARY KEY,
claim_id INT NOT NULL REFERENCES claims(claim_id),
payer_id INT NOT NULL REFERENCES insurance_payers(payer_id),
paid_amount DECIMAL(12,2) NOT NULL,
payment_date DATE NOT NULL,
payment_method VARCHAR(50),
check_number VARCHAR(30),
is_underpayment BOOLEAN DEFAULT FALSE,
underpayment_amount DECIMAL(12,2) DEFAULT 0.00,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE denials (
denial_id SERIAL PRIMARY KEY,
claim_id INT NOT NULL REFERENCES claims(claim_id),
denial_code VARCHAR(20) NOT NULL,
denial_reason VARCHAR(250),
denial_date DATE NOT NULL,
appeal_status VARCHAR(30),
appeal_date DATE,
appeal_outcome VARCHAR(100),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE adjudications (
adjudication_id SERIAL PRIMARY KEY,
claim_id INT NOT NULL REFERENCES claims(claim_id),
payer_id INT NOT NULL REFERENCES insurance_payers(payer_id),
adjudication_date DATE NOT NULL,
decision VARCHAR(30),
approved_amount DECIMAL(12,2),
billed_amount DECIMAL(12,2),
underpayment_amount DECIMAL(12,2) DEFAULT 0.00,
adjudication_days INT,
adjudicator_id VARCHAR(50),
notes TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
