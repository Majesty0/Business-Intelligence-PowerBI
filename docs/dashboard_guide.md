# Power BI Dashboard Guide

This guide describes the five interactive dashboards included in this project
and explains how to build them in Power BI Desktop using the processed data files.

---

## Prerequisites

- **Power BI Desktop** (free) – download from
  [https://powerbi.microsoft.com/desktop](https://powerbi.microsoft.com/desktop)
- Processed data files in `data/processed/` (run the scripts first – see
  [README.md](../README.md))

---

## Connecting to Data

1. Open Power BI Desktop and select **Get Data → Text/CSV**.
2. Load the following files from `data/processed/`:
   - `sales_clean.csv` (transactions)
   - `customers_clean.csv` (customer profiles)
   - `products_clean.csv` (product catalogue)
3. For the star-schema model, load all CSVs from `data/processed/model/`
   instead, and create relationships in the **Model** view (see
   [data_model_guide.md](data_model_guide.md)).

---

## Dashboard 1 – Executive Sales Overview

**Purpose:** High-level snapshot of business performance at a glance.

### Visuals to Create

| Visual | Type | Fields |
|--------|------|--------|
| Total Revenue | Card | `Sales` (Sum) |
| Total Profit | Card | `Profit` (Sum) |
| Profit Margin % | Card | `Profit / Sales * 100` (measure) |
| Total Orders | Card | `OrderID` (Count Distinct) |
| Revenue by Month | Line Chart | `OrderDate` (Month) → `Sales` (Sum) |
| Revenue by Category | Bar Chart | `Category` → `Sales` (Sum) |
| Revenue by Region | Map | `Region` → `Sales` (Sum, bubble size) |
| Top 10 Products | Bar Chart | `Product` → `Sales` (Top 10 filter) |

### Key DAX Measures

```dax
Total Revenue = SUM(sales_clean[Sales])
Total Profit  = SUM(sales_clean[Profit])
Profit Margin % = DIVIDE([Total Profit], [Total Revenue]) * 100
Order Count = DISTINCTCOUNT(sales_clean[OrderID])
Avg Order Value = DIVIDE([Total Revenue], [Order Count])
```

### Slicers

- `OrderDate` (date range)
- `Region`
- `Category`

---

## Dashboard 2 – Sales Trend Analysis

**Purpose:** Identify growth patterns, seasonality, and month-over-month trends.

### Visuals to Create

| Visual | Type | Fields |
|--------|------|--------|
| Monthly Revenue Trend | Line Chart | `OrderDate` (Month) → `Sales` |
| Quarterly Revenue | Clustered Column | `OrderQuarter` → `Sales` |
| YoY Revenue Comparison | Line Chart | `OrderDate` (Month) → `Sales` with Year legend |
| MoM Growth % | Line Chart | `OrderDate` (Month) → MoM Growth measure |
| Revenue vs. Profit Trend | Combo Chart | `OrderDate` (Month) → `Sales` (bars) + `Profit` (line) |

### Key DAX Measures

> **Note:** The `DATEADD`, `DATESYTD`, and other time-intelligence functions
> below require a properly configured date dimension table. Before using these
> measures, complete the star-schema model setup described in
> [data_model_guide.md](data_model_guide.md) and mark `dim_date` as a
> **Date Table** in Power BI (**Table tools → Mark as date table**, choose
> `FullDate`). If you are loading `sales_clean.csv` directly without a star
> schema, replace `dim_date[FullDate]` with `sales_clean[OrderDate]` in the
> measures below.

```dax
MoM Revenue Growth % =
VAR CurrentMonth  = [Total Revenue]
VAR PreviousMonth = CALCULATE([Total Revenue], DATEADD(dim_date[FullDate], -1, MONTH))
RETURN DIVIDE(CurrentMonth - PreviousMonth, PreviousMonth) * 100

YTD Revenue =
CALCULATE([Total Revenue], DATESYTD(dim_date[FullDate]))

Rolling 3-Month Avg =
AVERAGEX(
    DATESINPERIOD(dim_date[FullDate], LASTDATE(dim_date[FullDate]), -3, MONTH),
    [Total Revenue]
)
```

---

## Dashboard 3 – Customer Intelligence

**Purpose:** Understand who your customers are and segment them for targeted actions.

### Visuals to Create

| Visual | Type | Fields |
|--------|------|--------|
| Revenue by Segment | Donut Chart | `Segment` → `Sales` |
| Revenue by Loyalty Tier | Bar Chart | `LoyaltyTier` → `Sales` |
| Customer Count by Region | Filled Map | `Region` → Customer Count |
| RFM Segment Distribution | Bar Chart | `RFM_Segment` → Customer Count |
| Top 10 Customers by Revenue | Bar Chart | `CustomerName` → `Sales` (Top 10) |
| Avg Revenue per Customer | Card | Avg Revenue per Customer measure |

### Key DAX Measures

```dax
Customer Count = DISTINCTCOUNT(sales_clean[CustomerID])
Avg Revenue per Customer = DIVIDE([Total Revenue], [Customer Count])
New Customers (This Month) =
    CALCULATE([Customer Count],
        FILTER(customers_clean,
            MONTH(customers_clean[JoinDate]) = MONTH(TODAY()) &&
            YEAR(customers_clean[JoinDate])  = YEAR(TODAY())))
```

---

## Dashboard 4 – Product & Category Performance

**Purpose:** Determine which products and categories drive the most value.

### Visuals to Create

| Visual | Type | Fields |
|--------|------|--------|
| Revenue by Category | Treemap | `Category` / `SubCategory` → `Sales` |
| Profit Margin by SubCategory | Bar Chart | `SubCategory` → Profit Margin % |
| Top 10 Products by Revenue | Horizontal Bar | `Product` → `Sales` |
| Units Sold by Category | Column Chart | `Category` → `Quantity` |
| Discount Impact on Profit | Scatter | `Discount` (X) → `Profit` (Y) → bubble = `Sales` |
| Stock Level vs. Sales | Bar Chart | `ProductName` → `StockQuantity` + `Sales` (combo) |

### Key DAX Measures

```dax
Units Sold = SUM(sales_clean[Quantity])
Gross Margin % = AVERAGE(products_clean[GrossMarginPct])
Discount Rate Avg = AVERAGE(sales_clean[Discount])
Revenue per Unit = DIVIDE([Total Revenue], [Units Sold])
```

---

## Dashboard 5 – Operations & Shipping

**Purpose:** Monitor fulfilment efficiency and shipping performance.

### Visuals to Create

| Visual | Type | Fields |
|--------|------|--------|
| Avg Days to Ship | Card | `DaysToShip` (Average) |
| Orders by Ship Mode | Donut Chart | `ShipMode` → Count |
| Avg Days to Ship by Mode | Bar Chart | `ShipMode` → `DaysToShip` (Avg) |
| Orders Over Time by Ship Mode | Stacked Area | `OrderDate` (Month) → `OrderID` (Count), legend = `ShipMode` |
| Discount Impact by Ship Mode | Clustered Bar | `ShipMode` → `Discount` (Avg) |

### Key DAX Measures

```dax
Avg Days to Ship = AVERAGE(sales_clean[DaysToShip])
On-Time Rate (Same Day) =
    DIVIDE(
        CALCULATE([Order Count], sales_clean[ShipMode] = "Same Day"),
        [Order Count]
    ) * 100
```

---

## Applying Themes & Formatting

1. In Power BI Desktop, go to **View → Themes → Browse for themes**.
2. Apply a consistent colour palette for all visuals.
3. Set **canvas background** (Insert → Image or canvas settings) to a subtle
   brand colour or white for professional reports.
4. Use **bookmarks** (View → Bookmarks) to create navigation buttons between
   dashboards.
5. Add **drill-through** pages: right-click a product or customer visual and
   configure drill-through to a detail page.

---

## Publishing to Power BI Service

1. Save your `.pbix` file.
2. Click **Publish** in the Home ribbon and select a workspace.
3. Open Power BI Service and **pin** visuals to a new or existing dashboard.
4. Set up a **Scheduled Refresh** if using live data sources.
5. Share the dashboard with stakeholders via **Manage Access → Share**.
