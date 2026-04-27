# 🏥 Healthcare Claims Analytics Platform

Weasley Healthcare

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge\&logo=postgresql\&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Power BI](https://img.shields.io/badge/PowerBI-F2C811?style=for-the-badge\&logo=powerbi\&logoColor=black)

---

## 📌 Project Overview

Weasley Healthcare's revenue cycle was fragmented across multiple systems with no unified view of claims, billing, payer performance, or financial outcomes. This project builds a **centralized Healthcare Claims Intelligence Platform** that replaces manual, Excel-based reporting with an integrated enterprise-wide analytics solution.

The platform provides end-to-end **claims-to-cash visibility** across all revenue cycle domains — from patient encounter through payment reconciliation.

---

## Key Highlights

* Built a **2.4M+ record healthcare dataset** using Python (Faker, Pandas, NumPy)
* Designed a **14-table star schema** in PostgreSQL
* Implemented **HIPAA-compliant encryption (AES-128)** for sensitive fields
* Developed a **5-page Power BI dashboard** covering claims, payments, denials, and payer performance
* Identified **revenue leakage through underpayments (11.4%) and denial trends**

---

## 📥 Download Power BI Dashboard

👉 [Download Dashboard (.pbix)](https://drive.google.com/uc?export=download&id=1tJvZPnzPWubAuKUnnadSBRhgQd1r-DJ7)

---

## 📊 Dashboard Preview

### 🏠 Landing Page

![Landing](dashboard_screenshots/1.Landing%20page.png)

### 📈 Payer Performance

![Payer](dashboard_screenshots/2.Payer%20performance.png)

### 💰 Financial Payments

![Financial](dashboard_screenshots/3.Financial%20Payments.png)

### ⏳ Claim Aging

![Aging](dashboard_screenshots/4.claim%20aging.png)

### 🚫 Denial Analysis

![Denial](dashboard_screenshots/5.Denial%20Analysis.png)

---

## 🎯 Business Problem

| Pain Point                     | Impact               |
| ------------------------------ | -------------------- |
| Fragmented data across systems | No unified view      |
| Manual Excel reporting         | Delayed decisions    |
| No denial visibility           | Revenue leakage      |
| Inconsistent KPIs              | Unreliable reporting |
| No payer intelligence          | Weak negotiations    |

---

## 🏗️ Solution Architecture

```
Source Systems (OLTP)
        ↓
Python Data Generation (Faker + Pandas + NumPy)
        ↓
HIPAA Encryption (Fernet AES-128)
        ↓
PostgreSQL Database (Star Schema)
        ↓
Power BI Dashboard
        ↓
Insights & Decision Making
```

---

## 🛠️ Tech Stack

| Layer           | Technology                    | Purpose            |
| --------------- | ----------------------------- | ------------------ |
| Database        | PostgreSQL                    | Analytical storage |
| Data Generation | Python (Faker, Pandas, NumPy) | Synthetic data     |
| Encryption      | Cryptography (Fernet AES-128) | HIPAA compliance   |
| Connector       | SQLAlchemy, Psycopg2          | DB connection      |
| Visualization   | Power BI                      | Dashboard          |
| Compliance      | HIPAA                         | Data protection    |

---

## 🗄️ Database Schema

### 14 Tables | Star Schema | 2.4M+ Records

| Table            | Records       | Description            |
| ---------------- | ------------- | ---------------------- |
| hospitals        | 50            | Hospital data          |
| departments      | 200           | Department details     |
| providers        | 500           | Healthcare providers   |
| doctors          | 1,000         | Physician details      |
| insurance_payers | 20            | Insurance companies    |
| patients         | 100,000       | Encrypted patient data |
| policies         | 150,000       | Insurance policies     |
| appointments     | 300,000       | Visit records          |
| claims           | 500,000       | Core fact table        |
| claim_status     | 500,000       | Claim lifecycle        |
| payments         | 350,000       | Payment data           |
| denials          | 75,000        | Denial records         |
| adjudications    | 500,000       | Payer decisions        |
| **TOTAL**        | **2,476,770** |                        |

---

## 🔐 HIPAA Compliance

* All data is **100% synthetic** (Faker-generated)
* Patient name & phone stored using **AES-128 encryption**
* No real patient data used
* Encryption key must be stored securely

---

## 📊 Power BI Dashboard

### Pages Overview

* **Executive Summary** – KPIs & trends
* **Payer Performance** – Approval, denial, payments
* **Financial Analysis** – Cash flow & underpayments
* **Operations & Aging** – Claim delays & processing
* **Denial Analysis** – Root cause insights

---

## 📐 DAX Measures

```dax
First Pass Rate =
DIVIDE(
    COUNTROWS(FILTER(claims, claims[is_first_pass] = TRUE())),
    COUNTROWS(claims), 0
) * 100

Denial Rate =
DIVIDE(
    COUNTROWS(FILTER(claims, claims[claim_status] = "Denied")),
    COUNTROWS(claims), 0
) * 100

Underpayment Rate =
DIVIDE(
    COUNTROWS(FILTER(payments, payments[is_underpayment] = TRUE())),
    COUNTROWS(payments), 0
) * 100

Outstanding Claims Amount =
CALCULATE(
    SUM(claims[billed_amount]),
    claims[claim_status] IN {"Pending", "Submitted", "Acknowledged"}
)
```

---

## 📈 Key KPIs

| KPI                   |
| --------------------- |
| First Pass Rate       |
| Denial Rate           |
| Underpayment Rate     |
| Avg Adjudication Days |
| Approval Rate         |

---



*Built as part of Zestrics Data Analytics Internship Program*
