# Business Intelligence – Power BI

An end-to-end Business Intelligence project using **Microsoft Power BI**, covering
data ingestion, cleaning, analysis, star-schema modelling, and interactive dashboard
creation.

---

## Project Goals

| Goal | What this repo provides |
|------|------------------------|
| **Build interactive dashboards** | Five dashboard blueprints with DAX measures and visual specs (see [`docs/dashboard_guide.md`](docs/dashboard_guide.md)) |
| **Clean & manipulate data** | Python cleaning pipeline (`scripts/data_cleaning.py`) – deduplication, type parsing, validation, derived features |
| **Analyse data** | Python analysis pipeline (`scripts/data_analysis.py`) – KPIs, trend analysis, RFM scoring, discount impact |
| **Create data models** | Star-schema builder (`scripts/data_model.py`) – fact + five dimension tables ready for Power BI relationships |
| **Visualise data trends** | Guided visual types, DAX time-intelligence measures, and formatting tips for every dashboard |

---

## Repository Structure

```
Business-Intelligence-PowerBI/
├── data/
│   └── raw/                     # Source CSV datasets
│       ├── sales_data.csv        # 100 order-line transactions (2023)
│       ├── customers.csv         # 25 customer profiles
│       └── products.csv          # 30 product records
├── scripts/
│   ├── data_cleaning.py          # Step 1 – Clean & validate raw data
│   ├── data_analysis.py          # Step 2 – EDA, KPIs, RFM analysis
│   └── data_model.py             # Step 3 – Build star-schema model tables
├── tests/
│   ├── test_data_cleaning.py     # Unit tests for cleaning functions
│   └── test_data_analysis.py     # Unit tests for analysis functions
├── docs/
│   ├── dashboard_guide.md        # Power BI dashboard build instructions
│   └── data_model_guide.md       # Star-schema reference & DAX measures
├── dashboards/                   # Place your .pbix files here
└── README.md
```

---

## Quick Start

### 1 – Prerequisites

```bash
pip install pandas numpy pytest
```

### 2 – Run the Data Pipeline

Run the three scripts in order:

```bash
# Clean and validate raw data → data/processed/
python scripts/data_cleaning.py

# Compute KPIs, trends, RFM analysis → data/processed/
python scripts/data_analysis.py

# Build star-schema tables → data/processed/model/
python scripts/data_model.py
```

### 3 – Run Tests

```bash
pytest tests/ -v
```

### 4 – Open in Power BI

1. Download **Power BI Desktop** (free): <https://powerbi.microsoft.com/desktop>
2. Load CSVs from `data/processed/` (or `data/processed/model/` for the
   star-schema model).
3. Follow the step-by-step instructions in [`docs/dashboard_guide.md`](docs/dashboard_guide.md).

---

## Datasets

### `data/raw/sales_data.csv`
100 order-line transactions covering January–October 2023.

| Column | Description |
|--------|-------------|
| OrderID | Unique order identifier |
| OrderDate / ShipDate | Transaction and fulfilment dates |
| CustomerID / CustomerName | Customer reference |
| Region / Country | Geographic location |
| Category / SubCategory / Product | Product hierarchy |
| Quantity / UnitPrice / Discount | Pricing details |
| Sales / Profit | Revenue and profit amounts |
| ShipMode | Delivery method |

### `data/raw/customers.csv`
25 customer profiles with segment, loyalty tier, and contact information.

### `data/raw/products.csv`
30 product records with cost, price, stock levels, and supplier details.

---

## Data Pipeline

```
data/raw/*.csv
      │
      ▼
scripts/data_cleaning.py   → data/processed/sales_clean.csv
                                             customers_clean.csv
                                             products_clean.csv
      │
      ▼
scripts/data_analysis.py   → data/processed/kpi_summary.csv
                                             monthly_sales_trend.csv
                                             quarterly_sales_trend.csv
                                             category_performance.csv
                                             top_products.csv
                                             regional_performance.csv
                                             customer_segment_analysis.csv
                                             rfm_analysis.csv
                                             shipping_performance.csv
                                             discount_impact.csv
      │
      ▼
scripts/data_model.py      → data/processed/model/fact_sales.csv
                                                   dim_date.csv
                                                   dim_customer.csv
                                                   dim_product.csv
                                                   dim_geography.csv
                                                   dim_shipmode.csv
```

---

## Dashboards

Five dashboards are documented in [`docs/dashboard_guide.md`](docs/dashboard_guide.md):

1. **Executive Sales Overview** – Revenue, profit, margins, top products, regional map
2. **Sales Trend Analysis** – Monthly/quarterly trends, MoM growth, YTD measures
3. **Customer Intelligence** – Segment breakdown, loyalty tiers, RFM segments
4. **Product & Category Performance** – Category treemap, discount-profit scatter, stock levels
5. **Operations & Shipping** – Ship-mode comparison, fulfilment time analysis

---

## Data Model (Star Schema)

See [`docs/data_model_guide.md`](docs/data_model_guide.md) for the full entity diagram,
column definitions, relationship setup steps, and recommended DAX measures.

```
dim_date ──┐
           │
dim_customer ──┤
               ├── fact_sales
dim_geography ─┤
               │
dim_shipmode ──┘
```

---

## Key Analyses Performed

| Analysis | Script | Output File |
|----------|--------|-------------|
| Data quality validation | `data_cleaning.py` | (console report) |
| KPI dashboard metrics | `data_analysis.py` | `kpi_summary.csv` |
| Monthly revenue trend | `data_analysis.py` | `monthly_sales_trend.csv` |
| Category profitability | `data_analysis.py` | `category_performance.csv` |
| RFM customer scoring | `data_analysis.py` | `rfm_analysis.csv` |
| Regional performance | `data_analysis.py` | `regional_performance.csv` |
| Discount impact | `data_analysis.py` | `discount_impact.csv` |
| Star-schema model | `data_model.py` | `model/` directory |
