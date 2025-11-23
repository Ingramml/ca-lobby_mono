# Cal-ACCESS Lobbying Database Structure

> **Expert Overview** of the Cal-ACCESS Lobbying Database Structure
>
> **Source**: Cal-ACCESS Physical Data Model (Model_1, created February 21, 2002)
>
> **Database Type**: Oracle Database
>
> **System**: California Automated Lobbying and Campaign Contribution & Expenditure Search System

---

## Table of Contents

1. [System Context and Architecture](#system-context-and-architecture)
2. [Core Filer and Filing Management](#core-filer-and-filing-management)
3. [Lobbying Registration Data (Forms 600 Series)](#lobbying-registration-data-structures-forms-600-series)
4. [Lobbying Disclosure Data (Forms 615, 625, 635, 645)](#lobbying-disclosure-data-structures-forms-615-625-635-645)
5. [Lobbyist Relationship and Historical Data](#lobbyist-relationship-and-historical-data)
6. [Data Model Technical Properties](#data-model-technical-properties)

---

## System Context and Architecture

The Cal-ACCESS system is designed to manage and disclose electronic and paper filings related to both lobbying and campaign finance. The architecture relies on three primary subsystems interacting with the central **CAL-ACCESS DATABASE**:

### Three Primary Subsystems

#### 1. ELECTRONIC FILING SUBSYSTEM (EFS)
This subsystem accepts and validates electronic filings submitted by Campaign or Lobbying Filers (often via vendors).

#### 2. AGENCY MANAGEMENT SUBSYSTEM (AMS)
This system supports the business processes of the Secretary of State's Political Reform Division (PRD). Data management tables often contain the `AMS` prefix, such as:
- `AMS_PROCESSING_STATUS` - For tracking user-initiated jobs
- `AMS_SYSTEM_PARMS` - For system configuration

#### 3. DISCLOSURE SUBSYSTEM
This component discloses accepted filings to Internet users for public access.

### Physical Data Model

The physical data model documented in the source material is identified as **Model_1**, created on **February 21, 2002**.

---

## Core Filer and Filing Management

The database uses foundational tables to manage entities (filers) and documents (filings), which are critical for tracking lobbying activity:

### Core Tables

| Table Name | Description | Key Field |
|------------|-------------|-----------|
| **FILERS_CD** | The **parent table** from which all links and associations to a filer are derived | `FILER_ID` (unique identifier) |
| **FILINGS_CD** | The **parent table** from which all links and associations to a filing are derived | `FILING_ID` (unique identifier) |
| **FILER_FILINGS_CD** | A key index table that **links filers to their filings** (electronic, paper, key data entry (KDE), and legacy) | `FILER_ID` + `FILING_ID` |
| **NAMES_CD** | Contains the names of all entities in the system, often used for name searches where the entity has an identification number | `FILER_ID` |
| **ADDRESS_CD** | Holds all addresses for the system, forming the basis for address-based searches and display within the AMS | `FILER_ID` |
| **FILER_TO_FILER_TYPE_CD** | Links a filer to a set of characteristics (`FILER_TYPE`) and maintains a history of these characteristics over time | `FILER_ID` + `FILER_TYPE` |
| **FILER_ETHICS_CLASS_CD** | Specifically stores **lobbyist ethics training dates** (`ETHICS_DATE`) | `FILER_ID` + `ETHICS_DATE` |

### Data Flow Pattern

```
FILERS_CD (Master Registry)
    └── FILER_ID
         │
         ├──→ FILER_FILINGS_CD (Links filer to filings)
         │         └── FILING_ID
         │
         ├──→ NAMES_CD (Name variations)
         ├──→ ADDRESS_CD (Address information)
         ├──→ FILER_TO_FILER_TYPE_CD (Characteristics)
         └──→ FILER_ETHICS_CLASS_CD (Ethics training)

FILINGS_CD (Document Registry)
    └── FILING_ID
         │
         ├──→ CVR_REGISTRATION_CD (Registration cover pages)
         └──→ CVR_LOBBY_DISCLOSURE_CD (Disclosure cover pages)
```

---

## Lobbying Registration Data Structures (Forms 600 Series)

Lobbying registration and associated amendments are handled primarily by the Cover Page Registration tables and specific schedule tables.

### A. Registration Cover Pages (CVR_REGISTRATION & CVR2_REGISTRATION)

The core cover page information for lobbying registration forms is stored in **CVR_REGISTRATION_CD**. This covers Forms **601, 602, 603, 604, 606, and 607**.

#### Key Lobbying Fields in Cover Record

| Field Name | Description | Applies To |
|------------|-------------|------------|
| **ENTITY_CD** | Entity code of the subject of the filing | All registration forms |
| | Legal values: **LBY, LEM, LCO, and FRM** | |
| **EFF_DATE** | Effective date of authorization or termination | All registration forms |
| **LOBBY_INT** | Description of Part III Lobbying Interests | Form 603 |
| **IND_CLASS** / **BUS_CLASS** | Classification values for industry or business-related entities | Applicable forms |
| **COMPLET_DT** | Ethics orientation course completion date | Form 604 |

#### Entity Code Definitions

- **LBY** = Lobbyist (individual)
- **LEM** = Lobbyist Employer (the entity that hires/pays for lobbying)
- **LCO** = Lobbying Coalition
- **FRM** = Lobbying Firm (the contracted lobbying company)

#### CVR2_REGISTRATION

The **CVR2_REGISTRATION_CD** table holds additional names layout data for the same registration forms (601, F602, F603, F604, F606, and F607).

### B. Registration Amendment and Employer Schedules

| Table Name | Associated Form(s) | Function / Purpose |
|------------|-------------------|-------------------|
| **LEMP_CD** | Form **601** filings (Parts 2A and 2B) | Stores data for **Lobbyist Employers/Subcontracted Clients**. Includes fields for client address, contract period (`CON_PERIOD`), and lobbying interests description (`DESCRIP`). |
| **LOBBY_AMENDMENTS_CD** | Form **605 Part I** | Stores lobbyist registration amendment information. Contains flags and effective dates for adding (`ADD_L_CB`, `ADD_LE_CB`, `ADD_LF_CB`) or deleting (`DEL_L_CB`, `DEL_LE_CB`, `DEL_LF_CB`) lobbyists, employers, or lobbying firms. |

---

## Lobbying Disclosure Data Structures (Forms 615, 625, 635, 645)

Lobbying disclosure reports (filed quarterly) use a separate set of cover pages and detailed schedules to itemize activities, expenses, and contributions.

### A. Disclosure Cover Pages and Amendments

#### CVR_LOBBY_DISCLOSURE

The **CVR_LOBBY_DISCLOSURE_CD** table stores cover page information for lobbying disclosure forms **615, 625, 635, and 645**.

Key data elements include:
- `FIRM_NAME`, `FIRM_ADR1` - Firm/employer name and address
- `LBY_ACTVTY` - Description of lobbying activity (applies to Forms 635/645)

#### CVR2_LOBBY_DISCLOSURE

The **CVR2_LOBBY_DISCLOSURE_CD** table stores additional names data related to the disclosure forms (615, 625, 635, and 645), specifically listing entities such as:
- Partners (`ENTITY_CD` = PTN)
- Owners (`ENTITY_CD` = OWN)
- Officers (`ENTITY_CD` = OFF)
- Employees (`ENTITY_CD` = EMP)

#### F690P2

Amendments to existing disclosure filings are logged in the **F690P2_CD** table, which holds Form 690 amendment information.

### B. Disclosure Schedules

Detailed lobbying activity is recorded across several schedules, typically denoted by "L" tables:

| Table Name | Associated Form(s) | Function / Purpose |
|------------|-------------------|-------------------|
| **LEXP_CD** | F615 P1, F625 P3A, F635 P3C, F645 P2A | Stores **Lobbying Activity Expenditure Schedule information**. Includes payee details, expenditure amount, date, and description (`EXPN_DSCR`). It also captures information about the reportable person benefiting (`BENE_NAME`, `BENE_POSIT`). |
| **LPAY_CD** | F625 P2, F635 P3B | Tracks **Payments made/received to/from Lobbying Firms**. This includes fees and retainers (`FEES_AMT`), reimbursements (`REIMB_AMT`), and advance payments (`ADVAN_AMT`). <br><br>**CRITICAL TABLE** for tracking city/county lobbying payments. |
| **LOTH_CD** | F625 P3B | Records **Payments to other lobbying firms**. |
| **LCCM_CD** | F615 P2, F625 P4B, F635 P4B, F645 P3B | Stores detailed **Lobbying Campaign Contributions**. Includes contribution date, amount, contributor names, and recipient committee details. |
| **LATT_CD** | S630, S635, S640 | Holds **Lobbyist disclosure attachment schedules for payments**. |

### LPAY_CD Structure (Critical for City/County Tracking)

```
LPAY_CD - Lobbying Payments
├── FILING_ID          - Links to disclosure filing
├── AMEND_ID           - Amendment number (0 = original)
├── LINE_ITEM          - Line number on schedule
│
├── EMPLR_ID           - Employer filer ID
├── EMPLR_NAML         - Employer name (e.g., "City of Oakland")
├── EMPLR_NAMF         - Employer first name (if individual)
│
├── PAYEE_NAML         - Payee name (e.g., lobbying firm)
├── PAYEE_NAMF         - Payee first name
├── PAYEE_ADR1/2       - Payee address
│
├── FEES_AMT           - Fees paid
├── REIMB_AMT          - Reimbursements
├── ADVAN_AMT          - Advance payments
├── PER_TOTAL          - Total for this period
└── CUM_TOTAL          - Cumulative total
```

**Understanding LPAY_CD**:
- **EMPLR_NAML** = The city/county that **PAID** for lobbying
- **PAYEE_NAML** = The lobbying firm that **WAS PAID**
- **PER_TOTAL** = Amount for this reporting period
- **CUM_TOTAL** = Running cumulative total

---

## Lobbyist Relationship and Historical Data

The system uses specific structures to track relationships and historical financial activity, particularly for employers and firms, often utilizing multiple tables for disclosure and analytical purposes.

### Lobbyist Contribution Disclosure

The primary lobbyist contribution disclosure data is housed in **LOBBYIST_CONTRIBUTIONS3_CD**.

Temporary tables, `LOBBYIST_CONTRIBUTIONS1_CD` and `LOBBYIST_CONTRIBUTIONS2_CD`, are used in the process of generating this main disclosure table.

### Lobbying Change Log

**LOBBYING_CHG_LOG_CD** holds log data related to lobbyist changes for web display (tracking actions like ADD, DELETE, or CHANGE for attributes like NAME, ADDRESS, or LINK).

### Materialized Views (MV)

The database uses materialized view tables (`MVIEW`) for snapshots of aggregated data, such as:

| Materialized View | Purpose |
|------------------|---------|
| **MVIEW_LOBBYIST_CONTRIB** | Snapshot table for lobbyist contributions, including filing IDs, session IDs, and amounts |
| **MV_SMRY_F635** | Snapshot table specific to Form 635 summary data |

### Historical and Summary Tables

A substantial portion of the schema is dedicated to tracking quarterly and session totals for lobbying employers and firms:

#### Employer Tracking Tables

The tables **LOBBYIST_EMPLOYER1_CD**, **LOBBYIST_EMPLOYER2_CD**, and **LOBBYIST_EMPLOYER3_CD** all track:
- Quarterly totals
- Yearly totals (`YR_1_YTD_AMT`, `YR_2_YTD_AMT`)
- Session totals (`SESSION_TOTAL_AMT`)
- Associated interest codes

#### Firm Tracking Tables

Similarly, **LOBBYIST_FIRM1_CD**, **LOBBYIST_FIRM2_CD**, and **LOBBYIST_FIRM3_CD** track aggregated quarterly and session totals for lobbying firms.

#### History Tables

History tables like `LOBBYIST_EMPLOYER_HISTORY_CD` and `LOBBYIST_FIRM_HISTORY_CD` track similar financial totals over time.

### Note on Redundancy

The documentation explicitly notes that the relationship and specific functions of the multiple numerically suffixed tables (e.g., LOBBYIST_EMPLOYER1, LOBBYIST_EMPLOYER2) require further description, indicating complexity or lack of detailed functional documentation for these specific relational views or summary tables.

> **Original Note**: "Matt needs to describe the relationship between the multiple tables"

**Implication**: The exact purpose and relationship of numbered suffix tables (1, 2, 3) is not fully documented. Use with caution and validate against schedule table data.

---

## Data Model Technical Properties

The database uses a standardized approach for defining columns and indexes.

### A. Column Properties

Each column definition includes properties such as:

| Property | Description |
|----------|-------------|
| **Name and Code** | For readability and reference |
| **Data type** | Such as `VARCHAR2`, `NUMBER`, `DATE`, or `CLOB` |
| **Primary key (P)** | Uniquely identifies a row |
| **Mandatory (M)** | Indicates if the column must be assigned a value |

### B. Index Types

The system employs various index types to enforce data integrity and optimize performance:

| Index Type | Description |
|------------|-------------|
| **Primary key** | Uniquely identifies a row |
| **Foreign key (F)** | Depends on and migrates from a primary key in another table |
| **Alternate key (A)** | Also uniquely identifies a row but is not the primary key |
| **Unique (U)** | Ensures no two rows can share the same index value (all primary keys must be unique) |
| **Cluster (C)** | Index where the physical and logical (indexed) order are the same |

---

## Analogy for Understanding the Data Architecture

Understanding the Cal-ACCESS database for lobbying is like analyzing a vast **legislative archive**, but instead of physical boxes, the data is structured into digital containers:

- The **FILERS_CD** table acts as the master register of all lobbyists and firms (the *people* involved)
- The **FILINGS_CD** table is the log of every submitted report (the *documents*)
- The various **CVR_LOBBY_DISCLOSURE_CD** and **CVR_REGISTRATION_CD** tables act as the standardized *filing cabinets* for the cover pages, instantly telling you the type of form and the filer's identity
- Finally, the "L" schedules (**LEXP_CD**, **LPAY_CD**, **LCCM_CD**) are the detailed, itemized *receipts and ledgers*, proving the specific dollar amounts and activities reported, segmented specifically by the legal form requirements (e.g., Form 625 Part 3A, Form 645 Part 3B)

---

## Summary: Database Architecture Overview

### Core Design Pattern

```
Master Registry (FILERS) ← All entities
    ↓
Junction Table (FILER_FILINGS) ← Links entities to documents
    ↓
Document Registry (FILINGS) ← All submitted forms
    ↓
Cover Pages (CVR_*) ← Form metadata
    ↓
Schedules (L*) ← Detailed line items
```

### Key Tables by Purpose

| Purpose | Tables |
|---------|--------|
| **Entity Management** | FILERS_CD, NAMES_CD, ADDRESS_CD, FILER_TO_FILER_TYPE_CD |
| **Filing Management** | FILINGS_CD, FILER_FILINGS_CD |
| **Registration** | CVR_REGISTRATION_CD, CVR2_REGISTRATION_CD, LEMP_CD, LOBBY_AMENDMENTS_CD |
| **Disclosure** | CVR_LOBBY_DISCLOSURE_CD, CVR2_LOBBY_DISCLOSURE_CD, F690P2_CD |
| **Payments** | LPAY_CD (critical), LOTH_CD |
| **Expenditures** | LEXP_CD |
| **Contributions** | LCCM_CD, LOBBYIST_CONTRIBUTIONS1/2/3_CD |
| **Attachments** | LATT_CD |
| **Historical** | LOBBYIST_EMPLOYER1/2/3_CD, LOBBYIST_FIRM1/2/3_CD, *_HISTORY_CD tables |
| **Aggregated** | MVIEW_LOBBYIST_CONTRIB, MV_SMRY_F635 |
| **Audit** | LOBBYING_CHG_LOG_CD |

### Form to Table Mapping Quick Reference

| Form Type | Form Numbers | Cover Table | Schedule Tables |
|-----------|-------------|-------------|-----------------|
| **Registration** | 601-607 | CVR_REGISTRATION_CD | LEMP_CD, LOBBY_AMENDMENTS_CD |
| **Disclosure** | 615, 625, 635, 645 | CVR_LOBBY_DISCLOSURE_CD | LEXP_CD, LPAY_CD, LOTH_CD, LCCM_CD, LATT_CD |
| **Amendment** | 605, 690 | - | LOBBY_AMENDMENTS_CD, F690P2_CD |

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Source**: Cal-ACCESS Physical Data Model (Model_1, February 21, 2002)
**Maintained By**: Ca-Lobby Project Team
