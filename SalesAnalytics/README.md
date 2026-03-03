# Sales Analytics Example

A complete, production-ready Power BI analytics solution for sales data built on a star schema.

## Data Model

```
                  ┌─────────────┐
                  │    Date     │  (mark as Date Table)
                  │─────────────│
                  │ Date (PK)   │
                  │ Year        │
                  │ Quarter     │
                  │ Month       │
                  │ MonthName   │
                  │ IsWeekend   │
                  └──────┬──────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
   ┌──────┴──────┐ ┌─────┴──────┐ ┌────┴─────────┐
   │  Customers  │ │   Sales    │ │   Products   │
   │─────────────│ │  (Fact)    │ │──────────────│
   │CustomerID   │ │────────────│ │ProductID     │
   │CustomerName │ │OrderID     │ │ProductName   │
   │Segment      │ │OrderDate ──┼─│Category      │
   │Country      │ │CustomerID─ │ │SubCategory   │
   │Region       │ │ProductID ──┘ │UnitPrice     │
   └─────────────┘ │SalesAmount  │ └─────────────┘
                   │Quantity     │
                   │UnitCost     │
                   │Discount     │
                   └─────────────┘
```

## Files

| File | Description |
|---|---|
| [`sales_queries.pq`](sales_queries.pq) | Power Query (M) scripts to load and clean Sales, Customers, and Products |
| [`sales_measures.dax`](sales_measures.dax) | DAX measures: revenue, profit, customer KPIs, ranking, and trend analysis |

## Setup Steps

1. **Load data** — Paste each query from `sales_queries.pq` into the Advanced Editor and update file paths.
2. **Build date table** — Use the dynamic date table pattern in `PowerQuery/common_transformations.pq` (snippet #7) and mark it as a Date Table.
3. **Set relationships** — In Model view, create relationships:
   - `Sales[OrderDate]` → `Date[Date]` (many-to-one)
   - `Sales[CustomerID]` → `Customers[CustomerID]` (many-to-one)
   - `Sales[ProductID]` → `Products[ProductID]` (many-to-one)
4. **Add measures** — Create a dedicated **Measures** table, then paste measures from `sales_measures.dax`.
5. **Build visuals** — Use the measures in cards, line charts, bar charts, and matrix visuals.

## Key Measures

| Measure | Description |
|---|---|
| `Revenue` | Total sales amount |
| `Revenue YoY %` | Year-over-year growth percentage |
| `Revenue YTD` | Year-to-date revenue |
| `Gross Profit Margin %` | Profitability ratio |
| `Active Customers` | Distinct customers in period |
| `New Customers` | Customers with first order in period |
| `Customer Retention Rate %` | Returning customers vs. prior period |
| `Revenue 3M Rolling Avg` | Smoothed 3-month trend |
| `Performance Status` | Label: Exceeds / On / Below Target / At Risk |

## Recommended Visuals

- **KPI Cards**: Revenue, Revenue YoY %, Gross Profit Margin %, Active Customers
- **Line Chart**: Revenue & Revenue LY over time (monthly)
- **Bar Chart**: Revenue by Category or Region
- **Matrix**: Product SubCategory × Region with Revenue and Gross Profit Margin %
- **Scatter Chart**: Revenue vs. Gross Profit Margin % per Product
- **Slicer**: Year, Quarter, Region, Segment
