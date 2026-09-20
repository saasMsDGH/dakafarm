import asyncio
from sqlalchemy import text
from app.core.database import sessionlocal

async def wipe_and_seed():
    async with sessionlocal() as db:
        print("Wiping data...")
        tables_to_truncate = [
            "asset_distributions", "asset_payments", "assets", "customers", 
            "employees", "expense_payments", "expenses", "feed_records", 
            "financial_transactions", "financial_accounts", "flocks", "houses", 
            "medication_records", "mortality_records", "payments", 
            "payroll_payments", "payrolls", "product_categories", 
            "production_records", "products", "purchase_items", 
            "purchase_payments", "purchases", "sale_items", "sales", 
            "stock_movements", "suppliers", "vaccination_records"
        ]
        
        await db.execute(text(f"TRUNCATE TABLE {', '.join(tables_to_truncate)} RESTART IDENTITY CASCADE;"))
        await db.commit()
        print("Data wiped!")

        print("Seeding new data...")
        # 1. Accounts
        await db.execute(text("""
            INSERT INTO financial_accounts (name, account_type, bank_name, account_number, opening_balance, is_active, created_at, updated_at) VALUES
            ('Cash Account', 'cash', '', '', 2000000, true, '2026-09-01 08:00:00', '2026-09-01 08:00:00'),
            ('Bank Account', 'bank', 'NMB Bank', '00112233', 10000000, true, '2026-09-01 08:00:00', '2026-09-01 08:00:00'),
            ('Vodacom M-Pesa', 'mobile', 'Vodacom', '0755000000', 3000000, true, '2026-09-01 08:00:00', '2026-09-01 08:00:00'),
            ('Tigo Pesa', 'mobile', 'Tigo', '0711000000', 1500000, true, '2026-09-01 08:00:00', '2026-09-01 08:00:00');
        """))
        
        # 2. Farm Setup
        await db.execute(text("""
            INSERT INTO houses (name, location, capacity, status, created_at) VALUES
            ('Broiler House A', 'Sector 1', 5000, true, '2026-09-01 08:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO flocks (flock_code, house_id, breed, initial_quantity, current_quantity, arrival_date, status, created_at) VALUES
            ('FLK-001', 1, 'Lohmann Brown', 1000, 995, '2026-09-01', true, '2026-09-01 08:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO production_records (flock_id, record_date, total_birds, total_eggs, damaged_eggs, good_eggs, laying_percentage, created_at) VALUES
            (1, '2026-09-10', 995, 955, 5, 950, 95.9, '2026-09-10 10:00:00'),
            (1, '2026-09-11', 995, 962, 2, 960, 96.6, '2026-09-11 10:00:00'),
            (1, '2026-09-12', 995, 959, 4, 955, 96.3, '2026-09-12 10:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO mortality_records (flock_id, record_date, quantity, cause, created_at) VALUES
            (1, '2026-09-05', 2, 'Natural', '2026-09-05 14:00:00'),
            (1, '2026-09-15', 3, 'Illness', '2026-09-15 14:00:00');
        """))

        # 3. Inventory & Products
        await db.execute(text("""
            INSERT INTO product_categories (name, description, is_active, created_at) VALUES
            ('Poultry Feed', 'Feeds for chickens', true, '2026-09-01 08:00:00'),
            ('Eggs', 'Farm produce', true, '2026-09-01 08:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO products (category_id, name, unit_of_measure, unit_price, selling_price, current_stock, reorder_level, description, is_active, created_at) VALUES
            (1, 'Layers Mash (50kg)', 'bags', 60000, 65000, 50, 10, 'Quality layers feed', true, '2026-09-01 08:00:00'),
            (2, 'Tray of Eggs', 'trays', 8000, 12000, 150, 20, '30 eggs tray', true, '2026-09-01 08:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO stock_movements (product_id, movement_type, quantity, reference_type, reference_id, movement_date, created_at) VALUES
            (1, 'IN', 50, 'opening', NULL, '2026-09-01 09:00:00', '2026-09-01 09:00:00'),
            (2, 'IN', 150, 'opening', NULL, '2026-09-01 09:00:00', '2026-09-01 09:00:00');
        """))

        # 4. HR & Payroll
        await db.execute(text("""
            INSERT INTO employees (employee_code, first_name, last_name, position, phone, employment_date, status, created_at) VALUES
            ('EMP-001', 'John', 'Doe', 'Farm Worker', '0700000001', '2026-09-01', true, '2026-09-01 08:00:00'),
            ('EMP-002', 'Jane', 'Smith', 'Sales Rep', '0700000002', '2026-09-01', true, '2026-09-01 08:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO payrolls (employee_id, pay_period, basic_salary, allowances, deductions, net_salary, amount_paid, payment_date, payment_status, created_at) VALUES
            (1, 'Sep-2026', 300000, 10000, 0, 310000, 310000, '2026-09-15', 'paid', '2026-09-15 12:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO payroll_payments (payroll_id, account_id, payment_reference, amount, payment_method, payment_date, created_at) VALUES
            (1, 2, 'PR-001', 310000, 'bank', '2026-09-15 12:00:00', '2026-09-15 12:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO financial_transactions (account_id, transaction_date, transaction_type, direction, amount, description, reference_number, created_at) VALUES
            (2, '2026-09-15 12:00:00', 'PAYROLL', 'OUT', 310000, 'Salary Payment John Doe', 'PR-001', '2026-09-15 12:00:00');
        """))

        # 5. POS Sales
        await db.execute(text("""
            INSERT INTO customers (customer_code, name, business_type, phone, email, address, credit_limit, created_at) VALUES
            ('CUST-001', 'Retail Shopper', 'retail', '0000000000', '', '', 0, '2026-09-01 08:00:00'),
            ('CUST-002', 'Local Shop', 'wholesale', '0711111111', 'shop@local.com', 'Town Center', 120000, '2026-09-01 08:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO sales (invoice_number, customer_id, sale_date, subtotal, discount, total_amount, amount_paid, payment_status, created_at) VALUES
            ('INV-001', 2, '2026-09-05', 120000, 0, 120000, 120000, 'paid', '2026-09-05 10:30:00');
        """))
        
        await db.execute(text("""
            INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total_amount) VALUES
            (1, 2, 10, 12000, 120000);
        """))
        
        await db.execute(text("""
            INSERT INTO payments (sale_id, receipt_number, amount, payment_method, payment_date, created_at) VALUES
            (1, 'REC-001', 120000, 'cash', '2026-09-05 10:30:00', '2026-09-05 10:30:00');
        """))
        
        await db.execute(text("""
            INSERT INTO financial_transactions (account_id, transaction_date, transaction_type, direction, amount, description, reference_number, created_at) VALUES
            (1, '2026-09-05 10:30:00', 'SALE', 'IN', 120000, 'Sale Payment INV-001', 'REC-001', '2026-09-05 10:30:00');
        """))
        
        await db.execute(text("""
            INSERT INTO stock_movements (product_id, movement_type, quantity, reference_type, reference_id, movement_date, created_at) VALUES
            (2, 'OUT', 10, 'SALE', 1, '2026-09-05 10:30:00', '2026-09-05 10:30:00');
        """))
        
        # 6. Purchases & Expenses
        await db.execute(text("""
            INSERT INTO suppliers (supplier_code, name, contact_person, phone, email, address, created_at) VALUES
            ('SUP-001', 'Agro Vet Supplies', 'Mr. Vet', '0722222222', 'vet@agro.com', 'City Center', '2026-09-01 08:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO purchases (purchase_number, supplier_id, purchase_date, subtotal, discount, total_amount, amount_paid, payment_status, notes, created_at) VALUES
            ('PUR-001', 1, '2026-09-02', 600000, 0, 600000, 600000, 'paid', 'Feed stock', '2026-09-02 11:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO purchase_items (purchase_id, product_id, quantity, unit_cost, total_amount) VALUES
            (1, 1, 10, 60000, 600000);
        """))
        
        await db.execute(text("""
            INSERT INTO purchase_payments (purchase_id, payment_reference, amount, payment_method, payment_date, created_at) VALUES
            (1, 'PP-001', 600000, 'bank', '2026-09-02 11:00:00', '2026-09-02 11:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO financial_transactions (account_id, transaction_date, transaction_type, direction, amount, description, reference_number, created_at) VALUES
            (2, '2026-09-02 11:00:00', 'PURCHASE', 'OUT', 600000, 'Purchase Payment PUR-001', 'PP-001', '2026-09-02 11:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO stock_movements (product_id, movement_type, quantity, reference_type, reference_id, movement_date, created_at) VALUES
            (1, 'IN', 10, 'PURCHASE', 1, '2026-09-02 11:00:00', '2026-09-02 11:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO expenses (expense_number, category, description, amount, amount_paid, payment_status, expense_date, payment_method, created_at) VALUES
            ('EXP-001', 'Utilities', 'Electricity Bill Sep', 50000, 50000, 'paid', '2026-09-08', 'mobile', '2026-09-08 09:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO expense_payments (expense_id, account_id, payment_reference, amount, payment_method, payment_date, created_at) VALUES
            (1, 3, 'LUKU-123', 50000, 'mobile', '2026-09-08 09:00:00', '2026-09-08 09:00:00');
        """))
        
        await db.execute(text("""
            INSERT INTO financial_transactions (account_id, transaction_date, transaction_type, direction, amount, description, reference_number, created_at) VALUES
            (3, '2026-09-08 09:00:00', 'EXPENSE', 'OUT', 50000, 'Electricity Bill Sep', 'LUKU-123', '2026-09-08 09:00:00');
        """))

        await db.commit()
        print("Data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(wipe_and_seed())
