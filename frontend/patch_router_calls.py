import os

filepath = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/backend/app/api/v1/reports/router/financial.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Cash book
content = content.replace(
    'return await FinancialReportService.get_book_report(\n        db, account_id, params, date_from=date_from, date_to=date_to,\n        transaction_type=transaction_type, direction=direction,\n    )',
    'return await FinancialReportService.get_book_report(\n        db, account_id, params, date_from=date_from, date_to=date_to,\n        transaction_type=transaction_type, direction=direction, account_type=\"CASH\"\n    )',
    1
)

# Bank book
content = content.replace(
    'return await FinancialReportService.get_book_report(\n        db, account_id, params, date_from=date_from, date_to=date_to,\n        transaction_type=transaction_type, direction=direction,\n    )',
    'return await FinancialReportService.get_book_report(\n        db, account_id, params, date_from=date_from, date_to=date_to,\n        transaction_type=transaction_type, direction=direction, account_type=\"BANK\"\n    )',
    1
)

# Mobile book
content = content.replace(
    'return await FinancialReportService.get_book_report(\n        db, account_id, params, date_from=date_from, date_to=date_to,\n        transaction_type=transaction_type, direction=direction,\n    )',
    'return await FinancialReportService.get_book_report(\n        db, account_id, params, date_from=date_from, date_to=date_to,\n        transaction_type=transaction_type, direction=direction, account_type=\"MOBILE_MONEY\"\n    )',
    1
)


with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Router calls updated")
