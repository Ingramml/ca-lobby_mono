# California CAL-ACCESS Lobbying Database Tables

## Overview

The CAL-ACCESS system is California's campaign and lobbying information database maintained by the Secretary of State, where lobbyists and lobbying entities file detailed financial disclosures. The system contains 80 raw database tables, with a specific set dedicated to lobbying activities.

**Key Information:**
- System updates: Daily
- Format: Tab-delimited text files
- Access: Available for download from California Secretary of State website
- Data type: Campaign finance and lobbying activity disclosures

---

## Core Lobbying Tables

### 1. CVR_LOBBY_DISCLOSURE_CD
**Purpose:** Cover page of lobbying disclosure forms

**Fields:** 53 fields

**Key Information:**
- Contains filer identification numbers
- Reporting period dates (from/through)
- Amendment identification (0 = original, 1-999 = amendments)
- Lobbying activity descriptions
- Major donor information
- Signer information and dates

**Associated Forms:**
- Form 615: Lobbyist Report
- Form 625: Report of Lobbying Firm
- Form 635: Report of Lobbyist Employer or Lobbying Coalition
- Form 645: Report of Person Spending $5,000 or More

**Entity Codes:**
- CLI: Unknown
- FRM: Lobbying Firm
- IND: Person (spending > $5000)
- LBY: Lobbyist (an individual)
- LCO: Lobbying Coalition
- LEM: Lobbying Employer
- OTH: Other

---

### 2. CVR_REGISTRATION_CD
**Purpose:** Cover page of lobbying registration forms

**Fields:** 72 fields

**Key Information:**
- Individual or business entity information (name, address, ZIP)
- Ethics orientation class completion dates
- Lobbyist employer or firm names
- Industry and business classifications
- Date qualified as lobbyist/firm/employer
- Amendment tracking (000 = original, 001-999 = amendments)
- List of state agencies to be lobbied
- Authorization information

**Associated Forms:**
- Form 601: Lobbying Firm Registration Statement
- Form 603: Lobbyist Employer or Lobbying Coalition Registration Statement
- Form 604: Lobbyist Certification Statement
- Forms 606, 607: Additional registration forms

---

### 3. LEMP_CD
**Purpose:** Lobbyist employers and subcontracted clients

**Fields:** 25 fields

**Key Information:**
- Tracks relationships between employers and lobbyists
- Subcontracted client information
- Amendment identification numbers
- Links employers to their hired lobbying firms

---

### 4. LPAY_CD
**Purpose:** Payments made or received by lobbying firms

**Fields:** 27 fields

**Key Information:**
- Financial transaction records
- Payment amounts and dates
- Payor and payee information
- Amendment tracking
- Payment type classifications

**Associated Forms:**
- Form 625: Report of Lobbying Firm

---

### 5. LEXP_CD
**Purpose:** Lobbying expenditures and activity expenses

**Key Information:**
- Detailed expenditure records
- Activity-related costs
- Expense categories
- Vendor information

---

### 6. LOTH_CD
**Purpose:** Other lobbying-related payments

**Key Information:**
- Miscellaneous payments that don't fit standard categories
- Additional financial activities
- Special payment types

---

### 7. LCCM_CD
**Purpose:** Campaign contributions made by lobbying entities

**Key Information:**
- Contributions to campaigns by lobbyists and lobbying firms
- Recipient information
- Contribution amounts and dates
- Links lobbying activity to campaign finance

---

### 8. LATT_CD
**Purpose:** Attachments for lobbying payments

**Key Information:**
- Supporting documentation for payments
- Additional payment details
- Governmental agency reporting

**Associated Schedules:**
- Schedule 635C: Payments Received by Lobbying Coalitions
- Schedule 640: Governmental Agencies Reporting (Attachment to Form 635 or Form 645)

---

### 9. CVR2_LOBBY_DISCLOSURE_CD
**Purpose:** Secondary cover page for lobbying disclosures

**Key Information:**
- Additional disclosure information
- Supplementary filing data

---

### 10. CVR2_REGISTRATION_CD
**Purpose:** Secondary cover page for lobbying registrations

**Key Information:**
- Additional registration information
- Supplementary registration data

---

### 11. LOBBY_AMENDMENTS_CD
**Purpose:** Amendments to lobbyist registration forms

**Fields:** 43 fields

