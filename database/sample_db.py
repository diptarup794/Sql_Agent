import os
import sqlite3
import pandas as pd

def create_sample_database(db_path="sample.db"):
    """Create a sample database with sales and customer data."""
    conn = sqlite3.connect(db_path)
    
    # Create customers table
    customers_data = {
        'customer_id': range(1, 11),
        'name': [
            'John Smith', 'Emma Johnson', 'Michael Brown', 'Olivia Davis',
            'William Wilson', 'Sophia Martinez', 'James Taylor', 'Isabella Anderson',
            'Benjamin Thomas', 'Mia Hernandez'
        ],
        'email': [
            'john@example.com', 'emma@example.com', 'michael@example.com',
            'olivia@example.com', 'william@example.com', 'sophia@example.com',
            'james@example.com', 'isabella@example.com', 'benjamin@example.com',
            'mia@example.com'
        ],
        'city': [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
            'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'
        ]
    }
    
    # Create products table
    products_data = {
        'product_id': range(1, 11),
        'name': [
            'Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Monitor',
            'Keyboard', 'Mouse', 'Printer', 'Camera', 'Speaker'
        ],
        'category': [
            'Electronics', 'Electronics', 'Electronics', 'Audio', 'Electronics',
            'Accessories', 'Accessories', 'Office', 'Electronics', 'Audio'
        ],
        'price': [
            1200.00, 800.00, 500.00, 150.00, 300.00,
            80.00, 50.00, 200.00, 600.00, 120.00
        ],
        'stock': [
            50, 100, 75, 200, 60,
            150, 200, 40, 30, 80
        ]
    }
    
    # Create sales table
    sales_data = {
        'sale_id': range(1, 21),
        'customer_id': [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            1, 3, 5, 7, 9, 2, 4, 6, 8, 10
        ],
        'product_id': [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            5, 4, 3, 2, 1, 10, 9, 8, 7, 6
        ],
        'quantity': [
            1, 2, 1, 3, 1, 2, 1, 1, 2, 1,
            2, 1, 3, 1, 1, 2, 1, 2, 1, 3
        ],
        'sale_date': [
            '2023-01-15', '2023-01-20', '2023-02-05', '2023-02-10', '2023-02-15',
            '2023-03-01', '2023-03-10', '2023-03-15', '2023-03-20', '2023-04-01',
            '2023-04-05', '2023-04-10', '2023-04-15', '2023-04-20', '2023-05-01',
            '2023-05-05', '2023-05-10', '2023-05-15', '2023-05-20', '2023-06-01'
        ]
    }
    
    # Convert to DataFrames
    customers_df = pd.DataFrame(customers_data)
    products_df = pd.DataFrame(products_data)
    sales_df = pd.DataFrame(sales_data)
    
    # Save to database
    customers_df.to_sql('customers', conn, index=False, if_exists='replace')
    products_df.to_sql('products', conn, index=False, if_exists='replace')
    sales_df.to_sql('sales', conn, index=False, if_exists='replace')
    
    conn.close()
    
    return {
        "status": "success",
        "message": f"Sample database created at {db_path}",
        "tables": ["customers", "products", "sales"]
    }