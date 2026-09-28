# Business ERD

```mermaid
erDiagram
    CUSTOMERS ||--o{ SALES : makes
    SALES ||--|{ SALE_ITEMS : includes
    PRODUCTS ||--o{ SALE_ITEMS : sold_as
    SALES ||--o{ PAYMENTS : paid_via

    SUPPLIERS ||--o{ PURCHASES : supplies
    PURCHASES ||--|{ PURCHASE_ITEMS : includes
    PRODUCTS ||--o{ PURCHASE_ITEMS : bought_as
    PURCHASES ||--o{ PURCHASE_PAYMENTS : paid_via
```
