"""
Unit tests for data_analysis.py
================================
Tests that analysis functions produce correctly shaped, typed, and
logically consistent output DataFrames.

Run with:
    pip install pytest pandas numpy
    pytest tests/test_data_analysis.py -v
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from data_analysis import (
    compute_kpis,
    monthly_sales_trend,
    quarterly_sales_trend,
    category_performance,
    top_products,
    regional_performance,
    customer_segment_analysis,
    rfm_analysis,
    shipping_performance,
    discount_impact,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_sales() -> pd.DataFrame:
    """Representative cleaned sales DataFrame."""
    return pd.DataFrame({
        'OrderID': ['O001', 'O002', 'O003', 'O004', 'O005', 'O006'],
        'OrderDate': pd.to_datetime([
            '2023-01-10', '2023-01-20', '2023-02-05',
            '2023-02-15', '2023-03-01', '2023-03-20',
        ]),
        'ShipDate': pd.to_datetime([
            '2023-01-15', '2023-01-22', '2023-02-10',
            '2023-02-18', '2023-03-05', '2023-03-22',
        ]),
        'CustomerID': ['C001', 'C002', 'C001', 'C003', 'C002', 'C003'],
        'Region': ['East', 'West', 'East', 'South', 'West', 'South'],
        'Country': ['USA', 'USA', 'USA', 'USA', 'USA', 'USA'],
        'Category': ['Technology', 'Furniture', 'Office Supplies', 'Technology', 'Furniture', 'Technology'],
        'SubCategory': ['Phones', 'Chairs', 'Paper', 'Laptops', 'Tables', 'Accessories'],
        'Product': ['Phone A', 'Chair B', 'Paper C', 'Laptop D', 'Table E', 'Gadget F'],
        'Quantity': [2, 1, 10, 1, 2, 3],
        'UnitPrice': [800.00, 1300.00, 10.00, 1600.00, 250.00, 100.00],
        'Discount': [0.1, 0.05, 0.0, 0.15, 0.0, 0.05],
        'Sales': [1440.00, 1235.00, 100.00, 1360.00, 500.00, 285.00],
        'Profit': [288.00, 185.00, 36.00, 204.00, 75.00, 85.50],
        'ShipMode': ['Standard Class', 'Second Class', 'First Class', 'Same Day', 'Standard Class', 'Second Class'],
        'DaysToShip': [5, 2, 5, 0, 4, 2],
        'OrderYear': [2023, 2023, 2023, 2023, 2023, 2023],
        'OrderMonth': [1, 1, 2, 2, 3, 3],
        'OrderMonthName': ['January', 'January', 'February', 'February', 'March', 'March'],
        'OrderQuarter': ['Q1', 'Q1', 'Q1', 'Q1', 'Q1', 'Q1'],
        'ProfitMargin': [0.2, 0.15, 0.36, 0.15, 0.15, 0.30],
    })


@pytest.fixture
def sample_customers() -> pd.DataFrame:
    return pd.DataFrame({
        'CustomerID': ['C001', 'C002', 'C003'],
        'CustomerName': ['Alice Johnson', 'Bob Smith', 'Carol White'],
        'Segment': ['Consumer', 'Corporate', 'Home Office'],
        'LoyaltyTier': ['Gold', 'Silver', 'Bronze'],
    })


# ---------------------------------------------------------------------------
# KPI tests
# ---------------------------------------------------------------------------

class TestComputeKPIs:

    def test_returns_dataframe(self, sample_sales):
        result = compute_kpis(sample_sales)
        assert isinstance(result, pd.DataFrame)

    def test_has_kpi_and_value_columns(self, sample_sales):
        result = compute_kpis(sample_sales)
        assert list(result.columns) == ['KPI', 'Value']

    def test_total_revenue_correct(self, sample_sales):
        result = compute_kpis(sample_sales)
        expected = round(sample_sales['Sales'].sum(), 2)
        actual = result.loc[result['KPI'] == 'TotalRevenue', 'Value'].values[0]
        assert actual == expected

    def test_total_orders_correct(self, sample_sales):
        result = compute_kpis(sample_sales)
        expected = sample_sales['OrderID'].nunique()
        actual = result.loc[result['KPI'] == 'TotalOrders', 'Value'].values[0]
        assert actual == expected

    def test_profit_margin_between_0_and_100(self, sample_sales):
        result = compute_kpis(sample_sales)
        margin = result.loc[result['KPI'] == 'OverallProfitMarginPct', 'Value'].values[0]
        assert 0 <= margin <= 100


# ---------------------------------------------------------------------------
# Sales trend tests
# ---------------------------------------------------------------------------

class TestMonthlySalesTrend:

    def test_returns_dataframe(self, sample_sales):
        assert isinstance(monthly_sales_trend(sample_sales), pd.DataFrame)

    def test_has_required_columns(self, sample_sales):
        result = monthly_sales_trend(sample_sales)
        for col in ['OrderYear', 'OrderMonth', 'TotalRevenue', 'TotalProfit', 'OrderCount']:
            assert col in result.columns

    def test_revenue_non_negative(self, sample_sales):
        result = monthly_sales_trend(sample_sales)
        assert (result['TotalRevenue'] >= 0).all()


class TestQuarterlySalesTrend:

    def test_returns_dataframe(self, sample_sales):
        assert isinstance(quarterly_sales_trend(sample_sales), pd.DataFrame)

    def test_revenue_sums_match(self, sample_sales):
        result = quarterly_sales_trend(sample_sales)
        assert abs(result['TotalRevenue'].sum() - sample_sales['Sales'].sum()) < 0.01


# ---------------------------------------------------------------------------
# Category & product tests
# ---------------------------------------------------------------------------

class TestCategoryPerformance:

    def test_returns_dataframe(self, sample_sales):
        assert isinstance(category_performance(sample_sales), pd.DataFrame)

    def test_has_profit_margin(self, sample_sales):
        result = category_performance(sample_sales)
        assert 'ProfitMarginPct' in result.columns

    def test_unique_combinations(self, sample_sales):
        result = category_performance(sample_sales)
        combos = result[['Category', 'SubCategory']].drop_duplicates()
        assert len(combos) == len(result)


class TestTopProducts:

    def test_returns_correct_number(self, sample_sales):
        result = top_products(sample_sales, top_n=3)
        assert len(result) <= 3

    def test_sorted_by_revenue_descending(self, sample_sales):
        result = top_products(sample_sales, top_n=6)
        revenues = result['TotalRevenue'].tolist()
        assert revenues == sorted(revenues, reverse=True)


# ---------------------------------------------------------------------------
# Regional tests
# ---------------------------------------------------------------------------

class TestRegionalPerformance:

    def test_returns_dataframe(self, sample_sales):
        assert isinstance(regional_performance(sample_sales), pd.DataFrame)

    def test_revenue_share_sums_to_100(self, sample_sales):
        result = regional_performance(sample_sales)
        assert abs(result['RevenueSharePct'].sum() - 100.0) < 0.1


# ---------------------------------------------------------------------------
# Customer analysis tests
# ---------------------------------------------------------------------------

class TestCustomerSegmentAnalysis:

    def test_returns_dataframe(self, sample_sales, sample_customers):
        assert isinstance(customer_segment_analysis(sample_sales, sample_customers), pd.DataFrame)

    def test_segment_count_matches(self, sample_sales, sample_customers):
        result = customer_segment_analysis(sample_sales, sample_customers)
        unique_segments = sample_customers['Segment'].nunique()
        assert len(result) == unique_segments


class TestRFMAnalysis:

    def test_returns_dataframe(self, sample_sales):
        assert isinstance(rfm_analysis(sample_sales), pd.DataFrame)

    def test_has_required_columns(self, sample_sales):
        result = rfm_analysis(sample_sales)
        for col in ['CustomerID', 'Recency', 'Frequency', 'Monetary', 'RFM_Score', 'RFM_Segment']:
            assert col in result.columns

    def test_one_row_per_customer(self, sample_sales):
        result = rfm_analysis(sample_sales)
        assert result['CustomerID'].nunique() == len(result)

    def test_rfm_score_range(self, sample_sales):
        result = rfm_analysis(sample_sales)
        assert result['RFM_Score'].between(3, 12).all()


# ---------------------------------------------------------------------------
# Shipping tests
# ---------------------------------------------------------------------------

class TestShippingPerformance:

    def test_returns_dataframe(self, sample_sales):
        assert isinstance(shipping_performance(sample_sales), pd.DataFrame)

    def test_avg_days_non_negative(self, sample_sales):
        result = shipping_performance(sample_sales)
        assert (result['AvgDaysToShip'] >= 0).all()


# ---------------------------------------------------------------------------
# Discount impact tests
# ---------------------------------------------------------------------------

class TestDiscountImpact:

    def test_returns_dataframe(self, sample_sales):
        assert isinstance(discount_impact(sample_sales), pd.DataFrame)

    def test_revenue_sum_preserved(self, sample_sales):
        result = discount_impact(sample_sales)
        assert abs(result['TotalRevenue'].sum() - sample_sales['Sales'].sum()) < 0.01
