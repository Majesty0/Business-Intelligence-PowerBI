# Business-Intelligence-PowerBI

Kenya Agricultural Commodity Prices – Power BI Analysis
📌 Project Overview

This project presents a comprehensive data analysis and visualization of Kenya’s agricultural commodity prices using Power BI. The objective was to transform raw market price data into a structured data model and develop an interactive dashboard that provides insights into price trends, regional disparities, commodity performance, and market structure.

The dataset used contains over 11,000 records and includes information on commodity type, county, market, sale type (retail/wholesale), and price in Kenyan Shillings (KES).
Source: https://www.kaggle.com/datasets/usmanlovescode/kenya-food-prices-dataset?utm_source=chatgpt.com
🎯 Objectives

Perform data cleaning and transformation using Power Query.
Design a proper star schema data model.
Implement time intelligence measures (YoY and QoQ analysis).
Analyze price trends over time.
Identify regional price differences across counties.
Compare performance across commodities and sale types.
Develop a professional and interactive dashboard for decision-making.

🛠 Tools & Technologies

Power BI Desktop
Power Query (M Language)
DAX (Data Analysis Expressions)
Star Schema Data Modeling
Time Intelligence Functions

📂 Data Preparation (Power Query)

The following steps were performed:
Data profiling (column quality, distribution, and column profile enabled).
Corrected data types (Date, Whole Number, Currency).
Cleaned and standardized text fields (Trim, Clean, Proper Case).
Created conditional columns to categorize price levels (High/Medium/Low).
Built custom calculated columns using M formulas.
Removed duplicates and handled missing values.
Created dimension tables (DimDate, DimCounty, DimCommodity, DimSaleType).

🧱 Data Model

A star schema was implemented:
Fact Table
FactFoodPrices (main transactional table)
Dimension Tables
DimDate
DimCounty
DimCommodity
DimSaleType

Relationships:

One-to-many from each dimension to the fact table.
Single-direction filtering.
Proper Date table created using CALENDAR() and marked as Date Table.

📊 Key DAX Measures

Total Price (KES)
Minimum Price
Price Spread
Total Records

Year-over-Year (YoY) Change %
Quarter-over-Quarter (QoQ) Change %
Average Price by County

Time intelligence functions used:

SAMEPERIODLASTYEAR()
PREVIOUSQUARTER()
CALCULATE()
DIVIDE()

📈 Dashboard Insights

Key findings from the analysis:
Agricultural prices show a long-term declining trend with recent recovery.
There are noticeable regional price disparities across counties.
Certain commodities contribute significantly more to total market value.
The price spread indicates high variability between lowest and highest prices.
One sale type dominates market transactions.

📌 Business Value

This dashboard enables:

Monitoring of agricultural price stability.
Identification of regional market imbalances.
Data-driven policy and pricing decisions.
Trend forecasting using historical patterns.
Performance comparison across commodities and counties.

🚀 Skills Demonstrated

Real-world dataset handling (non-toy dataset)
Data cleaning and transformation
Star schema modeling
Time intelligence analysis
DAX measure development
Dashboard design & storytelling
Analytical reasoning


👤 Author

Power BI Data Analysis Project
Kenya Agricultural Commodity Prices
2026