**Key Information:**
- Tracks all changes to registration forms
- Amendment number tracking (0 = original, 1-999 = amendments)
- Date of amendments
- Nature of changes made

---

### 12. LOBBYING_CHG_LOG_CD
**Purpose:** Change log for lobbying records

**Key Information:**
- Audit trail of database changes
- Historical record modifications
- System-level tracking

---

### 13. F690P2_CD
**Purpose:** Additional lobbying form data

**Key Information:**
- Supplementary form information
- Additional disclosure requirements

---

## Key Forms and Their Table Relationships

### Form 601: Lobbying Firm Registration Statement
**Filed by:** Lobbying firms or individual contract lobbyists
**Filing schedule:** Biennial (every 2 years)
**Deadline:** Within 10 days of qualifying; renewal due Nov 1 - Dec 31 of even-numbered years
**Populates:** 8 CAL-ACCESS files

### Form 603: Lobbyist Employer or Lobbying Coalition Registration Statement
**Filed by:** Lobbyist employers or lobbying coalitions
**Filing schedule:** Biennial (every 2 years)
**Deadline:** Within 10 days of qualifying; renewal due Nov 1 - Dec 31 of even-numbered years
**Populates:** 7 CAL-ACCESS files

### Form 604: Lobbyist Certification Statement
**Filed by:** Individual lobbyists
**Purpose:** Certification of ethics training completion
**Populates:** 5 CAL-ACCESS files

### Form 615: Lobbyist Report
**Filed by:** In-house lobbyists
**Filing schedule:** Quarterly
**Sections:** 2 sections
**Populates:** 8 CAL-ACCESS files
**Note:** Attached to Form 625 or 635 for paper filers; filed separately by electronic filers

### Form 625: Report of Lobbying Firm
**Filed by:** Lobbying firms (including individual contract lobbyists)
**Filing schedule:** Quarterly
**Sections:** 6 sections
**Populates:** 12 CAL-ACCESS files

### Form 635: Report of Lobbyist Employer or Report of Lobbying Coalition
**Filed by:** Lobbyist employers or lobbying coalitions
**Filing schedule:** Quarterly
**Sections:** 8 sections
**Populates:** 11 CAL-ACCESS files

### Form 645: Report of Person Spending $5,000 or More
**Filed by:** Individuals or entities spending $5,000+ on lobbying
**Purpose:** Disclosure for non-registered lobbying activity

---

## Common Supporting Tables

These tables support both lobbying and campaign finance data:

### FILERS_CD
- Master filer information database
- Contains all registered entities

### FILER_FILINGS_CD
- Index linking filers to their filings
- 17 fields
- Critical for navigation across tables

### FILINGS_CD
- Filing metadata
- Filing dates and status information

### FILER_ADDRESS_CD
- Address information for filers

### FILER_LINKS_CD
- Relationships between different filer entities

### FILER_TYPES_CD
- Classification of filer types

### NAMES_CD
- Name information for individuals and entities

### TEXT_MEMO_CD
- Additional text descriptions and memos
- Extended narratives for activities

### IMAGE_LINKS_CD
- Links to scanned document images

### LOOKUP_CODES_CD
- Reference table for coded values
- Definitions for abbreviations and codes used throughout system

---

## How Tables Connect

### Primary Key Relationships

1. **FILER_ID**
   - The primary identifier that links filers across all tables
   - Unique to each registered entity

2. **FILING_ID**
   - Links specific filings to their detail records
   - Connects cover pages to supporting schedules

3. **AMEND_ID**
   - Amendment identification number
   - 0 = original filing
   - 1-999 = amendments

4. **ENTITY_CD**
   - Classifies the type of filer
   - Enables filtering by entity type

### Table Connection Flow

```
FILERS_CD (Master Registry)
    ↓
FILER_FILINGS_CD (Filing Index)
    ↓
CVR_REGISTRATION_CD or CVR_LOBBY_DISCLOSURE_CD (Cover Pages)
    ↓
Detailed Transaction Tables:
    - LEMP_CD (Employers)
    - LPAY_CD (Payments)
    - LEXP_CD (Expenditures)
    - LCCM_CD (Campaign Contributions)
    - LOTH_CD (Other Payments)
    ↓
Supporting Information:
    - LATT_CD (Attachments)
    - TEXT_MEMO_CD (Additional Text)
```

### Registration to Disclosure Flow

