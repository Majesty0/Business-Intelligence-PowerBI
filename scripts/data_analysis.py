"""
Data Analysis Script for Business Intelligence PowerBI Project
==============================================================
Performs exploratory data analysis (EDA) and generates summary
statistics that feed into Power BI dashboards.

Usage:
    python scripts/data_analysis.py

Output:
    Analysis result CSVs saved to data/processed/
"""

import os
import pandas as pd
import numpy as np


PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')


def load_clean_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all cleaned datasets."""
    sales = pd.read_csv(os.path.join(PROCESSED_DIR, 'sales_clean.csv'), parse_dates=['OrderDate', 'ShipDate'])
    customers = pd.read_csv(os.path.join(PROCESSED_DIR, 'customers_clean.csv'), parse_dates=['JoinDate'])
    products = pd.read_csv(os.path.join(PROCESSED_DIR, 'products_clean.csv'))
    return sales, customers, products


# ---------------------------------------------------------------------------
# KPI Summary
# ---------------------------------------------------------------------------

def compute_kpis(sales: pd.DataFrame) -> pd.DataFrame:
    """Calculate top-level KPI metrics."""
    kpis = {
        'TotalRevenue': round(sales['Sales'].sum(), 2),
        'TotalProfit': round(sales['Profit'].sum(), 2),
        'OverallProfitMarginPct': round(sales['Profit'].sum() / sales['Sales'].sum() * 100, 2),
        'TotalOrders': sales['OrderID'].nunique(),
        'TotalCustomers': sales['CustomerID'].nunique(),
        'TotalUnitsSold': int(sales['Quantity'].sum()),
        'AvgOrderValue': round(sales.groupby('OrderID')['Sales'].sum().mean(), 2),
        'AvgDaysToShip': round(sales['DaysToShip'].mean(), 1),
    }
    df = pd.DataFrame(list(kpis.items()), columns=['KPI', 'Value'])
    print("\n=== KPI SUMMARY ===")
    for _, row in df.iterrows():
        print(f"  {row['KPI']}: {row['Value']}")
    return df


# ---------------------------------------------------------------------------
# Sales Trend Analysis
# ---------------------------------------------------------------------------

def monthly_sales_trend(sales: pd.DataFrame) -> pd.DataFrame:
    """Aggregate monthly revenue, profit, and order count."""
    monthly = (
        sales.groupby(['OrderYear', 'OrderMonth', 'OrderMonthName', 'OrderQuarter'])
        .agg(
            TotalRevenue=('Sales', 'sum'),
            TotalProfit=('Profit', 'sum'),
            OrderCount=('OrderID', 'nunique'),
            UnitsSold=('Quantity', 'sum')
        )
        .round(2)
        .reset_index()
        .sort_values(['OrderYear', 'OrderMonth'])
    )
    monthly['MoM_RevenueGrowthPct'] = (
        monthly['TotalRevenue'].pct_change() * 100
    ).round(2)
    print(f"\nMonthly trend: {len(monthly)} months computed")
    return monthly


def quarterly_sales_trend(sales: pd.DataFrame) -> pd.DataFrame:
    """Aggregate quarterly revenue and profit."""
    quarterly = (
        sales.groupby(['OrderYear', 'OrderQuarter'])
        .agg(
            TotalRevenue=('Sales', 'sum'),
            TotalProfit=('Profit', 'sum'),
            OrderCount=('OrderID', 'nunique'),
        )
        .round(2)
        .reset_index()
        .sort_values(['OrderYear', 'OrderQuarter'])
    )
    print(f"Quarterly trend: {len(quarterly)} quarters computed")
    return quarterly


# ---------------------------------------------------------------------------
# Category & Product Analysis
# ---------------------------------------------------------------------------

def category_performance(sales: pd.DataFrame) -> pd.DataFrame:
    """Revenue, profit, and margin by Category and SubCategory."""
    cat = (
        sales.groupby(['Category', 'SubCategory'])
        .agg(
            TotalRevenue=('Sales', 'sum'),
            TotalProfit=('Profit', 'sum'),
            UnitsSold=('Quantity', 'sum'),
            OrderCount=('OrderID', 'nunique')
        )
        .round(2)
        .reset_index()
    )
    cat['ProfitMarginPct'] = (cat['TotalProfit'] / cat['TotalRevenue'] * 100).round(2)
    cat = cat.sort_values('TotalRevenue', ascending=False)
    print(f"\nCategory performance: {len(cat)} category-subcategory combinations")
    return cat


def top_products(sales: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Top N products by revenue."""
    prod = (
        sales.groupby(['Product', 'Category', 'SubCategory'])
        .agg(
            TotalRevenue=('Sales', 'sum'),
            TotalProfit=('Profit', 'sum'),
            UnitsSold=('Quantity', 'sum'),
        )
        .round(2)
        .reset_index()
        .nlargest(top_n, 'TotalRevenue')
    )
    prod['ProfitMarginPct'] = (prod['TotalProfit'] / prod['TotalRevenue'] * 100).round(2)
    print(f"Top {top_n} products by revenue computed")
    return prod


# ---------------------------------------------------------------------------
# Regional Analysis
# ---------------------------------------------------------------------------

def regional_performance(sales: pd.DataFrame) -> pd.DataFrame:
    """Revenue and profit by Region."""
    region = (
        sales.groupby('Region')
        .agg(
            TotalRevenue=('Sales', 'sum'),
            TotalProfit=('Profit', 'sum'),
            OrderCount=('OrderID', 'nunique'),
            CustomerCount=('CustomerID', 'nunique')
        )
        .round(2)
        .reset_index()
        .sort_values('TotalRevenue', ascending=False)
    )
    region['ProfitMarginPct'] = (region['TotalProfit'] / region['TotalRevenue'] * 100).round(2)
    region['RevenueSharePct'] = (region['TotalRevenue'] / region['TotalRevenue'].sum() * 100).round(2)
    print(f"\nRegional performance: {len(region)} regions computed")
    return region


