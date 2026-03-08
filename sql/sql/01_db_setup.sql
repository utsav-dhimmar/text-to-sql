-- ============================================================
-- STEP 1: DATABASE SETUP
-- Run this file first in your PostgreSQL database
-- Command: psql -U your_user -d your_database -f step1_db_setup.sql
-- ============================================================





-- ── 2. Drop existing tables (clean start) ───────────────────
DROP TABLE IF EXISTS quarterly_results;
DROP TABLE IF EXISTS exchange_listings;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS industries;
DROP TABLE IF EXISTS sectors;


-- ── 3. Create tables ────────────────────────────────────────

CREATE TABLE sectors (
    sector_id       SERIAL PRIMARY KEY,
    sector_name     VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE industries (
    industry_id       SERIAL PRIMARY KEY,
    industry_name     VARCHAR(150) NOT NULL,
    sector_id         INT NOT NULL REFERENCES sectors(sector_id)
);

CREATE TABLE companies (
    company_id      SERIAL PRIMARY KEY,
    company_name    VARCHAR(200) NOT NULL,
    industry_id     INT NOT NULL REFERENCES industries(industry_id)
);

CREATE TABLE exchange_listings (
    listing_id  SERIAL PRIMARY KEY,
    company_id  INT NOT NULL REFERENCES companies(company_id),
    exchange    VARCHAR(10) NOT NULL,
    code        VARCHAR(20) NOT NULL,
    UNIQUE (exchange, code)
);

CREATE TABLE quarterly_results (
    result_id           SERIAL PRIMARY KEY,
    company_id          INT NOT NULL REFERENCES companies(company_id),
    quarter             VARCHAR(20) NOT NULL,
    period_end_date     DATE NOT NULL,
    revenue             NUMERIC(15,2),
    operating_expenses  NUMERIC(15,2),
    operating_profit    NUMERIC(15,2),
    depreciation        NUMERIC(15,2),
    interest            NUMERIC(15,2),
    profit_before_tax   NUMERIC(15,2),
    tax                 NUMERIC(15,2),
    net_profit          NUMERIC(15,2),
    eps                 NUMERIC(10,2),
    UNIQUE (company_id, quarter)
);


-- ── 4. Indexes for fast querying ─────────────────────────────
CREATE INDEX idx_industries_sector   ON industries(sector_id);
CREATE INDEX idx_companies_industry  ON companies(industry_id);
CREATE INDEX idx_listings_company    ON exchange_listings(company_id);
CREATE INDEX idx_results_company     ON quarterly_results(company_id);
CREATE INDEX idx_results_quarter     ON quarterly_results(quarter);
CREATE INDEX idx_results_date        ON quarterly_results(period_end_date);



-- ── 5. View for AG2/LLM queries ──────────────────────────────
CREATE VIEW company_financials AS
SELECT
    qr.result_id,
    qr.quarter,
    qr.period_end_date,
    c.company_id,
    c.company_name,
    i.industry_name,
    s.sector_name,
    el_nse.code                                                   AS nse_code,
    el_bse.code                                                   AS bse_code,
    qr.revenue,
    qr.operating_expenses,
    qr.operating_profit,
    ROUND(qr.operating_profit / NULLIF(qr.revenue,0) * 100, 2)   AS operating_profit_margin,
    qr.depreciation,
    qr.interest,
    qr.profit_before_tax,
    qr.tax,
    qr.net_profit,
    qr.eps,
    SUM(qr.net_profit) OVER (PARTITION BY qr.company_id)         AS profit_ttm,
    ROUND(SUM(qr.eps)  OVER (PARTITION BY qr.company_id), 2)     AS eps_ttm
FROM quarterly_results qr
JOIN companies          c       ON c.company_id   = qr.company_id
JOIN industries         i       ON i.industry_id  = c.industry_id
JOIN sectors            s       ON s.sector_id    = i.sector_id
LEFT JOIN exchange_listings el_nse ON el_nse.company_id = c.company_id AND el_nse.exchange = 'NSE'
LEFT JOIN exchange_listings el_bse ON el_bse.company_id = c.company_id AND el_bse.exchange = 'BSE';


-- ── Done ─────────────────────────────────────────────────────
-- Next step: run step2_insert_data.sql to load your data