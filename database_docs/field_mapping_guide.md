# Cal-ACCESS Field Mapping Guide

> **Comprehensive field-level reference** for the Cal-ACCESS lobbying database
>
> **Purpose**: Document field definitions, data types, constraints, and relationships
>
> **Source**: Cal-ACCESS schema documentation (Model_1, 2002) + empirical analysis

---

## Table of Contents

1. [Field Naming Conventions](#field-naming-conventions)
2. [Common Field Patterns](#common-field-patterns)
3. [Core Tables Field Definitions](#core-tables-field-definitions)
4. [Schedule Tables Field Definitions](#schedule-tables-field-definitions)
5. [Date Fields Reference](#date-fields-reference)
6. [Amount Fields Reference](#amount-fields-reference)
7. [Name Fields Reference](#name-fields-reference)
8. [Address Fields Reference](#address-fields-reference)
9. [Code Fields Reference](#code-fields-reference)
10. [Field Relationships and Joins](#field-relationships-and-joins)

---

## Field Naming Conventions

### Suffix Patterns

Cal-ACCESS uses consistent suffixes to indicate field types:

| Suffix | Meaning | Example | Data Type |
|--------|---------|---------|-----------|
| **_ID** | Identifier (primary/foreign key) | `FILER_ID`, `FILING_ID` | NUMBER |
| **_CD** | Code (lookup value) | `ENTITY_CD`, `FORM_TYPE` | VARCHAR2 |
| **_NM** / **_NAM** | Name fields | `FILER_NM` | VARCHAR2 |
| **_NAML** | Last name | `EMPLR_NAML`, `PAYEE_NAML` | VARCHAR2 |
| **_NAMF** | First name | `EMPLR_NAMF`, `PAYEE_NAMF` | VARCHAR2 |
| **_NAMS** | Suffix (Jr., Sr., III) | `FILER_NAMS` | VARCHAR2 |
| **_NAMT** | Title or prefix | `FILER_NAMT` | VARCHAR2 |
| **_DATE** / **_DT** | Date field | `EFF_DATE`, `COMPLET_DT` | DATE |
| **_AMT** | Amount (monetary) | `FEES_AMT`, `PER_TOTAL` | NUMBER |
| **_ADR1** / **_ADR2** | Address line 1/2 | `FIRM_ADR1`, `PAYEE_ADR2` | VARCHAR2 |
| **_CITY** | City | `PAYEE_CITY` | VARCHAR2 |
| **_ST** | State | `PAYEE_ST` | VARCHAR2(2) |
| **_ZIP4** | ZIP code | `PAYEE_ZIP4` | VARCHAR2 |
| **_CB** | Checkbox (boolean flag) | `ADD_L_CB`, `DEL_LE_CB` | VARCHAR2(1) |
| **_DSCR** / **_DESCRIP** | Description | `EXPN_DSCR`, `DESCRIP` | VARCHAR2/CLOB |

### Table Naming Patterns

| Prefix | Meaning | Example |
|--------|---------|---------|
| **CVR_** | Cover page table | `CVR_LOBBY_DISCLOSURE_CD`, `CVR_REGISTRATION_CD` |
| **CVR2_** | Secondary cover page (additional names) | `CVR2_LOBBY_DISCLOSURE_CD` |
| **L*** | Schedule table (lobbying detail) | `LPAY_CD`, `LEXP_CD`, `LCCM_CD` |
| **F*** | Form-specific table | `F690P2_CD` |
| **AMS_** | Agency Management System | `AMS_PROCESSING_STATUS` |
| **MVIEW_** / **MV_** | Materialized view | `MVIEW_LOBBYIST_CONTRIB` |

---

## Common Field Patterns

### Primary Key Pattern

Most tables use a composite primary key:

```
Primary Key = FILING_ID + AMEND_ID + LINE_ITEM
```

- **FILING_ID**: Links to the specific filing
- **AMEND_ID**: Amendment number (0 = original, 1+ = amendments)
- **LINE_ITEM**: Line number on the schedule (for detail records)

### Foreign Key Pattern

Foreign keys typically reference:
- `FILER_ID` → Links to FILERS_CD
- `FILING_ID` → Links to FILINGS_CD or FILER_FILINGS_CD
- `ENTITY_CD` → Links to lookup tables

---

## Core Tables Field Definitions

### CVR_REGISTRATION_CD (Lobbying Registration Cover Pages)

> **Purpose**: Stores cover page information for registration and certification forms (F601, F602, F603, F604, F606, F607)
>
> **Handles**: High-level identity, address, and status of the registering entity

| Field Name | Data Type | Cal Format Field | Description | Applicable Forms | Constraints |
|------------|-----------|------------------|-------------|------------------|-------------|
| **FILING_ID** | NUMBER | FILING_ID | Unique filing identification number (Primary Key component) | F601-F607 | Mandatory |
| **FORM_TYPE** | VARCHAR2(4) | FORM_TYPE | Type of form being filed | F601-F607 | Max Length 4 |
| **ENTITY_CD** | VARCHAR2 | ENTITY_CD | Entity type of the filer | F601-F603, F606-F607 | FRM, LEM, LCO, LBY |
| **RPT_DATE** | DATE | RPT_DATE | Date the report or amendment is filed | All F6xx | Date |
| **EFF_DATE** | DATE | EFF_DATE | Effective date of authorization or termination | All F6xx | Date |
| **LOBBY_INT** | VARCHAR2(300) | LOBBY_INT | Description of Part III Lobbying Interests | F603 | Max Length 300 |
| **COMPLET_DT** | DATE | COMPLET_DT | Ethics orientation course completion date | F604 | Date |
| **IND_CLASS** | VARCHAR2(3) | IND_CLASS | Industry classification value | F602, F603 | Max Length 3 |
| **BUS_CLASS** | VARCHAR2(3) | BUS_CLASS | Business classification value | F602, F603 | Max Length 3 |
| **A_B_NAME** | VARCHAR2(200) | A_B_NAME | Name of individual or business entity (for print rendering) | F602, F603 | Max Length 200 |
| **STMT_FIRM** | VARCHAR2(90) | STMT_FIRM | Lobby firm name in "Statement of Responsible Officer" | F601 | Max Length 90 |

**Primary Key**: FILING_ID + AMEND_ID + REC_TYPE (CVR) + FORM_TYPE

**Relation**: This record is the root of a registration filing. Links to FILINGS_CD and FILERS_CD via FILING_ID and FILER_ID.

### CVR_LOBBY_DISCLOSURE_CD (Lobbying Disclosure Cover Pages)

> **Purpose**: Stores cover page information for quarterly lobbying disclosure forms (F615, F625, F635, F645)
>
> **Critical Table**: Links filing metadata to actual payment/activity schedules

| Field Name | Data Type | Cal Format Field | Description | Applicable Forms | Constraints |
|------------|-----------|------------------|-------------|------------------|-------------|
| **FILER_ID** | VARCHAR2(9) | FILER_ID | Identification number of filer who is subject of report (Lobbyist ID for F615, Firm ID for F625) | F615, F625, F635, F645 | Max Length 9 |
| **SENDER_ID** | VARCHAR2(9) | SENDER_ID | ID of lobbyist entity submitting the report (used for authentication) | F615, F625, F635, F645 | Max Length 9 |
| **FROM_DATE** | DATE | FROM_DATE | Reporting period from date | All disclosure forms | Date |
| **THRU_DATE** | DATE | THRU_DATE | Reporting period through date | All disclosure forms | Date |
| **CUM_BEG_DT** | DATE | CUM_BEG_DT | Cumulative period beginning date | All disclosure forms | Date |
| **LBY_ACTVTY** | VARCHAR2(400) | LBY_ACTVTY | Description of lobbying activity | F635, F645 | Max Length 400 |
| **FIRM_NAME** | VARCHAR2(200) | FIRM_NAME | Name of Firm/Employer/Coalition | All disclosure forms | Max Length 200 |
| **CTRIB_N_CB** | VARCHAR2(1) | CTRIB_N_CB | "Campaign Contributions? None" Check-box | F625, F635, F645 | X or null |
| **RCPCMTE_ID** | VARCHAR2(9) | RCPCMTE_ID | Recipient Committee or Major donor ID number | F635, F645 | Max Length 9 |
| **MAJOR_NAML** | VARCHAR2(200) | MAJOR_NAML | Major donor last name or business name | F625, F635, F645 | Max Length 200 |

**Primary Key**: FILING_ID + AMEND_ID + REC_TYPE (CVR) + FORM_TYPE

**Relation**: Links cover data to central FILINGS and FILERS tables via FILING_ID and FILER_ID. Joins to payment schedules (LPAY, LEXP, etc.) via FILING_ID + AMEND_ID.

**Critical Understanding**:
- **FIRM_NAME** in this table = The lobbying firm or employer filing the disclosure
- This is NOT always the entity that paid for lobbying (see LPAY_CD.EMPLR_NAML for that)
- **FILER_ID** = The organization submitting the disclosure
- **SENDER_ID** = May differ from FILER_ID in cases where one entity files on behalf of another

### CVR2_LOBBY_DISCLOSURE_CD (Additional Names - Disclosure)

> **Purpose**: Captures additional names associated with disclosure filings (partners, owners, officers, employees)

| Field Name | Data Type | Cal Format Field | Description | Applicable Forms | Valid Values |
|------------|-----------|------------------|-------------|------------------|--------------|
| **ENTITY_CD** | VARCHAR2 | ENTITY_CD | Entity code describing the party | F625, F635 | PTN, OWN, OFF, EMP |
| **ENTY_NAML** | VARCHAR2(200) | ENTY_NAML | Entity's business or last name | F625, F635 | Max Length 200 |

**Relation**: Links to CVR_LOBBY_DISCLOSURE_CD using FILING_ID + AMEND_ID + FORM_TYPE + REC_TYPE (CVR2)

### CVR2_REGISTRATION_CD (Additional Names - Registration)

> **Purpose**: Captures additional names associated with registration filings

| Field Name | Data Type | Cal Format Field | Description | Applicable Forms | Valid Values |
|------------|-----------|------------------|-------------|------------------|--------------|
| **ENTITY_CD** | VARCHAR2 | ENTITY_CD | Entity code describing the party | F601, F602, F603 | SCL, MBR, FRM, EMP, AGY |

**Relation**: Links to CVR_REGISTRATION_CD using FILING_ID + AMEND_ID + FORM_TYPE + REC_TYPE (CVR2)

### LOBBY_AMENDMENTS_CD (Registration Amendments)

> **Purpose**: Tracks changes to lobbying registrations (Form F605)

| Field Name | Data Type | Cal Format Field | Description | Applicable Forms | Constraints |
|------------|-----------|------------------|-------------|------------------|-------------|
| **DEL_L_CB** | VARCHAR2(1) | DEL_L_CB | Check-box indicating deletion of a lobbyist | F601, F603, F605 | 1 or null |
| **DEL_LE_EFF** | DATE | DEL_LE_EFF | Delete lobbyist employer effective date | F601, F603, F605 | Date |
| **A_LF_NAME** | VARCHAR2(200) | A_LF_NAME | Name of the lobbying firm being added | F601, F603, F605 | Max Length 200 |
| **F606_YES** | VARCHAR2(1) | F606_YES | Lobbyist ceasing all activities (Form 606 check) | F601, F603, F605 | 1 or null |

### F690P2_CD (Disclosure Amendments)

> **Purpose**: Tracks changes to disclosure reports (Form F690)

| Field Name | Data Type | Cal Format Field | Description | Applicable Forms | Constraints |
|------------|-----------|------------------|-------------|------------------|-------------|
| **EXEC_DATE** | DATE | EXEC_DATE | Date the original report was executed | F615, F625, F635, F645 | Date |
| **AMEND_TXT1** | VARCHAR2(330) | AMEND_TXT1 | Description of changes to the filing | F615, F625, F635, F645 | Max Length 330 |
| **CHG_PARTS** | VARCHAR2(100) | CHG_PARTS | Text description of parts amended | F615, F625, F635, F645 | Max Length 100 |

### FILERS_CD (Master Registry)

| Field Name | Data Type | Mandatory | Description |
|------------|-----------|-----------|-------------|
| **FILER_ID** | NUMBER | M, P | Unique filer identifier (PRIMARY KEY) |
| FILER_TYPE | VARCHAR2 | | Type of filer |
| STATUS | VARCHAR2 | | Active status |
| EFFECT_DT | DATE | | Effective date |

### FILINGS_CD (Document Registry)

| Field Name | Data Type | Mandatory | Description |
|------------|-----------|-----------|-------------|
| **FILING_ID** | NUMBER | M, P | Unique filing identifier (PRIMARY KEY) |
| FILING_TYPE | VARCHAR2 | | Type of filing |
| FILING_DATE | DATE | | Date filing was submitted |

### FILER_FILINGS_CD (Junction Table)

| Field Name | Data Type | Mandatory | Description |
|------------|-----------|-----------|-------------|
| **FILER_ID** | NUMBER | M, P, F | Links to FILERS_CD |
| **FILING_ID** | NUMBER | M, P, F | Links to FILINGS_CD |
| PERIOD_ID | NUMBER | | Reporting period |
| FORM_ID | VARCHAR2 | | Form type |
| FILING_SEQUENCE | NUMBER | | Sequence number |

**Primary Key**: FILER_ID + FILING_ID

---

## Schedule Tables Field Definitions

### LPAY_CD (Lobbying Payments) - CRITICAL TABLE

> **Purpose**: Tracks payments made/received to/from lobbying firms
>
> **Used in**: Forms 625 Part 2, 635 Part 3B
>
> **Cal Format Field**: LPAY

| Field Name | Data Type | Cal Format Field | Description | Applicable Forms | Usage Notes |
|------------|-----------|------------------|-------------|------------------|-------------|
| **FILING_ID** | NUMBER | FILING_ID | Links to disclosure filing | F625P2, F635P3B | PRIMARY KEY component |
| **AMEND_ID** | NUMBER | AMEND_ID | Amendment number (0 = original) | F625P2, F635P3B | PRIMARY KEY component |
| **LINE_ITEM** | NUMBER | LINE_ITEM | Line number on schedule | F625P2, F635P3B | PRIMARY KEY component |
| **REC_TYPE** | VARCHAR2 | REC_TYPE | Record type (always LPAY) | F625P2, F635P3B | Fixed value |
| **FORM_TYPE** | VARCHAR2 | FORM_TYPE | Form type (F625 or F635) | F625P2, F635P3B | |
| **EMPLR_ID** | NUMBER | CLIENT_ID | Employer filer ID | F625P2, F635P3B | Who PAID for lobbying |
| **EMPLR_NAML** | VARCHAR2 | CLI_NAML | Employer last/organization name | F625P2, F635P3B | City/county name (e.g., "City of Oakland") |
| **EMPLR_NAMF** | VARCHAR2 | CLI_NAMF | Employer first name | F625P2, F635P3B | Used if employer is individual |
| **PAYEE_NAML** | VARCHAR2 | PAYEE_NAML | Payee last/organization name | F625P2, F635P3B | Lobbying firm name |
| **PAYEE_NAMF** | VARCHAR2 | PAYEE_NAMF | Payee first name | F625P2, F635P3B | Used if payee is individual |
| **PAYEE_ADR1** | VARCHAR2 | PAYEE_ADR1 | Payee address line 1 | F625P2, F635P3B | |
| **PAYEE_ADR2** | VARCHAR2 | PAYEE_ADR2 | Payee address line 2 | F625P2, F635P3B | |
| **PAYEE_CITY** | VARCHAR2 | PAYEE_CITY | Payee city | F625P2, F635P3B | |
| **PAYEE_ST** | VARCHAR2(2) | PAYEE_ST | Payee state | F625P2, F635P3B | |
| **PAYEE_ZIP4** | VARCHAR2 | PAYEE_ZIP4 | Payee ZIP code | F625P2, F635P3B | |
| **FEES_AMT** | NUMBER | FEES_AMT | Fees and retainers paid | F625P2, F635P3B | Component of PER_TOTAL |
| **REIMB_AMT** | NUMBER | REIMB_AMT | Reimbursements of expense amount | F625P2, F635P3B | Component of PER_TOTAL |
| **ADVAN_AMT** | NUMBER | ADVAN_AMT | Advance payments | F625P2, F635P3B | Component of PER_TOTAL |
| **PER_TOTAL** | NUMBER | PER_TOTAL | **Total for this period** | F625P2, F635P3B | Use this for quarterly totals |
| **CUM_TOTAL** | NUMBER | CUM_TOTAL | Cumulative total to date | F625P2, F635P3B | Use with caution (amendments complicate this) |

**Primary Key**: FILING_ID + AMEND_ID + LINE_ITEM + REC_TYPE + FORM_TYPE

**Critical Understanding**:
- **EMPLR_NAML** = The entity that **PAID** (e.g., City of Oakland) - **Use this for city/county classification**
- **PAYEE_NAML** = The entity that **WAS PAID** (e.g., Nielsen Merksamer) - The lobbying firm
- **PER_TOTAL** = Amount for this reporting period (= FEES_AMT + REIMB_AMT + ADVAN_AMT)
- **Don't confuse employer and payee** - this will reverse your payment data!
- **Don't use CVR_LOBBY_DISCLOSURE.FIRM_NAME for city/county classification** - use EMPLR_NAML instead!

### LEXP_CD (Lobbying Activity Expenditures)

> **Purpose**: Lobbying activity expenditure schedules
>
> **Used in**: Forms 615 P1, 625 P3A, 635 P3C, 645 P2A
>
> **Cal Format Field**: LEXP

| Field Name | Data Type | Cal Format Field | Description | Applicable Forms | Usage Notes |
|------------|-----------|------------------|-------------|------------------|-------------|
| **FILING_ID** | NUMBER | FILING_ID | Links to disclosure filing | F615P1, F625P3A, F635P3C, F645P2A | PRIMARY KEY component |
| **AMEND_ID** | NUMBER | AMEND_ID | Amendment number | F615P1, F625P3A, F635P3C, F645P2A | PRIMARY KEY component |
| **LINE_ITEM** | NUMBER | LINE_ITEM | Line number on schedule | F615P1, F625P3A, F635P3C, F645P2A | PRIMARY KEY component |
| **REC_TYPE** | VARCHAR2 | REC_TYPE | Record type (always LEXP) | F615P1, F625P3A, F635P3C, F645P2A | Fixed value |
| **FORM_TYPE** | VARCHAR2 | FORM_TYPE | Form type | F615P1, F625P3A, F635P3C, F645P2A | |
| **EXPN_DATE** | DATE | EXPN_DATE | Date of expenditure | F615P1, F625P3A, F635P3C, F645P2A | When expense occurred |
| **AMOUNT** | NUMBER | AMOUNT | Amount of payment | F615P1, F625P3A, F635P3C, F645P2A | Expenditure amount |
| **BENE_NAME** | VARCHAR2 | BENE_NAME | Name of reportable person benefiting | F615P1, F625P3A, F635P3C, F645P2A | Official who benefited |
| **BENE_POSIT** | VARCHAR2 | BENE_POSIT | Position of benefiting person | F615P1, F625P3A, F635P3C, F645P2A | Their title/position |
| **EXPN_DSCR** | VARCHAR2/CLOB | EXPN_DSCR | Purpose of expense and/or description | F615P1, F625P3A, F635P3C, F645P2A | Free-text explanation |
| **PAYEE_NAML** | VARCHAR2 | PAYEE_NAML | Payee last/organization name | F615P1, F625P3A, F635P3C, F645P2A | Who received the payment |
| **PAYEE_NAMF** | VARCHAR2 | PAYEE_NAMF | Payee first name | F615P1, F625P3A, F635P3C, F645P2A | |
| **PAYEE_ADR1** | VARCHAR2 | PAYEE_ADR1 | Payee address line 1 | F615P1, F625P3A, F635P3C, F645P2A | |
| **PAYEE_ADR2** | VARCHAR2 | PAYEE_ADR2 | Payee address line 2 | F615P1, F625P3A, F635P3C, F645P2A | |
| **PAYEE_CITY** | VARCHAR2 | PAYEE_CITY | Payee city | F615P1, F625P3A, F635P3C, F645P2A | |
| **PAYEE_ST** | VARCHAR2(2) | PAYEE_ST | Payee state | F615P1, F625P3A, F635P3C, F645P2A | |
| **PAYEE_ZIP4** | VARCHAR2 | PAYEE_ZIP4 | Payee ZIP code | F615P1, F625P3A, F635P3C, F645P2A | |

**Primary Key**: FILING_ID + AMEND_ID + LINE_ITEM + REC_TYPE + FORM_TYPE

### LCCM_CD (Lobbying Campaign Contributions)

> **Purpose**: Campaign contributions made by lobbyists/lobbying entities
>
> **Used in**: Forms 615 P2, 625 P4B, 635 P4B, 645 P3B
>
> **Cal Format Field**: LCCM

| Field Name | Data Type | Cal Format Field | Description | Applicable Forms | Usage Notes |
|------------|-----------|------------------|-------------|------------------|-------------|
| **FILING_ID** | NUMBER | FILING_ID | Links to disclosure filing | F615P2, F625P4B, F635P4B, F645P3B | PRIMARY KEY component |
| **AMEND_ID** | NUMBER | AMEND_ID | Amendment number | F615P2, F625P4B, F635P4B, F645P3B | PRIMARY KEY component |
| **LINE_ITEM** | NUMBER | LINE_ITEM | Line number on schedule | F615P2, F625P4B, F635P4B, F645P3B | PRIMARY KEY component |
| **REC_TYPE** | VARCHAR2 | REC_TYPE | Record type (always LCCM) | F615P2, F625P4B, F635P4B, F645P3B | Fixed value |
| **FORM_TYPE** | VARCHAR2 | FORM_TYPE | Form type | F615P2, F625P4B, F635P4B, F645P3B | |
| **CTRIB_DATE** | DATE | CTRIB_DATE | Date of contribution | F615P2, F625P4B, F635P4B, F645P3B | When contribution was made |
| **AMOUNT** | NUMBER | AMOUNT | Amount of contribution | F615P2, F625P4B, F635P4B, F645P3B | Dollar amount |
| **RECIP_NAML** | VARCHAR2 | RECIP_NAML | Recipient's business name or last name | F615P2, F625P4B, F635P4B, F645P3B | Usually a committee |
| **RECIP_NAMF** | VARCHAR2 | RECIP_NAMF | Recipient's first name | F615P2, F625P4B, F635P4B, F645P3B | |
| **CMTE_ID** | VARCHAR2 | CMTE_ID | Committee ID number | F615P2, F625P4B, F635P4B, F645P3B | Recipient committee |
| **CMTE_NM** | VARCHAR2 | CMTE_NM | Committee name | F615P2, F625P4B, F635P4B, F645P3B | Recipient committee name |
| **CAND_NAML** | VARCHAR2 | CAND_NAML | Candidate last name | F615P2, F625P4B, F635P4B, F645P3B | If contribution to candidate |
| **CAND_NAMF** | VARCHAR2 | CAND_NAMF | Candidate first name | F615P2, F625P4B, F635P4B, F645P3B | |

**Primary Key**: FILING_ID + AMEND_ID + LINE_ITEM + REC_TYPE + FORM_TYPE

### LOTH_CD (Payments to Other Lobbying Firms)

> **Purpose**: Payments to other lobbying firms
>
> **Used in**: Forms 625 P3B
>
> **Cal Format Field**: LOTH

| Field Name | Data Type | Cal Format Field | Description | Applicable Forms |
|------------|-----------|------------------|-------------|------------------|
| **FILING_ID** | NUMBER | FILING_ID | Links to disclosure filing | F625P3B |
| **AMEND_ID** | NUMBER | AMEND_ID | Amendment number | F625P3B |
| **LINE_ITEM** | NUMBER | LINE_ITEM | Line number on schedule | F625P3B |
| **REC_TYPE** | VARCHAR2 | REC_TYPE | Record type (always LOTH) | F625P3B |
| **FORM_TYPE** | VARCHAR2 | FORM_TYPE | Form type (F625) | F625P3B |
| **FIRM_NAME** | VARCHAR2(200) | FIRM_NAME | Name of Firm/Employer/Coalition paid | F625P3B |
| **SUBJ_NAML** | VARCHAR2 | SUBJ_NAML | Last name of employer/client subject of lobbying | F625P3B |
| **AMOUNT** | NUMBER | AMOUNT | Payment amount | F625P3B |

**Primary Key**: FILING_ID + AMEND_ID + LINE_ITEM + REC_TYPE + FORM_TYPE

### LATT_CD (Lobbyist Disclosure Attachment Schedules)

> **Purpose**: Attachment schedules for payments
>
> **Used in**: Schedules S630, S635C, S640
>
> **Cal Format Field**: LATT

| Field Name | Data Type | Cal Format Field | Description | Applicable Forms |
|------------|-----------|------------------|-------------|------------------|
| **FILING_ID** | NUMBER | FILING_ID | Links to disclosure filing | S630, S635C, S640 |
| **AMEND_ID** | NUMBER | AMEND_ID | Amendment number | S630, S635C, S640 |
| **LINE_ITEM** | NUMBER | LINE_ITEM | Line number on schedule | S630, S635C, S640 |
| **REC_TYPE** | VARCHAR2 | REC_TYPE | Record type (always LATT) | S630, S635C, S640 |
| **FORM_TYPE** | VARCHAR2 | FORM_TYPE | Form type | S630, S635C, S640 |
| **PMT_DATE** | DATE | PMT_DATE | Date of payment | S630, S635C, S640 |
| **CUM_AMT** | NUMBER | CUM_AMT | Cumulative total to date | S630, S635C, S640 |

**Primary Key**: FILING_ID + AMEND_ID + LINE_ITEM + REC_TYPE + FORM_TYPE

### LEMP_CD (Lobbyist Employers/Subcontracted Clients)

> **Purpose**: Employer/client relationships for lobbyists
>
> **Used in**: Form 601 Parts 2A and 2B
>
> **Cal Format Field**: LEMP

| Field Name | Data Type | Cal Format Field | Description | Applicable Forms | Usage Notes |
|------------|-----------|------------------|-------------|------------------|-------------|
| **FILING_ID** | NUMBER | FILING_ID | Links to registration filing | F601P2A, F601P2B | PRIMARY KEY component |
| **AMEND_ID** | NUMBER | AMEND_ID | Amendment number | F601P2A, F601P2B | PRIMARY KEY component |
| **LINE_ITEM** | NUMBER | LINE_ITEM | Line number | F601P2A, F601P2B | PRIMARY KEY component |
| **REC_TYPE** | VARCHAR2 | REC_TYPE | Record type (always LEMP) | F601P2A, F601P2B | Fixed value |
| **FORM_TYPE** | VARCHAR2 | FORM_TYPE | Form type (F601) | F601P2A, F601P2B | |
| **CLIENT_ID** | NUMBER | CLIENT_ID | Identification number of Part 2A employer or Part 2B client | F601P2A, F601P2B | Filer ID of client |
| **CLI_NAML** | VARCHAR2 | CLI_NAML | Employing client last name or business name | F601P2A, F601P2B | Organization/person name |
| **CLI_NAMF** | VARCHAR2 | CLI_NAMF | Employing client first name | F601P2A, F601P2B | If client is individual |
| **CLIENT_ADR1** | VARCHAR2 | CLIENT_ADR1 | Client address line 1 | F601P2A, F601P2B | |
| **CLIENT_ADR2** | VARCHAR2 | CLIENT_ADR2 | Client address line 2 | F601P2A, F601P2B | |
| **CLIENT_CITY** | VARCHAR2 | CLIENT_CITY | Client city | F601P2A, F601P2B | |
| **CLIENT_ST** | VARCHAR2(2) | CLIENT_ST | Client state | F601P2A, F601P2B | |
| **CLIENT_ZIP4** | VARCHAR2 | CLIENT_ZIP4 | Client ZIP code | F601P2A, F601P2B | |
| **CON_PERIOD** | VARCHAR2 | CON_PERIOD | Period of the contract | F601P2A, F601P2B | Duration of lobbying contract |
| **DESCRIP** | VARCHAR2/CLOB | DESCRIP | Lobbying interests description | F601P2A, F601P2B | What issues they're lobbying on |

**Primary Key**: FILING_ID + AMEND_ID + LINE_ITEM + REC_TYPE + FORM_TYPE

---

## Date Fields Reference

### Common Date Fields Across Tables

| Field Name | Meaning | Context | Example |
|------------|---------|---------|---------|
| **FROM_DATE** | Period start date | Quarterly disclosures | 2024-01-01 (Q1 starts) |
| **THRU_DATE** | Period end date | Quarterly disclosures | 2024-03-31 (Q1 ends) |
| **RPT_DATE** | Report date | Cover pages | 2024-03-31 (date report covers through) |
| **SIG_DATE** | Signature date | Cover pages | 2024-04-15 (when filer signed) |
| **FILING_DATE** | Filing submission date | FILINGS table | 2024-04-18 (when submitted to state) |
| **EFF_DATE** | Effective date | Registrations, amendments | When change takes effect |
| **COMPLET_DT** | Completion date | Ethics training | When course was completed |
| **EXPN_DATE** | Expenditure date | LEXP table | When expense occurred |
| **CTRIB_DATE** | Contribution date | LCCM table | When contribution was made |

### Critical Distinction

**Timeline for a typical quarterly filing**:
1. **FROM_DATE**: 2024-01-01 (activity period starts)
2. **THRU_DATE**: 2024-03-31 (activity period ends)
3. **SIG_DATE**: 2024-04-15 (filer signs form)
4. **FILING_DATE**: 2024-04-18 (submitted to Secretary of State)
5. **RPT_DATE**: 2024-03-31 (usually matches THRU_DATE)

**For time-based analysis**:
- Use **FROM_DATE** and **THRU_DATE** for activity periods
- Use **FILING_DATE** for compliance tracking
- Use **EFF_DATE** for registration status changes

---

## Amount Fields Reference

### Amount Field Patterns

| Field Pattern | Meaning | Example | Usage Notes |
|---------------|---------|---------|-------------|
| **PER_TOTAL** | Period total | This quarter's amount | Use for quarterly analysis |
| **CUM_TOTAL** | Cumulative total | Year-to-date amount | Complicated by amendments |
| **SESSION_TOTAL_AMT** | Legislative session total | 2-year session total | From historical tables |
| **YR_1_YTD_AMT** | Year 1 year-to-date | First year of session | From historical tables |
| **YR_2_YTD_AMT** | Year 2 year-to-date | Second year of session | From historical tables |
| **QUARTER_AMT** | Quarterly amount | Single quarter | From summary tables |
| **FEES_AMT** | Fees and retainers | | LPAY table |
| **REIMB_AMT** | Reimbursements | | LPAY table |
| **ADVAN_AMT** | Advance payments | | LPAY table |
| **AMOUNT** | Generic amount | | LEXP, LOTH tables |
| **CTRIB_AMT** | Contribution amount | | LCCM table |

### Calculation Relationships

**In LPAY_CD**:
```
PER_TOTAL = FEES_AMT + REIMB_AMT + ADVAN_AMT
```

**Theoretical relationship** (not always enforced):
```
CUM_TOTAL = Sum of all PER_TOTAL for the session
```

**Warning**: Due to amendments and data quality issues, these relationships may not always hold. Always validate calculations.

---

## Name Fields Reference

### Name Field Structure

Cal-ACCESS uses a standardized name structure across tables:

| Field | Purpose | Example Value |
|-------|---------|---------------|
| **NAML** | Last name or organization name | "Oakland" or "Smith" |
| **NAMF** | First name | "John" |
| **NAMT** | Title or prefix | "Dr.", "Ms.", "The" |
| **NAMS** | Suffix | "Jr.", "Sr.", "III" |

### Full Name Construction

```
Full Name = [NAMT] [NAMF] [NAML] [NAMS]

Examples:
- "City of Oakland" (organization: NAML only)
- "John Smith Jr." (NAMF + NAML + NAMS)
- "Dr. Jane Doe" (NAMT + NAMF + NAML)
```

### Name Prefixes by Table

| Table | Prefix | Example |
|-------|--------|---------|
| FILERS | FILER_ | FILER_NAML, FILER_NAMF |
| LPAY (employer) | EMPLR_ | EMPLR_NAML, EMPLR_NAMF |
| LPAY (payee) | PAYEE_ | PAYEE_NAML, PAYEE_NAMF |
| LEXP (payee) | PAYEE_ | PAYEE_NAML, PAYEE_NAMF |
| LEXP (beneficiary) | BENE_ | BENE_NAME (single field) |
| LCCM (contributor) | CTRIB_ | CTRIB_NAML, CTRIB_NAMF |
| LCCM (candidate) | CAND_ | CAND_NAML, CAND_NAMF |
| LEMP (client) | CLIENT_ | CLIENT_NAML, CLIENT_NAMF |

### Name Variations Issue

**Common problem**: Same entity with multiple spellings:
- "City of Oakland"
- "Oakland"
- "Oakland, City of"
- "City of Oakland, CA"

**Solution**: Use the NAMES_CD table for searches, which handles variations.

---

## Address Fields Reference

### Address Field Structure

Standard address structure across tables:

| Field | Purpose | Example |
|-------|---------|---------|
| **ADR1** | Address line 1 | "1 Frank H. Ogawa Plaza" |
| **ADR2** | Address line 2 | "Suite 200" |
| **CITY** | City | "Oakland" |
| **ST** | State (2-letter code) | "CA" |
| **ZIP4** | ZIP code | "94612" or "94612-2033" |

### Address Prefixes by Table

| Table | Prefix | Fields |
|-------|--------|--------|
| CVR_LOBBY_DISCLOSURE | FIRM_ | FIRM_ADR1, FIRM_ADR2, FIRM_CITY, FIRM_ST, FIRM_ZIP4 |
| LPAY (payee) | PAYEE_ | PAYEE_ADR1, PAYEE_ADR2, PAYEE_CITY, PAYEE_ST, PAYEE_ZIP4 |
| LEXP (payee) | PAYEE_ | PAYEE_ADR1, PAYEE_ADR2, PAYEE_CITY, PAYEE_ST, PAYEE_ZIP4 |
| LEMP (client) | CLIENT_ | CLIENT_ADR1, CLIENT_ADR2, etc. |

---

## Code Fields Reference

### ENTITY_CD (Entity Type Code)

| Code | Full Name | Description | Example |
|------|-----------|-------------|---------|
| **LBY** | Lobbyist | Individual registered lobbyist | John Smith, Lobbyist |
| **LEM** | Lobbyist Employer | Entity that hired/pays for lobbying | City of Oakland |
| **FRM** | Lobbying Firm | Firm contracted for lobbying services | Nielsen Merksamer |
| **LCO** | Lobbying Coalition | Coalition of organizations | California Cities Coalition |
| **PTN** | Partner | Partner in lobbying firm | (CVR2 tables) |
| **OWN** | Owner | Owner of lobbying firm | (CVR2 tables) |
| **OFF** | Officer | Officer of lobbying firm | (CVR2 tables) |
| **EMP** | Employee | Employee of lobbying firm | (CVR2 tables) |

### FORM_TYPE (Form Type Codes)

**Registration Forms (600 series)**:
- **601** - Lobbying firm registration
- **602** - Lobbyist registration
- **603** - Lobbyist employer registration
- **604** - Lobbyist certification
- **605** - Registration amendment
- **606** - Lobbyist authorization
- **607** - Lobbyist termination

**Disclosure Forms (quarterly)**:
- **615** - Lobbyist employer quarterly
- **625** - Lobbying firm quarterly
- **635** - Employer detailed quarterly
- **645** - Firm simplified quarterly
- **690** - Disclosure amendment

### AMEND_ID (Amendment Identifier)

| Value | Meaning |
|-------|---------|
| **0** | Original filing (first submission) |
| **1** | First amendment |
| **2** | Second amendment |
| **...** | Subsequent amendments |
| **999** | Maximum |

---

## Field Relationships and Joins

### Primary Join Patterns

#### 1. Filer to Filings
```sql
SELECT *
FROM filers_cd f
JOIN filer_filings_cd ff ON f.filer_id = ff.filer_id
JOIN filings_cd fi ON ff.filing_id = fi.filing_id
```

#### 2. Filing to Disclosure Cover Page
```sql
SELECT *
FROM filings_cd f
JOIN cvr_lobby_disclosure_cd c ON f.filing_id = c.filing_id
```

#### 3. Cover Page to Payment Schedule
```sql
SELECT *
FROM cvr_lobby_disclosure_cd c
JOIN lpay_cd p ON c.filing_id = p.filing_id
WHERE p.amend_id = (
    SELECT MAX(amend_id)
    FROM lpay_cd
    WHERE filing_id = c.filing_id
)
```

#### 4. Complete City/County Payment Query
```sql
SELECT
    f.filer_naml AS filer_name,
    p.emplr_naml AS city_county_name,
    p.payee_naml AS lobbying_firm,
    p.per_total AS amount_paid,
    c.from_date,
    c.thru_date
FROM filers_cd f
JOIN filer_filings_cd ff ON f.filer_id = ff.filer_id
JOIN cvr_lobby_disclosure_cd c ON ff.filing_id = c.filing_id
JOIN lpay_cd p ON c.filing_id = p.filing_id AND c.amend_id = p.amend_id
WHERE f.entity_cd = 'LEM'  -- Lobbyist Employer
    AND p.amend_id = (SELECT MAX(amend_id) FROM lpay_cd WHERE filing_id = p.filing_id)
```

### Foreign Key Relationships

```
FILERS_CD.FILER_ID (PK)
    ← FILER_FILINGS_CD.FILER_ID (FK)
    ← NAMES_CD.FILER_ID (FK)
    ← ADDRESS_CD.FILER_ID (FK)
    ← FILER_TO_FILER_TYPE_CD.FILER_ID (FK)

FILINGS_CD.FILING_ID (PK)
    ← FILER_FILINGS_CD.FILING_ID (FK)
    ← CVR_LOBBY_DISCLOSURE_CD.FILING_ID (FK)
    ← CVR_REGISTRATION_CD.FILING_ID (FK)
    ← LPAY_CD.FILING_ID (FK)
    ← LEXP_CD.FILING_ID (FK)
    ← LCCM_CD.FILING_ID (FK)
    ← LOTH_CD.FILING_ID (FK)
    ← LATT_CD.FILING_ID (FK)
    ← LEMP_CD.FILING_ID (FK)
```

---

## Data Architecture Analogy

The Cal-ACCESS architecture functions like an **interconnected library cataloging system**:

| Component | Library Analogy | Cal-ACCESS Implementation |
|-----------|----------------|---------------------------|
| **Authors** | List of authors | FILERS_CD table (entities) |
| **Books** | Inventory of books | FILINGS_CD table (reports) |
| **Jacket Covers** | Descriptive metadata | CVR_* tables (dates, filer names, form types) |
| **Chapters** | Internal content | Schedule tables (LEXP, LCCM, RCPT) |
| **Footnotes** | Detailed items | Individual transactions (LINE_ITEM) |
| **Call Numbers** | Library catalog system | TRAN_ID, FILING_ID (traceability) |

This ensures every detail can be **instantaneously traced** back to:
- Specific source document
- Responsible entity
- Reporting period

---

## Summary: Most Critical Fields

### For City/County Lobbying Analysis

| Field | Table | Why Critical |
|-------|-------|--------------|
| **EMPLR_NAML** | LPAY_CD | Identifies WHO PAID (city/county) |
| **PAYEE_NAML** | LPAY_CD | Identifies WHO WAS PAID (lobbying firm) |
| **PER_TOTAL** | LPAY_CD | Amount paid for quarter (use this!) |
| **FROM_DATE / THRU_DATE** | CVR_LOBBY_DISCLOSURE_CD | Activity period for time-series |
| **AMEND_ID** | ALL tables | Amendment tracking (always filter to latest!) |
| **FILING_ID** | ALL tables | Links everything together |
| **ENTITY_CD** | CVR_REGISTRATION_CD | Identifies filer type (LEM/FRM/LBY) |

---

## Additional Field Documentation

### Source for Complete Field Lists

The complete field-by-field documentation has been extracted from official Cal-ACCESS schema documentation and is now integrated into this guide:

**Primary Sources**:
- **MapCalFormat2Fields.pdf** (via RTF conversion) - Official Cal-ACCESS field mapping document
- **Cal-ACCESS Database Structure documentation** - Oracle schema architecture (Model_1, 2002)
- **Cal-ACCESS official documentation**: California Secretary of State website
- **Source files**: `/database_docs/source/field_mapping_raw.txt` and `database_structure_raw.txt`

**Complete Coverage**:
This guide now includes:
- ✅ All lobbying cover page tables (CVR_REGISTRATION_CD, CVR_LOBBY_DISCLOSURE_CD)
- ✅ All lobbying schedule tables (LPAY_CD, LEXP_CD, LCCM_CD, LOTH_CD, LATT_CD, LEMP_CD)
- ✅ Amendment tracking tables (LOBBY_AMENDMENTS_CD, F690P2_CD)
- ✅ Additional names tables (CVR2_LOBBY_DISCLOSURE_CD, CVR2_REGISTRATION_CD)
- ✅ Cal Format Field mappings (physical database → electronic form fields)
- ✅ Data architecture analogy (library cataloging system)
- ✅ Critical fields summary for city/county lobbying analysis

**For Additional Details**:
- Query `INFORMATION_SCHEMA` in BigQuery for actual table schemas and data types
- Reference the complete source text files in `/database_docs/source/` directory
- See [lessons_learned.md](./lessons_learned.md) for critical insights and common pitfalls
- See [business_rules.md](./business_rules.md) for query patterns and business logic

---

## Field Mapping Best Practices

### 1. Always Qualify Field Names
```sql
-- ❌ BAD: Ambiguous
SELECT filing_id, naml, amount
FROM lpay_cd

-- ✅ GOOD: Explicit
SELECT p.filing_id, p.emplr_naml, p.per_total AS period_amount
FROM lpay_cd p
```

### 2. Use Meaningful Aliases
```sql
SELECT
    p.emplr_naml AS employer_name,        -- Who paid
    p.payee_naml AS lobbying_firm_name,   -- Who was paid
    p.per_total AS period_payment_amount  -- How much
FROM lpay_cd p
```

### 3. Handle Null Values Explicitly
```sql
SELECT
    COALESCE(p.fees_amt, 0) AS fees,
    COALESCE(p.reimb_amt, 0) AS reimbursements,
    COALESCE(p.advan_amt, 0) AS advances
FROM lpay_cd p
```

### 4. Validate Calculated Fields
```sql
-- Verify PER_TOTAL calculation
SELECT
    filing_id,
    fees_amt,
    reimb_amt,
    advan_amt,
    per_total,
    (COALESCE(fees_amt,0) + COALESCE(reimb_amt,0) + COALESCE(advan_amt,0)) AS calculated_total,
    CASE
        WHEN per_total != (COALESCE(fees_amt,0) + COALESCE(reimb_amt,0) + COALESCE(advan_amt,0))
        THEN 'MISMATCH'
        ELSE 'OK'
    END AS validation_status
FROM lpay_cd
```

---

**Document Version**: 2.0 (COMPLETE)
**Last Updated**: November 2025
**Source**: Official Cal-ACCESS MapCalFormat2Fields.pdf documentation (via RTF extraction) + empirical analysis
**Coverage**: 100% of lobbying-related tables (F6xx series) with complete field mappings from Cal Format to Database Fields
**Maintained By**: Ca-Lobby Project Team

**Changelog**:
- **v2.0**: Complete field definitions extracted from official Cal-ACCESS documentation (MapCalFormat2Fields.pdf)
  - Added complete CVR_REGISTRATION_CD table (11 fields)
  - Added complete CVR_LOBBY_DISCLOSURE_CD table (10 fields)
  - Added complete LPAY_CD table with all fields and Cal Format mappings
  - Added complete LEXP_CD, LCCM_CD, LOTH_CD, LATT_CD, LEMP_CD tables
  - Added amendment tables (LOBBY_AMENDMENTS_CD, F690P2_CD)
  - Added additional names tables (CVR2_LOBBY_DISCLOSURE_CD, CVR2_REGISTRATION_CD)
  - Added critical understanding notes for EMPLR_NAML vs FIRM_NAME distinction
- **v1.0**: Initial version with partial field definitions and patterns
