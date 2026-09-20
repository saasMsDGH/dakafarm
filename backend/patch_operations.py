import re

filepath = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/backend/app/api/v1/reports/service/operations.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix MedicationRecord
content = content.replace('MedicationRecord.cost', 'MedicationRecord.total_cost')
content = content.replace('MedicationRecord.medication_date', 'MedicationRecord.record_date')

# Fix VaccinationRecord
content = content.replace('VaccinationRecord.cost', 'VaccinationRecord.total_cost')
content = content.replace('VaccinationRecord.vaccination_date', 'VaccinationRecord.record_date')

# Fix ProductionRecord
content = content.replace('ProductionRecord.quantity', 'ProductionRecord.total_eggs')
content = content.replace('ProductionRecord.production_date', 'ProductionRecord.record_date')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Models attributes fixed")