# ---------------------------------------------------------------------------
# Customer Analysis
# ---------------------------------------------------------------------------

def customer_segment_analysis(sales: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Revenue and profitability by customer segment."""
    merged = sales.merge(customers[['CustomerID', 'Segment', 'LoyaltyTier']], on='CustomerID', how='left')
    seg = (
        merged.groupby('Segment')
        .agg(
            TotalRevenue=('Sales', 'sum'),
            TotalProfit=('Profit', 'sum'),
            OrderCount=('OrderID', 'nunique'),
            CustomerCount=('CustomerID', 'nunique')
        )
        .round(2)
        .reset_index()
    )
    seg['AvgRevenuePerCustomer'] = (seg['TotalRevenue'] / seg['CustomerCount']).round(2)
    seg['ProfitMarginPct'] = (seg['TotalProfit'] / seg['TotalRevenue'] * 100).round(2)
    print(f"\nCustomer segment analysis: {len(seg)} segments computed")
    return seg


def rfm_analysis(sales: pd.DataFrame,
                 snapshot_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """
    Recency-Frequency-Monetary (RFM) analysis.
    Scores customers 1-4 on each dimension, then assigns a segment label.

    Args:
        sales: Cleaned sales DataFrame.
        snapshot_date: Reference date for recency calculation. Defaults to one
            day after the latest order in *sales*. Pass a fixed date for
            reproducible RFM scores across analysis runs.
    """
    if snapshot_date is None:
        snapshot_date = sales['OrderDate'].max() + pd.Timedelta(days=1)

    rfm = sales.groupby('CustomerID').agg(
        Recency=('OrderDate', lambda x: (snapshot_date - x.max()).days),
        Frequency=('OrderID', 'nunique'),
        Monetary=('Sales', 'sum')
    ).reset_index()

    rfm['R_Score'] = pd.qcut(rfm['Recency'], q=4, labels=[4, 3, 2, 1]).astype(int)
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4]).astype(int)
    rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), q=4, labels=[1, 2, 3, 4]).astype(int)
    rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']

    def segment_label(score: int) -> str:
        if score >= 10:
            return 'Champions'
        elif score >= 8:
            return 'Loyal Customers'
        elif score >= 6:
            return 'Potential Loyalists'
        elif score >= 4:
            return 'At Risk'
        else:
            return 'Lost'

    rfm['RFM_Segment'] = rfm['RFM_Score'].apply(segment_label)
    rfm['Monetary'] = rfm['Monetary'].round(2)
    print(f"\nRFM analysis: {len(rfm)} customers scored")
    return rfm


# ---------------------------------------------------------------------------
# Shipping Analysis
# ---------------------------------------------------------------------------

def shipping_performance(sales: pd.DataFrame) -> pd.DataFrame:
    """Average days-to-ship and order count by ShipMode."""
    ship = (
        sales.groupby('ShipMode')
        .agg(
            AvgDaysToShip=('DaysToShip', 'mean'),
            OrderCount=('OrderID', 'nunique'),
            TotalRevenue=('Sales', 'sum')
        )
        .round(2)
        .reset_index()
        .sort_values('AvgDaysToShip')
    )
    print(f"\nShipping analysis: {len(ship)} ship modes computed")
    return ship


# ---------------------------------------------------------------------------
# Discount Impact Analysis
# ---------------------------------------------------------------------------

def discount_impact(sales: pd.DataFrame) -> pd.DataFrame:
    """Revenue and profit by discount bracket."""
    bins = [-0.001, 0, 0.05, 0.1, 0.15, 1.0]
    labels = ['No Discount', '1-5%', '6-10%', '11-15%', '>15%']
    sales = sales.copy()
    sales['DiscountBracket'] = pd.cut(sales['Discount'], bins=bins, labels=labels)
    disc = (
        sales.groupby('DiscountBracket', observed=True)
        .agg(
            TotalRevenue=('Sales', 'sum'),
            TotalProfit=('Profit', 'sum'),
            OrderCount=('OrderID', 'nunique')
        )
        .round(2)
        .reset_index()
    )
    disc['ProfitMarginPct'] = (disc['TotalProfit'] / disc['TotalRevenue'] * 100).round(2)
    print(f"\nDiscount impact: {len(disc)} brackets computed")
    return disc


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Starting data analysis pipeline...")
    sales, customers, products = load_clean_data()

    # Compute all analyses
    kpis = compute_kpis(sales)
    monthly = monthly_sales_trend(sales)
    quarterly = quarterly_sales_trend(sales)
    cat_perf = category_performance(sales)
    top_prods = top_products(sales, top_n=10)
    regional = regional_performance(sales)
    seg_analysis = customer_segment_analysis(sales, customers)
    rfm = rfm_analysis(sales)
    shipping = shipping_performance(sales)
    discount = discount_impact(sales)

    # Save results
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    output_files = {
        'kpi_summary.csv': kpis,
        'monthly_sales_trend.csv': monthly,
        'quarterly_sales_trend.csv': quarterly,
        'category_performance.csv': cat_perf,
        'top_products.csv': top_prods,
        'regional_performance.csv': regional,
        'customer_segment_analysis.csv': seg_analysis,
        'rfm_analysis.csv': rfm,
        'shipping_performance.csv': shipping,
        'discount_impact.csv': discount,
    }

    for filename, df in output_files.items():
        path = os.path.join(PROCESSED_DIR, filename)
        df.to_csv(path, index=False)
        print(f"Saved {filename}")

    print("\nData analysis pipeline complete.")


if __name__ == '__main__':
    main()
