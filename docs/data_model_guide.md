# Data Model Guide – Star Schema

This document explains the star-schema data model built by `scripts/data_model.py`
and how to configure relationships in Power BI Desktop.

---

## Schema Overview

```
                    ┌──────────────┐
                    │  dim_date    │
                    │  (DateKey)   │
                    └──────┬───────┘
                           │ OrderDateKey / ShipDateKey
         ┌─────────────────┼─────────────────────┐
         │                 │                     │
┌────────┴──────┐  ┌───────┴────────┐  ┌────────┴──────┐
│ dim_customer  │  │  fact_sales    │  │ dim_product   │
│ (CustomerID)  │──│ (OrderID)      │──│ (via Product) │
└───────────────┘  │  OrderDateKey  │  └───────────────┘
                   │  ShipDateKey   │
                   │  CustomerID    │
                   │  GeoKey        │
                   │  ShipModeKey   │
                   └───────┬────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
     ┌────────┴──────┐       ┌──────────┴──────┐
     │ dim_geography │       │ dim_shipmode    │
     │ (GeoKey)      │       │ (ShipModeKey)   │
     └───────────────┘       └─────────────────┘
```

---

## Tables

### `fact_sales` (Fact Table)

| Column | Type | Description |
|--------|------|-------------|
| OrderID | Text | Unique order identifier |
| OrderDateKey | Integer | FK → dim_date.DateKey |
| ShipDateKey | Integer | FK → dim_date.DateKey |
| CustomerID | Text | FK → dim_customer.CustomerID |
| GeoKey | Text | FK → dim_geography.GeoKey |
| ShipModeKey | Integer | FK → dim_shipmode.ShipModeKey |
| Category | Text | Product category |
| SubCategory | Text | Product sub-category |
| Product | Text | Product name |
| Quantity | Integer | Units ordered |
| UnitPrice | Decimal | List price per unit |
| Discount | Decimal | Discount rate (0–1) |
| Sales | Decimal | Net revenue |
| Profit | Decimal | Net profit |
| ProfitMargin | Decimal | Profit / Sales |
| DaysToShip | Integer | OrderDate → ShipDate |

### `dim_date`

| Column | Type | Description |
|--------|------|-------------|
| DateKey | Integer | YYYYMMDD surrogate key |
| FullDate | Date | Calendar date |
| Year | Integer | Calendar year |
| Quarter | Integer | 1–4 |
| QuarterName | Text | Q1–Q4 |
| Month | Integer | 1–12 |
| MonthName | Text | January–December |
| MonthShort | Text | Jan–Dec |
| Week | Integer | ISO week number |
| DayOfMonth | Integer | 1–31 |
| DayOfWeek | Integer | 1=Monday, 7=Sunday |
| DayName | Text | Monday–Sunday |
| IsWeekend | Boolean | True for Sat/Sun |
| YearMonth | Text | YYYY-MM |
| YearQuarter | Text | YYYY-Q# |

### `dim_customer`

| Column | Type | Description |
|--------|------|-------------|
| CustomerID | Text | Primary key |
| FullName | Text | Customer full name |
| Segment | Text | Consumer / Corporate / Home Office |
| City | Text | Customer city |
| State | Text | Customer state |
| Region | Text | East / West / Central / South |
| Country | Text | Country |
| LoyaltyTier | Text | Bronze / Silver / Gold / Platinum |
| CustomerSince | Date | Join date |
| TenureYears | Decimal | Years since joining |

### `dim_product`

| Column | Type | Description |
|--------|------|-------------|
| ProductID | Text | Primary key |
| ProductName | Text | Full product name |
| Category | Text | Main category |
| SubCategory | Text | Sub-category |
| Brand | Text | Manufacturer brand |
| UnitCost | Decimal | Cost to the business |
| UnitPrice | Decimal | Selling price |
| GrossMarginPct | Decimal | (Price − Cost) / Price × 100 |
| StockQuantity | Integer | Units in stock |
| ReorderLevel | Integer | Minimum stock trigger |
| Supplier | Text | Supplier name |
| Discontinued | Text | Yes / No |

### `dim_geography`

| Column | Type | Description |
|--------|------|-------------|
| GeoKey | Text | Surrogate key (e.g. EAS_USA) |
| Region | Text | Sales region |
| Country | Text | Country |

### `dim_shipmode`

| Column | Type | Description |
|--------|------|-------------|
| ShipModeKey | Integer | Surrogate key |
| ShipMode | Text | Shipping method name |
| MinDays | Integer | Expected minimum transit days |
| MaxDays | Integer | Expected maximum transit days |

---

## Setting Up Relationships in Power BI

1. Open `Model` view in Power BI Desktop.
2. Create the following relationships (all **many-to-one**, single-direction):

| From (Many) | To (One) | Cardinality |
|-------------|----------|-------------|
| fact_sales[OrderDateKey] | dim_date[DateKey] | Many → One |
| fact_sales[ShipDateKey] | dim_date[DateKey] | Many → One |
| fact_sales[CustomerID] | dim_customer[CustomerID] | Many → One |
| fact_sales[GeoKey] | dim_geography[GeoKey] | Many → One |
| fact_sales[ShipModeKey] | dim_shipmode[ShipModeKey] | Many → One |

> **Note:** Power BI supports two relationships between fact_sales and dim_date
> (OrderDateKey and ShipDateKey). Mark `OrderDateKey → dim_date[DateKey]` as
> **Active** and `ShipDateKey → dim_date[DateKey]` as **Inactive**. Use
> `USERELATIONSHIP()` in DAX when filtering by ship date.

3. In **Properties** for each relationship, set:
   - Cross-filter direction: **Single** (fact → dimension)
   - Cardinality: **Many to one (*:1)**

---

## Recommended Measures

Create these in a dedicated `_Measures` table in Power BI:

```dax
-- Revenue & Profit
Total Revenue   = SUM(fact_sales[Sales])
Total Profit    = SUM(fact_sales[Profit])
Profit Margin % = DIVIDE([Total Profit], [Total Revenue]) * 100

-- Volume
Order Count   = DISTINCTCOUNT(fact_sales[OrderID])
Units Sold    = SUM(fact_sales[Quantity])
Avg Order Value = DIVIDE([Total Revenue], [Order Count])

-- Shipping
Avg Days to Ship = AVERAGE(fact_sales[DaysToShip])

-- Time Intelligence (requires dim_date marked as Date Table)
YTD Revenue  = CALCULATE([Total Revenue], DATESYTD(dim_date[FullDate]))
MTD Revenue  = CALCULATE([Total Revenue], DATESMTD(dim_date[FullDate]))
Prior Month Revenue = CALCULATE([Total Revenue], DATEADD(dim_date[FullDate], -1, MONTH))
MoM Growth % = DIVIDE([Total Revenue] - [Prior Month Revenue], [Prior Month Revenue]) * 100
```

---

## Marking the Date Table

For time-intelligence DAX functions to work correctly:

1. Select `dim_date` in the **Fields** pane.
2. Go to **Table tools → Mark as date table**.
3. Select `FullDate` as the date column.
