"""
Data Model Builder for Business Intelligence PowerBI Project
============================================================
Creates a star-schema data model from the cleaned datasets,
producing a fact table and conformed dimension tables ready for
import into Power BI.

Star Schema Layout
------------------
Fact Table:
    fact_sales      – one row per order line

Dimension Tables:
    dim_date        – date dimension (calendar attributes)
    dim_customer    – customer attributes
    dim_product     – product attributes
    dim_geography   – region / country attributes
    dim_shipmode    – shipping mode attributes

Usage:
    python scripts/data_model.py

Output:
    Star-schema CSV files saved to data/processed/model/
"""

import os
import pandas as pd
import numpy as np
from datetime import date, timedelta


PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
MODEL_DIR = os.path.join(PROCESSED_DIR, 'model')


def load_clean_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load cleaned CSVs."""
    sales = pd.read_csv(
        os.path.join(PROCESSED_DIR, 'sales_clean.csv'),
        parse_dates=['OrderDate', 'ShipDate']
    )
    customers = pd.read_csv(
        os.path.join(PROCESSED_DIR, 'customers_clean.csv'),
        parse_dates=['JoinDate']
    )
    products = pd.read_csv(os.path.join(PROCESSED_DIR, 'products_clean.csv'))
    return sales, customers, products


# ---------------------------------------------------------------------------
# Dimension: Date
# ---------------------------------------------------------------------------

def build_dim_date(start: date, end: date) -> pd.DataFrame:
    """
    Generate a full date dimension covering [start, end].
    Each row represents one calendar day with common BI attributes.
    """
    date_range = pd.date_range(start=start, end=end, freq='D')
    dim = pd.DataFrame({'FullDate': date_range})
    dim['DateKey'] = dim['FullDate'].dt.strftime('%Y%m%d').astype(int)
    dim['Year'] = dim['FullDate'].dt.year
    dim['Quarter'] = dim['FullDate'].dt.quarter
    dim['QuarterName'] = 'Q' + dim['Quarter'].astype(str)
    dim['Month'] = dim['FullDate'].dt.month
    dim['MonthName'] = dim['FullDate'].dt.strftime('%B')
    dim['MonthShort'] = dim['FullDate'].dt.strftime('%b')
    dim['Week'] = dim['FullDate'].dt.isocalendar().week.astype(int)
    dim['DayOfMonth'] = dim['FullDate'].dt.day
    dim['DayOfWeek'] = dim['FullDate'].dt.dayofweek + 1       # 1=Mon, 7=Sun
    dim['DayName'] = dim['FullDate'].dt.day_name()
    dim['IsWeekend'] = dim['DayOfWeek'].isin([6, 7])
    dim['YearMonth'] = dim['FullDate'].dt.strftime('%Y-%m')
    dim['YearQuarter'] = dim['Year'].astype(str) + '-' + dim['QuarterName']
    print(f"dim_date: {len(dim)} rows ({start} → {end})")
    return dim


# ---------------------------------------------------------------------------
# Dimension: Customer
# ---------------------------------------------------------------------------

def build_dim_customer(customers: pd.DataFrame) -> pd.DataFrame:
    """Select and rename customer attributes for the dimension table."""
    dim = customers[[
        'CustomerID', 'CustomerName', 'Segment', 'City', 'State',
        'Region', 'Country', 'LoyaltyTier', 'JoinDate', 'TenureYears'
    ]].copy()
    dim = dim.rename(columns={
        'CustomerName': 'FullName',
        'JoinDate': 'CustomerSince',
    })
    print(f"dim_customer: {len(dim)} rows")
    return dim


# ---------------------------------------------------------------------------
# Dimension: Product
# ---------------------------------------------------------------------------

def build_dim_product(products: pd.DataFrame) -> pd.DataFrame:
    """Select and rename product attributes for the dimension table."""
    dim = products[[
        'ProductID', 'ProductName', 'Category', 'SubCategory', 'Brand',
        'UnitCost', 'UnitPrice', 'GrossMarginPct', 'StockQuantity',
        'ReorderLevel', 'Supplier', 'Discontinued'
    ]].copy()
    print(f"dim_product: {len(dim)} rows")
    return dim


# ---------------------------------------------------------------------------
# Dimension: Geography
# ---------------------------------------------------------------------------

def build_dim_geography(sales: pd.DataFrame) -> pd.DataFrame:
    """Derive a geography dimension from unique Region/Country combinations in sales."""
    dim = (
        sales[['Region', 'Country']]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim.insert(0, 'GeoKey', dim['Region'].str[:3].str.upper() + '_' + dim['Country'].str[:3].str.upper())
    print(f"dim_geography: {len(dim)} rows")
    return dim


# ---------------------------------------------------------------------------
# Dimension: Ship Mode
# ---------------------------------------------------------------------------

def build_dim_shipmode(sales: pd.DataFrame) -> pd.DataFrame:
    """Derive a ship-mode dimension with expected day ranges."""
    ship_info = {
        'Same Day': (0, 0),
        'First Class': (1, 2),
        'Second Class': (3, 5),
        'Standard Class': (5, 7),
    }
    modes = sales['ShipMode'].dropna().unique()
    rows = []
    for mode in sorted(modes):
        min_days, max_days = ship_info.get(mode, (np.nan, np.nan))
        rows.append({'ShipMode': mode, 'MinDays': min_days, 'MaxDays': max_days})
    dim = pd.DataFrame(rows)
    dim.insert(0, 'ShipModeKey', range(1, len(dim) + 1))
    print(f"dim_shipmode: {len(dim)} rows")
    return dim


# ---------------------------------------------------------------------------
# Fact Table: Sales
# ---------------------------------------------------------------------------

def build_fact_sales(
    sales: pd.DataFrame,
    dim_date: pd.DataFrame,
    dim_customer: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_geography: pd.DataFrame,
    dim_shipmode: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the fact_sales table by joining foreign keys from all dimensions.
    Measures: Quantity, UnitPrice, Discount, Sales (revenue), Profit,
              DaysToShip, ProfitMargin.
    """
    fact = sales.copy()

    # DateKey (integer YYYYMMDD)
    fact['OrderDateKey'] = fact['OrderDate'].dt.strftime('%Y%m%d').astype(int)
    fact['ShipDateKey'] = fact['ShipDate'].dt.strftime('%Y%m%d').astype(int)

    # GeoKey
    geo_map = dim_geography.set_index(['Region', 'Country'])['GeoKey'].to_dict()
    fact['GeoKey'] = fact[['Region', 'Country']].apply(tuple, axis=1).map(geo_map)

    # ShipModeKey
    ship_map = dim_shipmode.set_index('ShipMode')['ShipModeKey']
    fact['ShipModeKey'] = fact['ShipMode'].map(ship_map)

    # Select fact columns
    fact_cols = [
        'OrderID', 'OrderDateKey', 'ShipDateKey',
        'CustomerID', 'GeoKey', 'ShipModeKey',
        'Category', 'SubCategory', 'Product',
        'Quantity', 'UnitPrice', 'Discount',
        'Sales', 'Profit', 'ProfitMargin', 'DaysToShip',
    ]
    fact = fact[[c for c in fact_cols if c in fact.columns]]
    print(f"fact_sales: {len(fact)} rows")
    return fact


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Building star-schema data model...\n")
    os.makedirs(MODEL_DIR, exist_ok=True)

    sales, customers, products = load_clean_data()

    # Build dimensions
    date_start = sales['OrderDate'].min().date()
    date_end = max(sales['OrderDate'].max().date(), sales['ShipDate'].dropna().max().date())

    dim_date = build_dim_date(date_start, date_end)
    dim_customer = build_dim_customer(customers)
    dim_product = build_dim_product(products)
    dim_geography = build_dim_geography(sales)
    dim_shipmode = build_dim_shipmode(sales)
    fact_sales = build_fact_sales(
        sales, dim_date, dim_customer, dim_product, dim_geography, dim_shipmode
    )

    # Save to model directory
    tables = {
        'dim_date.csv': dim_date,
        'dim_customer.csv': dim_customer,
        'dim_product.csv': dim_product,
        'dim_geography.csv': dim_geography,
        'dim_shipmode.csv': dim_shipmode,
        'fact_sales.csv': fact_sales,
    }
    for filename, df in tables.items():
        path = os.path.join(MODEL_DIR, filename)
        df.to_csv(path, index=False)
        print(f"  Saved {filename}")

    print("\nStar-schema model build complete.")
    print(f"Files are in: {MODEL_DIR}")


if __name__ == '__main__':
    main()