1. **Registration Phase:**
   - Entity registers using Form 601, 603, or 604
   - Data stored in CVR_REGISTRATION_CD and CVR2_REGISTRATION_CD
   - Filer created in FILERS_CD

2. **Quarterly Disclosure Phase:**
   - Registered entities file quarterly reports (Form 615, 625, 635, or 645)
   - Cover information in CVR_LOBBY_DISCLOSURE_CD
   - Detailed transactions in LPAY_CD, LEXP_CD, LCCM_CD, LOTH_CD
   - Employment relationships in LEMP_CD

3. **Amendment Phase:**
   - Changes tracked in LOBBY_AMENDMENTS_CD
   - Amendment numbers increment (001, 002, etc.)

---

## Important Concepts

### Entity Types

- **Lobbying Firm (FRM):** Organization that employs lobbyists and is hired by clients
- **Lobbyist Employer (LEM):** Organization that hires lobbyists (either in-house or via firms)
- **Lobbying Coalition (LCO):** Group of 10+ entities pooling funds to hire lobbyists
- **Lobbyist (LBY):** Individual who lobbies officials
- **$5,000 Filer (IND):** Individual/entity spending $5,000+ but not hiring lobbyists

### Amendment System

- **000:** Original filing
- **001-999:** Sequential amendment numbers
- All amendments linked to original via FILING_ID and FILER_ID

### Reporting Requirements

**Registration:**
- Due within 10 days of qualifying
- Biennial renewal (every 2 years)
- Renewal period: November 1 - December 31 of even-numbered years

**Quarterly Disclosure:**
- Filed each calendar quarter
- Due approximately 30 days after quarter end
- Includes financial activities and lobbying efforts

---

## Data Access and Usage

### Accessing the Data

1. **CAL-ACCESS Website:** User-friendly web interface at cal-access.sos.ca.gov
2. **Raw Data Downloads:** Tab-delimited text files available from Secretary of State
3. **California Civic Data Coalition:** Processed and documented data with improved usability

### Data Format

- **File Format:** Tab-delimited text (.TSV)
- **Compression:** ZIP format
- **Update Frequency:** Daily
- **Extraction Tools:** PKZIP, WinZip, MacZip, or standard archive utilities

### Technical Considerations

- No official technical support provided by Secretary of State
- Documentation is fragmented and may be outdated
- California Civic Data Coalition provides more reliable documentation
- Data structure last comprehensively documented in 2002

### Data Quality Notes

- Information changes frequently
- Filers may submit amendments
- Some fields may be incomplete or inconsistent
- Always verify critical information with original filed documents

---

## Additional Resources

### Official Sources

- **California Secretary of State - Political Reform Division**
  - Website: sos.ca.gov/campaign-lobbying
  - Email: prd@sos.ca.gov
  - Phone: (916) 653-6814

- **Fair Political Practices Commission (FPPC)**
  - Provides guidance on lobbying rules and regulations
  - Website: fppc.ca.gov

### Community Resources

- **California Civic Data Coalition**
  - Website: calaccess.californiacivicdata.org
  - Provides improved documentation and data processing
  - Open-source tools for data analysis

- **California Lobby Search**
  - Website: calobbysearch.org
  - Simplified search interface for lobbying data
  - Bill tracking by company and lobbying firm

### Documentation

- CAL-ACCESS Tables, Columns and Indexes (2002)
- .CAL Format Layout documentation
- Map from .CAL Format to Database Table and Fields
- FPPC Lobbying Manual

---

## Legal Framework

### Political Reform Act of 1974

- Adopted as Proposition 9
- Requires disclosure of campaign and lobbying finances
- Administered by Secretary of State and FPPC
- Governs all lobbying registration and disclosure

### Key Requirements

- **Registration:** Lobbyists, firms, and employers must register
- **Quarterly Reports:** Financial disclosures required each quarter
- **Ethics Training:** Lobbyists must complete ethics courses
- **Gift Limits:** Strict limits on gifts to officials ($630 for 2025-2026)
- **Public Disclosure:** All information publicly available

---

## Notes

- This documentation is based on information available as of October 2025
- Table structures may change; always consult current official documentation
- Some table names use "_CD" suffix (appears to stand for "California Data")
- The system tracks both state-level lobbying and campaign finance
- Local lobbying (city/county) is not tracked in CAL-ACCESS

---

**Document Version:** 1.0  
**Last Updated:** October 24, 2025  
**Source:** California Secretary of State, California Civic Data Coalition
