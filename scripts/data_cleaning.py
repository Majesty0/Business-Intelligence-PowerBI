"""
Data Cleaning Script for Business Intelligence PowerBI Project
=============================================================
This script cleans and validates the raw sales, customer, and product data
before loading it into Power BI for dashboard creation.

Usage:
    python scripts/data_cleaning.py

Output:
    Cleaned CSV files saved to data/processed/
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime


RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')


def load_data(filename: str) -> pd.DataFrame:
    """Load a CSV file from the raw data directory."""
    filepath = os.path.join(RAW_DATA_DIR, filename)
    df = pd.read_csv(filepath)
    print(f"Loaded {filename}: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def save_data(df: pd.DataFrame, filename: str) -> None:
    """Save a cleaned DataFrame to the processed data directory."""
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    filepath = os.path.join(PROCESSED_DATA_DIR, filename)
    df.to_csv(filepath, index=False)
    print(f"Saved cleaned data to {filepath}: {df.shape[0]} rows")


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate the sales dataset.

    Steps:
      1. Parse date columns
      2. Drop duplicate order IDs
      3. Remove rows with missing critical fields
      4. Validate numeric ranges (Quantity, UnitPrice, Discount, Sales, Profit)
      5. Standardise text columns (strip whitespace, title-case names)
      6. Derive additional date features (Year, Month, Quarter, DayOfWeek)
      7. Recalculate Sales and Profit to ensure consistency
    """
    print("\n--- Cleaning Sales Data ---")

    # 1. Parse dates
    for col in ['OrderDate', 'ShipDate']:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # 2. Drop duplicate OrderIDs (keep first occurrence)
    before = len(df)
    df = df.drop_duplicates(subset=['OrderID'], keep='first')
    print(f"  Removed {before - len(df)} duplicate orders")

    # 3. Drop rows missing critical fields
    critical_cols = ['OrderID', 'CustomerID', 'Product', 'Quantity', 'UnitPrice', 'Sales']
    before = len(df)
    df = df.dropna(subset=critical_cols)
    print(f"  Removed {before - len(df)} rows with missing critical fields")

    # 4. Validate numeric ranges
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    df = df[(df['Discount'] >= 0) & (df['Discount'] <= 1)]
    df = df[df['Sales'] >= 0]

    # 5. Standardise text columns
    for col in ['CustomerName', 'Region', 'Country', 'Category', 'SubCategory', 'ShipMode']:
        df[col] = df[col].str.strip().str.title()

    # 6. Derive date features
    df['OrderYear'] = df['OrderDate'].dt.year
    df['OrderMonth'] = df['OrderDate'].dt.month
    df['OrderMonthName'] = df['OrderDate'].dt.strftime('%B')
    df['OrderQuarter'] = df['OrderDate'].dt.quarter.map(
        {1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4'}
    )
    df['OrderDayOfWeek'] = df['OrderDate'].dt.day_name()
    df['DaysToShip'] = (df['ShipDate'] - df['OrderDate']).dt.days

    # 7. Recalculate Sales and Profit for consistency
    df['CalculatedSales'] = (df['Quantity'] * df['UnitPrice'] * (1 - df['Discount'])).round(2)
    df['ProfitMargin'] = (df['Profit'] / df['Sales'].replace(0, np.nan)).round(4)

    print(f"  Sales data clean complete: {len(df)} rows remain")
    return df


def clean_customer_data(df: pd.DataFrame,
                        reference_date: datetime | None = None) -> pd.DataFrame:
    """
    Clean and validate the customers dataset.

    Steps:
      1. Drop duplicates on CustomerID
      2. Validate email format (basic check)
      3. Standardise text columns
      4. Parse JoinDate and derive customer tenure in days

    Args:
        df: Raw customers DataFrame.
        reference_date: Date used to compute tenure. Defaults to today if not
            provided. Pass a fixed date for reproducible results.
    """
    print("\n--- Cleaning Customer Data ---")

    # 1. Drop duplicate CustomerIDs
    before = len(df)
    df = df.drop_duplicates(subset=['CustomerID'], keep='first')
    print(f"  Removed {before - len(df)} duplicate customers")

    # 2. Basic email validation
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    invalid_emails = ~df['Email'].str.match(email_pattern, na=False)
    if invalid_emails.any():
        print(f"  Warning: {invalid_emails.sum()} rows have invalid email addresses")
    df.loc[invalid_emails, 'Email'] = np.nan

    # 3. Standardise text columns
    for col in ['CustomerName', 'Segment', 'City', 'State', 'Region', 'Country', 'LoyaltyTier']:
        df[col] = df[col].str.strip().str.title()

    # 4. Parse JoinDate and compute tenure
    if reference_date is None:
        reference_date = datetime.today()
    df['JoinDate'] = pd.to_datetime(df['JoinDate'], errors='coerce')
    df['TenureDays'] = (reference_date - df['JoinDate']).dt.days
    df['TenureYears'] = (df['TenureDays'] / 365.25).round(1)

    print(f"  Customer data clean complete: {len(df)} rows remain")
    return df


def clean_product_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate the products dataset.

    Steps:
      1. Drop duplicate ProductIDs
      2. Validate that UnitCost < UnitPrice
      3. Standardise text columns
      4. Calculate gross margin percentage
    """
    print("\n--- Cleaning Product Data ---")

    # 1. Drop duplicate ProductIDs
    before = len(df)
    df = df.drop_duplicates(subset=['ProductID'], keep='first')
    print(f"  Removed {before - len(df)} duplicate products")

    # 2. Validate cost vs price
    invalid_margin = df['UnitCost'] >= df['UnitPrice']
    if invalid_margin.any():
        print(f"  Warning: {invalid_margin.sum()} products have cost >= price")

    # 3. Standardise text columns
    for col in ['ProductName', 'Category', 'SubCategory', 'Brand', 'Supplier']:
        df[col] = df[col].str.strip()
    df['Discontinued'] = df['Discontinued'].str.strip().str.title()

    # 4. Calculate gross margin %
    df['GrossMarginPct'] = (
        (df['UnitPrice'] - df['UnitCost']) / df['UnitPrice'] * 100
    ).round(2)

    print(f"  Product data clean complete: {len(df)} rows remain")
    return df


def generate_data_quality_report(sales: pd.DataFrame,
                                 customers: pd.DataFrame,
                                 products: pd.DataFrame) -> None:
    """Print a brief data-quality summary for each cleaned dataset."""
    print("\n=== DATA QUALITY REPORT ===")
    for name, df in [("Sales", sales), ("Customers", customers), ("Products", products)]:
        null_counts = df.isnull().sum()
        null_cols = null_counts[null_counts > 0]
        print(f"\n{name} ({df.shape[0]} rows x {df.shape[1]} cols):")
        if null_cols.empty:
            print("  No missing values.")
        else:
            for col, cnt in null_cols.items():
                print(f"  {col}: {cnt} missing ({cnt / len(df) * 100:.1f}%)")
    print("\n===========================\n")


def main():
    print("Starting data cleaning pipeline...")

    sales_raw = load_data('sales_data.csv')
    customers_raw = load_data('customers.csv')
    products_raw = load_data('products.csv')

    sales_clean = clean_sales_data(sales_raw)
    customers_clean = clean_customer_data(customers_raw)
    products_clean = clean_product_data(products_raw)

    generate_data_quality_report(sales_clean, customers_clean, products_clean)

    save_data(sales_clean, 'sales_clean.csv')
    save_data(customers_clean, 'customers_clean.csv')
    save_data(products_clean, 'products_clean.csv')

    print("Data cleaning pipeline complete.")


if __name__ == '__main__':
    main()
