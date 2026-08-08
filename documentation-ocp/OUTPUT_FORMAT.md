# OUTPUT FORMAT SPECIFICATION
## Excel Report Structure and Data Format (Current System)

---

## TABLE OF CONTENTS
1. [Excel File Structure](#excel-file-structure)
2. [Sheet Specifications](#sheet-specifications)
3. [Data Format Requirements](#data-format-requirements)
4. [Validation Rules](#validation-rules)
5. [Example Output Values](#example-output-values)

---

## EXCEL FILE STRUCTURE

### File Naming Convention
```python
EXCEL_FILE_FORMAT = "hybrid_optimization_results_{timestamp}.xlsx"
# Example: hybrid_optimization_results_20250719_143022.xlsx

REQUIRED_SHEETS = [
    "Demand Delivery",         # Sheet 1: Consumer analysis with acid breakdown
    "Phosphoric Production",   # Sheet 2: P29 and P54 production details
    "Acid 29 Stocks",         # Sheet 3: P29 stock movements and mass balance
    "Acid 54 Stocks",         # Sheet 4: P54 stock movements and mass balance
    "Central Storage Stocks"   # Sheet 5: IR11 and IR12 operations
]
```

---

## SHEET SPECIFICATIONS

### Sheet 1: "Demand Delivery"
```python
DEMAND_DELIVERY_SHEET = {
    "title": "DEMAND & DELIVERY ANALYSIS",
    "columns": [
        "Line",                                    # Consumer/fertilizer line name
        "Products",                               # Fertilizer products with quantities
        "Acid Needed (Amount)",                   # Required acid by type with amounts
        "Acid Planned (Total Received & Source)"  # Delivered acid with source tracking
    ],
    
    "data_structure": {
        "consumer_order": ["U16", "U116A", "U116BC", "IMACID", "EMAPHOS", "MAPS", "U53", "107DEF", "JFC1-5"],
        "products_format": "ProductName (QuantityT)\nProductName2 (QuantityT)",
        "acid_needed_format": "acid_type: amount.1ft\nacid_type2: amount.1ft",
        "acid_planned_format": "acid_type: amount.1ft (from SourceLine)\nacid_type2: amount.1ft (from IR11/IR12)"
    },
    
    "data_example": {
        "Line": "U16",
        "Products": "DAP_STANDARD (3057t)\nTSP_EURO (1200t)",
        "Acid Needed (Amount)": "acid_29_std: 1607.1t\nacid_54_ncl: 1449.9t\nacid_54_dec_total: 453.1t",
        "Acid Planned (Total Received & Source)": "acid_29_std: 1607.1t (from 13AB,13CD)\nCoC: 453.1t (from IR11)\nacid_54_ncl: 1449.9t (from 14XY,14CD)"
    },
    
    "formatting": {
        "text_wrap": True,
        "vertical_alignment": "top",
        "auto_column_width": True,
        "line_separation": "\\n for multi-line content"
    }
}
```

### Sheet 2: "Phosphoric Production"
```python
PHOSPHORIC_PRODUCTION_SHEET = {
    "p29_section": {
        "title": "P29 ACID PRODUCTION",
        "start_row": 1,
        "columns": [
            "Line",                     # 13AB, 13CD, 13XY, 13ZU, 13E, 13F
            "Total Production",         # Fixed daily production (tonnes)
            "Standard Production",      # Standard acid produced
            "Decadmiated Production",   # Decadmiated acid produced (0, 750, or 1500)
            "Initial Stock STD",        # Starting standard acid inventory
            "Initial Stock DEC",        # Starting decadmiated acid inventory  
            "STD to Concentration",     # Standard acid sent to P54 concentration
            "DEC to Concentration",     # Decadmiated acid sent to P54 concentration
            "STD to Fertilizer",        # Standard acid delivered to consumers
            "DEC to Fertilizer"         # Decadmiated acid delivered to consumers
        ]
    },
    
    "p54_section": {
        "title": "P54 ACID PRODUCTION", 
        "start_row": "After P29 section + 3 rows",
        "columns": [
            "Line",                     # 14AB, 14CD, 14XY, 14ZU, 14EXT
            "Total Production",         # NCL acid production from concentration
            "Initial Stock NCL",        # Starting NCL inventory
            "NCL to Clarification",     # NCL sent for manual clarification
            "NCL to Cocrystallization", # NCL sent for systematic co-crystallization
            "NCL to Fertilizer"         # NCL delivered directly to consumers
        ]
    }
}
```

### Sheet 3: "Acid 29 Stocks"
```python
ACID29_STOCKS_SHEET = {
    "title": "ACID 29% STOCK MOVEMENTS & MASS BALANCE",
    "columns": [
        "Line",                       # P29 line identifier (13AB, 13CD, etc.)
        "Acid Type",                 # acid_29_std or acid_29_dec
        "Initial Stock",             # Starting inventory (tonnes)
        "Production",                # Daily production (tonnes)
        "Transfers In",              # From other lines (tonnes)
        "Transfers Out",             # To other lines (tonnes)
        "Sludge Returns",            # Sludge returns from processing (tonnes)
        "To Concentration",          # Sent to P54 production (tonnes)
        "Delivery Out (Planned)",    # Planned delivery to consumers (tonnes)
        "Delivery Out (Actual)",     # Actual delivery after stock adjustment (tonnes)
        "Delivery Shortfall",        # Shortfall due to insufficient stock (tonnes)
        "Final Stock",               # Ending inventory (tonnes)
        "Stock Violation"            # True if stock went negative (boolean)
    ],
    
    "data_structure": [
        # One row for each line and acid type combination
        {"Line": "13AB", "Acid Type": "acid_29_std", ...},
        {"Line": "13AB", "Acid Type": "acid_29_dec", ...},
        {"Line": "13CD", "Acid Type": "acid_29_std", ...},
        # ... continue for all lines and types
    ],
    
    "mass_balance_validation": {
        "formula": "Initial + Production + Transfers_In + Sludge_Returns = Transfers_Out + To_Concentration + Actual_Delivery + Final_Stock",
        "stock_constraint": "Final_Stock >= 0 (violations tracked)"
    }
}
```

### Sheet 4: "Acid 54 Stocks"  
```python
ACID54_STOCKS_SHEET = {
    "title": "ACID 54% STOCK MOVEMENTS & MASS BALANCE",
    "columns": [
        "Line",                      # P54 line identifier (14AB, 14CD, etc.)
        "Initial Stock",             # Starting NCL inventory (tonnes)
        "Production",                # NCL production from concentration (tonnes)
        "Sludge Returns",            # CoC sludge returns to NCL stock (tonnes)
        "Systematic CoC Out",        # NCL sent to systematic co-crystallization (tonnes)
        "Manual Clarification Out",  # NCL sent to manual clarification (tonnes)
        "Delivery Out (Planned)",    # Planned NCL delivery to consumers (tonnes)
        "Delivery Out (Actual)",     # Actual NCL delivery after stock adjustment (tonnes)
        "Delivery Shortfall",        # Shortfall due to insufficient stock (tonnes)
        "Final Stock",               # Ending NCL inventory (tonnes)
        "Stock Violation"            # True if stock went negative (boolean)
    ],
    
    "data_structure": [
        # One row per P54 line (only NCL type stored locally)
        {"Line": "14AB", "Initial Stock": 901.1, ...},
        {"Line": "14CD", "Initial Stock": 369.0, ...},
        # ... continue for all P54 lines
    ],
    
    "special_notes": {
        "sludge_source": "20% of co-crystallization input returns as sludge to NCL stock",
        "no_dec_cl_storage": "Decadmiated clarified acid goes directly to IR11 (no local storage)",
        "systematic_coc": "Systematic co-crystallization processes ALL available NCL from enabled echelons"
    }
}
```

### Sheet 5: "Central Storage Stocks"
```python
CENTRAL_STORAGE_SHEET = {
    "title": "CENTRAL STORAGE OPERATIONS (IR11 & IR12)",
    "columns": [
        "Storage",                   # IR11 or IR12
        "Acid Types",               # CoC + DEC_CL (IR11) or CL (IR12)
        "Initial Stock",            # Starting inventory (tonnes)
        "CoC Input",                # Co-crystallized acid input (IR11 only)
        "DEC_CL Input",             # Decadmiated clarified acid input (IR11 only)
        "CL Input",                 # Clarified acid input (IR12 only, shows in separate column)
        "Total Input",              # Sum of all inputs
        "Deliveries (Planned)",     # Planned deliveries to consumers (tonnes)
        "Deliveries (Actual)",      # Actual deliveries after stock adjustment (tonnes)
        "Delivery Shortfall",       # Shortfall due to insufficient stock (tonnes)
        "Final Stock",              # Ending inventory (tonnes)
        "Stock Violation"           # True if stock went negative (boolean)
    ],
    
    "data_structure": [
        {
            "Storage": "IR11",
            "Acid Types": "CoC + DEC_CL",
            "Initial Stock": 5500.8,  # From get_vol_54_IR11(9.38)
            "CoC Input": "Systematic co-crystallization output",
            "DEC_CL Input": "Automatic decadmiated clarification output",
            "CL Input": 0,
            "Total Input": "CoC + DEC_CL",
            "capacity": 6378.4        # get_vol_54_IR11(10.80)
        },
        {
            "Storage": "IR12", 
            "Acid Types": "CL",
            "Initial Stock": 4004.1,  # From get_vol_54_IR12(9.14)
            "CoC Input": 0,
            "DEC_CL Input": 0,
            "CL Input": "Manual clarification output",
            "Total Input": "CL only",
            "capacity": 4804.3        # get_vol_54_IR12(10.80)
        }
    ]
}
```

---

## DATA FORMAT REQUIREMENTS

### Number Formatting
```python
DATA_FORMATTING = {
    "tonnes": {
        "decimal_places": 1,
        "example": 1234.5,
        "zero_display": 0.0
    },
    
    "percentages": {
        "decimal_places": 1,
        "example": 85.3,
        "format": "##.#%"
    },
    
    "boolean_values": {
        "stock_violation": "True/False",
        "optimization_status": "Optimal/Infeasible/Unbounded"
    }
}
```

### Text Formatting
```python
TEXT_FORMATTING = {
    "multi_line_cells": {
        "separator": "\\n",
        "wrap_text": True,
        "vertical_align": "top",
        "example": "DAP_STANDARD (3057t)\\nTSP_EURO (1200t)"
    },
    
    "acid_breakdown": {
        "format": "acid_type: amount.1ft",
        "example": "acid_29_std: 1607.1t\\nacid_54_dec_total: 453.1t"
    },
    
    "source_tracking": {
        "local_sources": "13AB,13CD,13XY", 
        "central_sources": "IR11" or "IR12",
        "example": "acid_54_cl: 250.0t (from IR12)"
    }
}
```

---

## VALIDATION RULES

### Data Consistency Checks
```python
VALIDATION_RULES = {
    "mass_balance_tolerance": 0.001,      # 0.1% tolerance for mass balance
    "stock_constraint": "All final stocks >= 0 (violations tracked but allowed)",
    "delivery_adjustment": "Actual delivery <= planned delivery (due to stock constraints)",
    
    "required_totals": {
        "total_acid_delivered": "Sum of all actual consumer deliveries",
        "total_p29_production": "Sum of all P29 line production", 
        "total_p54_production": "Sum of all P54 NCL production"
    },
    
    "consistency_checks": [
        "P29: Initial + Production + Transfers_In + Sludge = Transfers_Out + Concentration + Delivery + Final",
        "P54: Initial + Production + Sludge = CoC + Clarification + Delivery + Final",
        "Central: Initial + Input = Delivery + Final",
        "Stock violations are tracked but system continues with adjusted deliveries"
    ]
}
```

### Stock Violation Handling
```python
STOCK_VIOLATION_SYSTEM = {
    "detection": "Final stock < 0 after mass balance calculation",
    "correction": "Reduce actual delivery to prevent negative stock",
    "tracking": "Log delivery shortfall = planned_delivery - actual_delivery",
    "reporting": "Mark Stock Violation = True in relevant sheet",
    "objective": "System continues optimization with realistic delivery amounts"
}
```

---

## EXAMPLE OUTPUT VALUES

### Sample Sheet 1 Data (Demand Delivery)
```python
EXAMPLE_DEMAND_DELIVERY = {
    "U16": {
        "Products": "DAP_STANDARD (3057t)\\nTSP_EURO (1200t)",
        "Acid Needed": "acid_29_std: 1607.1t\\nacid_54_ncl: 1449.9t\\nacid_54_dec_total: 453.1t",
        "Acid Planned": "acid_29_std: 1607.1t (from 13AB,13CD)\\nCoC: 453.1t (from IR11)\\nacid_54_ncl: 1449.9t (from 14XY,14CD)"
    },
    "EMAPHOS": {
        "Products": "Direct",
        "Acid Needed": "acid_54_ncl: 700.0t", 
        "Acid Planned": "acid_54_ncl: 700.0t (from 14ZU,14XY,14AB)"
    }
}
```

### Sample Sheet 3 Data (Acid 29 Stocks)
```python
EXAMPLE_P29_STOCKS = {
    "13AB_acid_29_std": {
        "Line": "13AB",
        "Acid Type": "acid_29_std",
        "Initial Stock": 790.2,
        "Production": 1500.0,
        "Transfers In": 0.0,
        "Transfers Out": 0.0,
        "Sludge Returns": 87.5,    # From EMAPHOS ARP1
        "To Concentration": 1200.0,
        "Delivery Out (Planned)": 500.0,
        "Delivery Out (Actual)": 500.0,
        "Delivery Shortfall": 0.0,
        "Final Stock": 677.7,
        "Stock Violation": False
    }
}
```

### Sample Sheet 5 Data (Central Storage)
```python
EXAMPLE_CENTRAL_STORAGE = {
    "IR11": {
        "Storage": "IR11",
        "Acid Types": "CoC + DEC_CL", 
        "Initial Stock": 5500.8,
        "CoC Input": 1600.0,       # From systematic co-crystallization
        "DEC_CL Input": 135.0,     # From automatic decadmiation clarification
        "CL Input": 0.0,
        "Total Input": 1735.0,
        "Deliveries (Planned)": 800.0,
        "Deliveries (Actual)": 800.0,
        "Delivery Shortfall": 0.0,
        "Final Stock": 6435.8,
        "Stock Violation": False
    }
}
```

---

## CURRENT SYSTEM CHARACTERISTICS

### Key Features
1. **5-Sheet Structure**: Focused on essential production and stock tracking
2. **Stock Violation Handling**: System continues with adjusted deliveries instead of failing
3. **Mass Balance Tracking**: Complete input/output accounting for all acid types
4. **Source Tracking**: Detailed breakdown of where each acid type comes from
5. **Real-time Adjustment**: Actual vs planned delivery tracking

### Excel Generation Features
```python
EXCEL_FEATURES = {
    "auto_column_width": "Columns automatically adjust to content",
    "text_wrapping": "Multi-line content properly wrapped and aligned",
    "calculation_transparency": "All mass balance components visible",
    "violation_tracking": "Stock violations clearly marked but not blocking",
    "source_attribution": "Each delivery linked to specific source line or storage"
}
```

---

**This output format specification reflects the actual current system implementation as of 2025. Any AI implementation must generate Excel files following this precise 5-sheet structure with complete mass balance tracking and stock violation handling.**