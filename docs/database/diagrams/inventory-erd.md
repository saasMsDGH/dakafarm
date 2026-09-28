# Inventory ERD

```mermaid
erDiagram
    PRODUCT_CATEGORIES ||--o{ PRODUCTS : contains
    PRODUCTS ||--o{ STOCK_MOVEMENTS : tracks
```
