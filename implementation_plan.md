# Redesign Paint Store Database Schema

Redesign the backend database to accurately classify paint products (Emulsion, Enamel, Distemper, Primer) with a scalable, maintainable schema that supports future product categories (hardware items, putty, thinner, etc.).

## Design Decisions (Agreed Upon)

| Decision | Choice |
|---|---|
| Table strategy | **Option B** — Single unified `product` table with nullable category-specific columns |
| Dimension storage | **Lookup tables** for `brand` and `category`; **VARCHAR** for finish, quality, surface, chemistry, specialty |
| Pack size | `pack_size_value DECIMAL` + `pack_size_unit VARCHAR` (supports L, KG, and future "units" for hardware) |
| Color tracking | **Base shades only** (what's physically on shelf) |
| Emulsion finish | **Not tracked separately** — embedded in series name |
| Enamel surface | **Not tracked separately** — enamel is for Metal & Wood by definition |
| Scalability | Category table is open-ended; product columns are generic enough to accommodate new types |

## Proposed Changes

### Backend Module

---

#### [MODIFY] [database.py](file:///d:/caffeine_nights/backend/database.py)

Complete rewrite of the [init_db()](file:///d:/caffeine_nights/backend/database.py#16-118) function with the new schema:

**Table: `brand`** (unchanged)
- `brand_id INT AUTO_INCREMENT PK`
- `brand_name VARCHAR(100) NOT NULL UNIQUE`

**Table: `category`** (unchanged)
- `category_id INT AUTO_INCREMENT PK`
- `category_name VARCHAR(50) NOT NULL UNIQUE`

**Table: `product`** (redesigned)
- `product_id INT AUTO_INCREMENT PK`
- `brand_id INT FK → brand`
- `category_id INT FK → category`
- `series_name VARCHAR(250) NOT NULL` — e.g., "Silk Glamor", "Apcolite Premium", "Tractor UNO"
- `surface_type VARCHAR(100)` — e.g., Interior, Exterior, Wall/Masonry, Wood, Metal (Red Oxide)
- `chemistry VARCHAR(100)` — e.g., Synthetic/Alkyd (Oil-Based), Acrylic, Water-Based
- `quality_tier VARCHAR(50)` — e.g., Luxury, Premium, Economy, Standard
- `finish_type VARCHAR(100)` — e.g., High Gloss, Satin, Matt, Smooth Matte (primarily for Enamel/Distemper)
- `specialty VARCHAR(100)` — e.g., PU, Epoxy, Rustshield, UNO, OBD
- `formulation VARCHAR(100)` — e.g., Acrylic, Vinyl (primarily for Emulsion)
- `UNIQUE KEY (brand_id, category_id, series_name, quality_tier, finish_type)` — prevents duplicates

**Table: `inventory`** (enhanced)
- `sku_id INT AUTO_INCREMENT PK`
- `product_id INT FK → product`
- `base_color VARCHAR(150) NOT NULL`
- `pack_size_value DECIMAL(10,2)` — e.g., 1, 4, 10, 20
- `pack_size_unit VARCHAR(10)` — e.g., "L", "KG", "UNIT" (future-proof)
- `quantity INT DEFAULT 0`
- `price_cp DECIMAL(10,2)` — cost price
- `price_sp DECIMAL(10,2)` — selling price
- `min_stock_alert INT DEFAULT 3`
- `UNIQUE (product_id, base_color, pack_size_value, pack_size_unit)` — prevents duplicate SKUs

Also fixes the existing typo: `IntegrityErrors` → `IntegrityError` (line 114).

---

#### [MODIFY] [constants.py](file:///d:/caffeine_nights/backend/constants.py)

Replace with corrected, research-validated domain constants:

```python
# Categories
CATEGORIES = ['Emulsion', 'Enamel', 'Distemper', 'Primer']

# Brands
BRANDS = ['Asian Paints', 'Berger Paints', 'Nerolac', 'Indigo Paints']

# Surface types (per category context)
SURFACE_TYPES = ['Interior', 'Exterior', 'Wall/Masonry', 'Wood', 'Metal (Red Oxide)', 'Metal (Zinc Chromate)']

# Chemistry / Base
CHEMISTRY_TYPES = ['Synthetic/Alkyd (Oil-Based)', 'Water-Based (Acrylic Enamel)', 'Acrylic', 'Vinyl']

# Quality tiers
QUALITY_TIERS = ['Luxury', 'Premium', 'Economy', 'Standard']

# Finish types (Enamel & Distemper)
FINISH_TYPES = ['High Gloss', 'Satin', 'Matt', 'Smooth Matte', 'Soft Sheen']

# Specialty variants
SPECIALTIES = ['Standard', 'PU', 'Epoxy', 'Rustshield', 'UNO', 'OBD']

# Formulations (Emulsion)
FORMULATIONS = ['Acrylic', 'Vinyl']

# Pack size units
PACK_SIZE_UNITS = ['L', 'KG']

# Common pack sizes
COMMON_PACK_SIZES = {
    'L': [0.2, 0.5, 1, 4, 10, 20],
    'KG': [1, 2, 5, 10, 20]
}

# Base colors
BASE_COLORS = ['White Base', 'P0 Base', 'P1 Base', 'N2 Base', 'Yellow Base', 'Red Base', 'Brown Base']
```

## Verification Plan

### Automated Tests

1. **Run the init script** and verify tables are created correctly:
```bash
cd d:\caffeine_nights
python -m backend.database
```
Then verify in MySQL CLI:
```sql
USE kapoorpainthardware_db;
SHOW TABLES;
DESCRIBE brand;
DESCRIBE category;
DESCRIBE product;
DESCRIBE inventory;
SELECT * FROM category;
SELECT * FROM brand;
```

2. **Test unique constraint works** by attempting to insert a duplicate product — should raise `IntegrityError`.

### Manual Verification
- The user can visually confirm the `DESCRIBE` output matches the planned schema.
- The user confirms the seeded `category` and `brand` rows are correct.
