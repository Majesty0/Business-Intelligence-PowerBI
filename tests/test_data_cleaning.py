"""
Unit tests for data_cleaning.py
================================
Tests cover the core cleaning transformations for each dataset.

Run with:
    pip install pytest pandas numpy
    pytest tests/test_data_cleaning.py -v
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

# Allow importing from the scripts package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from data_cleaning import clean_sales_data, clean_customer_data, clean_product_data


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_sales() -> pd.DataFrame:
    """Minimal valid sales DataFrame."""
    return pd.DataFrame({
        'OrderID': ['O001', 'O002', 'O003'],
        'OrderDate': ['2023-01-05', '2023-02-10', '2023-03-15'],
        'ShipDate': ['2023-01-10', '2023-02-15', '2023-03-18'],
        'CustomerID': ['C001', 'C002', 'C001'],
        'CustomerName': ['alice johnson', 'BOB SMITH', 'alice johnson'],
        'Region': ['east', 'west', 'east'],
        'Country': ['usa', 'usa', 'usa'],
        'Category': ['technology', 'furniture', 'office supplies'],
        'SubCategory': ['phones', 'chairs', 'paper'],
        'Product': ['Phone A', 'Chair B', 'Paper C'],
        'Quantity': [2, 1, 10],
        'UnitPrice': [799.99, 1299.00, 9.99],
        'Discount': [0.1, 0.05, 0.0],
        'Sales': [1439.98, 1234.05, 99.90],
        'Profit': [287.99, 184.11, 35.96],
        'ShipMode': ['standard class', 'second class', 'first class'],
    })


@pytest.fixture
def minimal_customers() -> pd.DataFrame:
    """Minimal valid customers DataFrame."""
    return pd.DataFrame({
        'CustomerID': ['C001', 'C002'],
        'CustomerName': ['alice johnson', 'BOB SMITH'],
        'Segment': ['consumer', 'corporate'],
        'Email': ['alice@example.com', 'not-an-email'],
        'Phone': ['555-0101', '555-0102'],
        'City': ['new york', 'los angeles'],
        'State': ['ny', 'ca'],
        'Region': ['east', 'west'],
        'Country': ['usa', 'usa'],
        'JoinDate': ['2020-03-15', '2019-07-22'],
        'TotalOrders': [8, 7],
        'TotalSpend': [5243.51, 6396.22],
        'LoyaltyTier': ['gold', 'platinum'],
    })


@pytest.fixture
def minimal_products() -> pd.DataFrame:
    """Minimal valid products DataFrame."""
    return pd.DataFrame({
        'ProductID': ['P001', 'P002'],
        'ProductName': ['Phone X', 'Chair Y'],
        'Category': ['Technology', 'Furniture'],
        'SubCategory': ['Phones', 'Chairs'],
        'Brand': ['BrandA', 'BrandB'],
        'UnitCost': [500.00, 700.00],
        'UnitPrice': [799.99, 1299.00],
        'StockQuantity': [100, 50],
        'ReorderLevel': [20, 10],
        'Supplier': ['Supplier A', 'Supplier B'],
        'LaunchDate': ['2022-01-01', '2021-06-01'],
        'Discontinued': ['No', 'No'],
    })


# ---------------------------------------------------------------------------
# Sales cleaning tests
# ---------------------------------------------------------------------------

class TestCleanSalesData:

    def test_date_columns_parsed(self, minimal_sales):
        result = clean_sales_data(minimal_sales)
        assert pd.api.types.is_datetime64_any_dtype(result['OrderDate'])
        assert pd.api.types.is_datetime64_any_dtype(result['ShipDate'])

    def test_derived_date_columns_present(self, minimal_sales):
        result = clean_sales_data(minimal_sales)
        for col in ['OrderYear', 'OrderMonth', 'OrderMonthName', 'OrderQuarter', 'OrderDayOfWeek', 'DaysToShip']:
            assert col in result.columns, f"Missing column: {col}"

    def test_text_columns_title_cased(self, minimal_sales):
        result = clean_sales_data(minimal_sales)
        assert result['CustomerName'].iloc[0] == 'Alice Johnson'
        assert result['Region'].iloc[0] == 'East'

    def test_duplicate_orders_removed(self, minimal_sales):
        dup = pd.concat([minimal_sales, minimal_sales.iloc[:1]], ignore_index=True)
        result = clean_sales_data(dup)
        assert result['OrderID'].nunique() == result.shape[0]

    def test_invalid_quantity_removed(self, minimal_sales):
        bad = minimal_sales.copy()
        bad.loc[0, 'Quantity'] = 0
        result = clean_sales_data(bad)
        assert (result['Quantity'] > 0).all()

    def test_invalid_discount_removed(self, minimal_sales):
        bad = minimal_sales.copy()
        bad.loc[0, 'Discount'] = -0.1
        result = clean_sales_data(bad)
        assert (result['Discount'] >= 0).all()

    def test_days_to_ship_non_negative(self, minimal_sales):
        result = clean_sales_data(minimal_sales)
        assert (result['DaysToShip'] >= 0).all()

    def test_profit_margin_column_added(self, minimal_sales):
        result = clean_sales_data(minimal_sales)
        assert 'ProfitMargin' in result.columns

    def test_order_quarter_values(self, minimal_sales):
        result = clean_sales_data(minimal_sales)
        assert set(result['OrderQuarter'].unique()).issubset({'Q1', 'Q2', 'Q3', 'Q4'})


# ---------------------------------------------------------------------------
# Customer cleaning tests
# ---------------------------------------------------------------------------

class TestCleanCustomerData:

    def test_invalid_email_set_to_nan(self, minimal_customers):
        result = clean_customer_data(minimal_customers)
        assert pd.isna(result.loc[result['CustomerID'] == 'C002', 'Email'].values[0])

    def test_valid_email_kept(self, minimal_customers):
        result = clean_customer_data(minimal_customers)
        assert result.loc[result['CustomerID'] == 'C001', 'Email'].values[0] == 'alice@example.com'

    def test_text_columns_title_cased(self, minimal_customers):
        result = clean_customer_data(minimal_customers)
        assert result['CustomerName'].iloc[0] == 'Alice Johnson'
        assert result['Segment'].iloc[0] == 'Consumer'

    def test_tenure_columns_added(self, minimal_customers):
        result = clean_customer_data(minimal_customers)
        assert 'TenureDays' in result.columns
        assert 'TenureYears' in result.columns

    def test_tenure_positive(self, minimal_customers):
        result = clean_customer_data(minimal_customers)
        assert (result['TenureDays'] > 0).all()

    def test_duplicate_customers_removed(self, minimal_customers):
        dup = pd.concat([minimal_customers, minimal_customers.iloc[:1]], ignore_index=True)
        result = clean_customer_data(dup)
        assert result['CustomerID'].nunique() == result.shape[0]


# ---------------------------------------------------------------------------
# Product cleaning tests
# ---------------------------------------------------------------------------

class TestCleanProductData:

    def test_gross_margin_calculated(self, minimal_products):
        result = clean_product_data(minimal_products)
        expected = round((799.99 - 500.00) / 799.99 * 100, 2)
        assert result.loc[result['ProductID'] == 'P001', 'GrossMarginPct'].values[0] == expected

    def test_duplicate_products_removed(self, minimal_products):
        dup = pd.concat([minimal_products, minimal_products.iloc[:1]], ignore_index=True)
        result = clean_product_data(dup)
        assert result['ProductID'].nunique() == result.shape[0]

    def test_gross_margin_column_present(self, minimal_products):
        result = clean_product_data(minimal_products)
        assert 'GrossMarginPct' in result.columns

    def test_gross_margin_range(self, minimal_products):
        result = clean_product_data(minimal_products)
        assert (result['GrossMarginPct'] > 0).all()
        assert (result['GrossMarginPct'] < 100).all()
