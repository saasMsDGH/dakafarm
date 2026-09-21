import sys
import os
import json
sys.path.insert(0, os.path.abspath('d:/myprojects/AMAS FARM/AMAS-FARM-Management-System/backend'))

from app.core.database import Base

import app.api.v1.user.models
import app.api.v1.farm.models.house
import app.api.v1.farm.models.flock
import app.api.v1.farm.models.medication_record
import app.api.v1.farm.models.vaccination_record
import app.api.v1.farm.models.production_record
import app.api.v1.farm.models.mortality_record
import app.api.v1.farm.models.feed_record
import app.api.v1.inventory.models.product_category
import app.api.v1.inventory.models.product
import app.api.v1.inventory.models.stock_movement
import app.api.v1.pos.models.customer
import app.api.v1.pos.models.sale
import app.api.v1.pos.models.supplier
import app.api.v1.pos.models.purchase
import app.api.v1.pos.models.expense
import app.api.v1.pos.models.payment
import app.api.v1.pos.models.purchase_payment
import app.api.v1.pos.models.expense_payment
import app.api.v1.hr.models.employee
import app.api.v1.hr.models.payroll
import app.api.v1.hr.models.payroll_payment
import app.api.v1.assets.models.asset
import app.api.v1.assets.models.asset_payment
import app.api.v1.finance.models.account
import app.api.v1.finance.models.transaction

output = {}
for table_name, table in Base.metadata.tables.items():
    t_info = {
        "name": table.name,
        "columns": [],
        "fks": [],
        "indexes": [],
    }
    for col in table.columns:
        c_info = {
            "name": col.name,
            "type": str(col.type),
            "nullable": col.nullable,
            "primary_key": col.primary_key,
            "default": str(col.default.arg) if col.default else None,
            "server_default": str(col.server_default.arg) if col.server_default else None,
            "unique": col.unique
        }
        t_info["columns"].append(c_info)
    
    for fk in table.foreign_keys:
        t_info["fks"].append({
            "column": fk.parent.name,
            "target": fk.target_fullname,
            "ondelete": fk.ondelete,
            "onupdate": fk.onupdate
        })
        
    for idx in table.indexes:
        t_info["indexes"].append({
            "name": idx.name,
            "unique": idx.unique,
            "columns": [c.name for c in idx.columns]
        })
        
    output[table_name] = t_info

print(json.dumps(output, indent=2))
