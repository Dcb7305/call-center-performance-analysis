# Requirements: Call Center Performance Analysis

**Owner:** Christopher Barber
**Stakeholders:** Call center leadership (requesters and decision-makers)
**Status:** Delivered (Nov 2026)

This document records what leadership asked for, how each requirement was defined, and how the work was checked before anyone relied on it. It was written up front and updated as decisions were made.

---

## 1. Business problem

Callers are hanging up before they reach an agent. Leadership needs to decide whether to fix this by **hiring more agents** or by **coaching current agents to shorten handle time**. Both cost money, so they want the data to point the way first.

## 2. Business questions

| # | Question | Decision it supports |
|---|----------|----------------------|
| Q1 | Is our abandon rate higher than the industry standard? | Whether action is needed at all |
| Q2 | If it is, is the main driver **Service Level** (not enough capacity) or **Average Handle Time** (calls taking too long)? | Hire agents vs. coach on handle time |
| Q3 | At what daily call volume does performance start to break down? | How much capacity to add, and when |

## 3. Scope

**In scope**
- 1,251 consecutive days of daily call center data
- Abandon rate, answer rate, service level, and time-based metrics
- Trends over time and the relationship between call volume and performance

**Out of scope**
- Individual agent performance (the data is daily totals, not per agent)
- Customer satisfaction and call reasons (not in the dataset)
- Staffing cost modeling (a follow-up once leadership picks a direction)

## 4. Data source

| Item | Detail |
|------|--------|
| Source | *Call Center Data* (Kaggle), `Call Center Data.csv` |
| Grain | One row per day, 1,251 rows |
| Storage | Google BigQuery, project `call-center-analysis-cb`, table `Raw Data` |
| Fields (9) | ID, incoming calls, answered calls, abandoned calls, answer rate, average answer speed, average talk duration, average waiting time, service level |

## 5. Metric definitions

Everyone has to agree on the definitions before the numbers mean anything.

| Metric | Definition | Notes |
|--------|------------|-------|
| Abandon rate | Abandoned calls ÷ incoming calls | Primary KPI for Q1 |
| Answer rate | Answered calls ÷ incoming calls | Stored as a decimal (0.553 = 55.3%) and shown as a percentage |
| Service level | % of calls answered within 20 seconds | Overall figure is **weighted by answered calls**; compared against the common 80/20 industry target |
| Handle time (proxy) | Average talk duration | **Assumption:** the dataset has no after-call work time, so talk duration stands in for AHT |
| Wait time | Average waiting time per call | Converted from TIME to seconds |
| Monthly figures | Days grouped into 30-day periods | Answer and abandon rates are **weighted by incoming calls**, and service level by answered calls, so busy days count more than quiet days |

## 6. Functional requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Profile the raw data for types, duplicates, missing values, value ranges, and logic errors before cleaning | Must |
| FR-2 | Produce a clean table with consistent column names (snake_case) and time fields converted to seconds | Must |
| FR-3 | Prove the clean table matches the source (see acceptance criteria) | Must |
| FR-4 | Report overall abandon rate and compare it with an industry benchmark | Must |
| FR-5 | Show abandon rate and service level trends over time | Must |
| FR-6 | Show how call volume relates to service level and abandon rate | Must |
| FR-7 | Identify the call volume level where performance drops off | Should |
| FR-8 | Give leadership a short written recommendation with supporting visuals | Must |
| FR-9 | Publish an interactive dashboard that stakeholders can explore on their own | Should |

## 7. Data quality and acceptance criteria

The data must pass every check below before it's used in any report.

| Check | Pass condition | Result |
|-------|----------------|--------|
| Row count | Raw rows = clean rows (or every dropped row is explained) | ✅ 1,251 = 1,251 |
| Duplicates | 0 duplicate IDs | ✅ 0 |
| Missing values | 0 nulls in all 9 columns | ✅ 0 |
| Call math | Answered + abandoned = incoming on every row | ✅ 0 mismatches |
| Impossible values | No days with more answered calls than incoming | ✅ 0 |
| Rate integrity | Answer rate = answered ÷ incoming | ✅ 0 mismatches |
| Totals | Call totals match between raw and clean tables | ✅ Match |
| Time conversion | Spot check of converted seconds against the original TIME values | ✅ Pass |

**Outliers:** Days with very high volume (clustered around IDs 839–884) were investigated. The totals reconcile, so they were **kept as a real demand spike** rather than removed. These days turned out to be central to the findings.

**Safety net:** The cleaning script still filters missing IDs and impossible call counts, even though this dataset passed every check, so the pipeline stays safe if new data is loaded.

## 8. Deliverables

| Deliverable | Tool | Audience |
|-------------|------|----------|
| Explore / clean / validate pipeline (`sql/01_explore.sql`, `sql/02_clean.sql`, `sql/03_validate.sql`) | SQL, BigQuery | Data team |
| Performance dashboard | Power BI | Leadership |
| Volume trend analysis | Python | Data team |
| Interactive KPI dashboard | Tableau Public | Leadership, self-serve |
| Leadership report (1–2 pages) | Written summary + visuals | Leadership |
| README and this requirements doc | GitHub | Everyone |

## 9. Decisions log

| Decision | Why |
|----------|-----|
| Kept the high-volume days | Totals reconciled, so they reflect real demand, not bad data |
| Used talk duration as the handle time proxy | No after-call work field in the data; noted as an assumption |
| Grouped days into 30-day periods | Daily data was too noisy to show a trend |
| Weighted rates by call volume | Prevents a quiet day from counting the same as a 1,500-call day |
| Weighted service level by answered calls (66.8%) | Service level measures how fast answered calls were picked up, so answered calls are the right base |
| Kept validation filters in the cleaning script | Protects future loads, even though no rows failed this time |

## 10. Outcome

- **Q1:** Yes. Across about 248K calls, the abandon rate was **10.9%**, and only **66.8%** of calls were answered within 20 seconds, well below the common 80/20 service level target.
- **Q2:** The main driver was **capacity, not handle time**. Talk duration stayed fairly steady (about 1–5 minutes), while average waiting time reached as high as 25 min 51 sec. During the biggest demand spike (days 839–884), service level fell to about 34% and answer rates dropped to about 55–60%.
- **Q3:** Performance holds below about **300 incoming calls per day** and drops sharply above it. Monthly, service level falls sharply once volume passes about 8K calls.
- **Recommendation:** Leadership should run a staffing review focused on days above about 300 calls. Service level still ranges from about 53% to 88% at normal volume, so handle time coaching is worth a second look once capacity is addressed.

## 11. Open items and future work

- Add per-agent data to separate team-wide issues from individual coaching needs
- Add after-call work time to measure true AHT
- Build a staffing cost model once leadership chooses a direction