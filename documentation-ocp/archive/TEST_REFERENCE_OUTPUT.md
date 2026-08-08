# TEST REFERENCE & EXCEL OUTPUT STRUCTURE
## Exact Test System Example and Expected Output Format

---

## TABLE OF CONTENTS
1. [Test System Reference Data](#test-system-reference-data)
2. [Expected Optimization Results](#expected-optimization-results)
3. [Excel Output Structure](#excel-output-structure)
4. [Validation Numbers](#validation-numbers)
5. [Success Criteria](#success-criteria)

---

## TEST SYSTEM REFERENCE DATA

### Input Parameters (Exact Test Values)
```python
# P29 Production (Fixed - Cannot Change)
P29_PRODUCTION_TEST = {
    '13AB': 1198,   # tonnes/day
    '13CD': 1530,   # tonnes/day
    '13XY': 1427,   # tonnes/day
    '13ZU': 1479,   # tonnes/day
    '13E': 1642,    # tonnes/day
    '13F': 1430     # tonnes/day
}
# Total P29 Production: 8,706 tonnes/day

# Initial Stock Levels (from tank height measurements in meters)
INITIAL_STOCK_HEIGHTS_TEST = {
    # P29 tank heights (meters) - use get_vol_29(height) to convert to tonnes
    'P29_heights': {
        '13AB': 11.10,  # meters → get_vol_29(11.10) = 637.8 tonnes standard
        '13CD': 11.10,  # meters → get_vol_29(11.10) = 637.8 tonnes standard
        '13XY': 6.70,   # meters → get_vol_29(6.70) = 385.0 tonnes standard
        '13ZU': 7.90,   # meters → get_vol_29(7.90) = 453.9 tonnes standard
        '13E': 12.40,   # meters → get_vol_29(12.40) = 712.5 tonnes standard
        '13F': 8.40     # meters → get_vol_29(8.40) = 482.4 tonnes standard
    },
    
    # P54 tank heights (meters) - use get_vol_54(height) to convert to tonnes
    'P54_heights': {
        '14AB': 16.62,  # meters → get_vol_54(16.62) = 1517.5 tonnes NCL
        '14CD': 12.88,  # meters → get_vol_54(12.88) = 1175.6 tonnes NCL
        '14XY': 7.56,   # meters → get_vol_54(7.56) = 690.0 tonnes NCL
        '14ZU': 3.67,   # meters → get_vol_54(3.67) = 335.0 tonnes NCL
        '14EXT': 10.55  # meters → get_vol_54(10.55) = 962.5 tonnes NCL
    },
    
    # Central storage heights (meters) - use get_vol_54(height) to convert to tonnes
    'central_storage_heights': {
        'IR11': 8.50,   # meters → get_vol_54(8.50) = 775.5 tonnes (CoC + DEC_CL)
        'IR12': 7.20    # meters → get_vol_54(7.20) = 657.0 tonnes (CL)
    }
}

# Converted stock levels (after applying conversion formulas)
INITIAL_STOCK_29_STD_TEST = {
    '13AB': 637.8,  # get_vol_29(11.10) - all initial stock is standard acid
    '13CD': 637.8,  # get_vol_29(11.10) - all initial stock is standard acid
    '13XY': 385.0,  # get_vol_29(6.70) - all initial stock is standard acid
    '13ZU': 453.9,  # get_vol_29(7.90) - all initial stock is standard acid
    '13E': 712.5,   # get_vol_29(12.40) - all initial stock is standard acid
    '13F': 482.4    # get_vol_29(8.40) - all initial stock is standard acid
}
# Total Initial P29 Standard Stock: 3,309.4 tonnes

INITIAL_STOCK_29_DEC_TEST = {
    '13AB': 0.0,    # No initial decadmiated stock
    '13CD': 0.0,    # No initial decadmiated stock
    '13XY': 0.0,    # No initial decadmiated stock
    '13ZU': 0.0,    # No initial decadmiated stock
    '13E': 0.0,     # No initial decadmiated stock
    '13F': 0.0      # No initial decadmiated stock
}
# Total Initial P29 Decadmiated Stock: 0.0 tonnes
# Total Initial P29 Stock: 3,309.4 tonnes (std + dec)

INITIAL_STOCK_54_NCL_TEST = {
    '14AB': 1517.5, # get_vol_54(16.62) = 1517.5 tonnes
    '14CD': 1175.6, # get_vol_54(12.88) = 1175.6 tonnes
    '14XY': 690.0,  # get_vol_54(7.56) = 690.0 tonnes
    '14ZU': 335.0,  # get_vol_54(3.67) = 335.0 tonnes
    '14EXT': 962.5  # get_vol_54(10.55) = 962.5 tonnes
}
# Total Initial P54 NCL Stock: 4,680.6 tonnes

INITIAL_CENTRAL_STORAGE_TEST = {
    'IR11': 775.5,  # get_vol_54(8.50) = 775.5 tonnes (CoC + DEC_CL)
    'IR12': 657.0   # get_vol_54(7.20) = 657.0 tonnes (CL)
}
# Total Initial Central Storage: 1,432.5 tonnes

# IMPORTANT: Use the height measurements as inputs and apply conversion formulas
# get_vol_29(height_meters) → tonnes for P29 tanks
# get_vol_54(height_meters) → tonnes for P54 tanks and central storage
```

### Demand Requirements (Exact Test Values)
```python
# Direct Acid Demand
ACID_DEMAND_TEST = {
    'IMACID': {'29_STD': 0},           # 0 tonnes
    'EMAPHOS': {'54_NCL': 700},        # 700 tonnes NCL acid
    'MAPS': {'29_STD': 0},             # 0 tonnes
    'U53': {'54_CL': 100},             # 100 tonnes CL acid from IR12
    '107DEF': {                        # Direct consumer with multiple types
        '29_STD': 200,                 # 200 tonnes standard P29
        '54_CL': 150,                  # 150 tonnes CL from IR12
        '54_COC': 100                  # 100 tonnes CoC from IR11
    },
    'JFC1-5': {'29_STD': 0}           # 0 tonnes
}
# Total Direct Acid Demand: 1,250 tonnes

# Fertilizer Production Demand
FERTILIZER_DEMAND_TEST = {
    'U16': {
        'MAP_11_52_SPECIAL': 4950,     # 4,950 tonnes MAP
        'DAP_EURO': 3655               # 3,655 tonnes DAP
    },
    'U116A': {
        'MAP_11_52_SPECIAL': 3630      # 3,630 tonnes MAP
    },
    'U116BC': {
        'NPK_14_18_18_6S_1B2O3_AFRIQUE': 4710  # 4,710 tonnes NPK
    }
}
# Total Fertilizer Demand: 16,945 tonnes

# Fertilizer Acid Requirements (calculated from quality profiles)
FERTILIZER_ACID_REQUIREMENTS = {
    'U16': {
        'MAP_11_52_SPECIAL': {'acid_29_std': 0.625 * 4950},  # = 3,093.75 tonnes
        'DAP_EURO': {'acid_29_dec': 0.756 * 3655}            # = 2,763.18 tonnes
    },
    'U116A': {
        'MAP_11_52_SPECIAL': {'acid_29_std': 0.625 * 3630}   # = 2,268.75 tonnes
    },
    'U116BC': {
        'NPK_14_18_18_6S_1B2O3_AFRIQUE': {'acid_54_dec_total': 0.513 * 4710}  # = 2,416.23 tonnes
    }
}
```

### Working Hours Configuration
```python
ECHELON_WORKING_HOURS_TEST = {
    # EXT echelons (all enabled for co-crystallization - 24h each)
    "E": 24, "F": 24, "G": 24, "H": 24,
    
    # AB echelons (I,J for CoC 24h; A,K,B,L for regular NCL)
    "I": 24, "J": 24,           # CoC echelons
    "A": 12.83, "K": 8, "B": 24, "L": 24,  # Regular NCL echelons
    
    # CD echelons (no co-crystallization)
    "C": 24, "M": 24, "D": 24, "N": 16,
    
    # XY echelons (no co-crystallization)
    "X": 24, "P": 24, "Y": 24, "Q": 24,
    
    # ZU echelons (no co-crystallization)
    "Z": 24, "R": 24, "U": 14, "S": 13.25, "V": 8, "W": 24
}
```

### Process Configuration (Test System Settings)
```python
# Decadmiation configuration for test system
DECADMIATION_CONFIG_TEST = {
    'enabled_lines': ['13AB', '13CD', '13XY', '13ZU', '13E', '13F'],  # All lines capable (default)
    'initial_dec_stock': {  # Starting with no decadmiated stock
        '13AB': 0.0, '13CD': 0.0, '13XY': 0.0, 
        '13ZU': 0.0, '13E': 0.0, '13F': 0.0
    },
    'levels_allowed': [0, 750, 1500],  # Possible decadmiation amounts per day
    'note': 'All lines can produce decadmiated acid if needed, starting with zero dec stock'
}

# Clarification configuration for test system  
CLARIFICATION_CONFIG_TEST = {
    'enabled_lines': ['14AB', '14CD', '14XY', '14ZU', '14EXT'],  # All P54 lines enabled (default)
    'capacity_per_line': 1000,      # tonnes/day max clarification per line
    'yield': 0.90,                  # 90% yield (10% sludge return to P29)
    'sludge_return_to': 'P29_standard_stock',  # Sludge returns as standard acid
    'note': 'All P54 lines have clarification capability in test system'
}

# Co-crystallization configuration for test system
COCRYSTALLIZATION_CONFIG_TEST = {
    'enabled_echelons': {
        'EXT': ['E', 'F', 'G', 'H'],     # All 4 echelons enabled for CoC
        'AB': ['I', 'J']                  # Only I,J echelons enabled (A,B,K,L regular NCL)
    },
    'disabled_lines': ['14CD', '14XY', '14ZU'],  # No CoC capability
    'yield': 0.80,                      # 80% yield (20% sludge return to NCL)
    'sludge_return_to': 'P54_NCL_stock', # Sludge returns as NCL acid
    'note': 'Only EXT (all echelons) and AB (I,J echelons) perform co-crystallization'
}
```

---

## EXPECTED OPTIMIZATION RESULTS

### Key Success Metrics from Test System
```python
# Expected results from successful optimization
EXPECTED_TEST_RESULTS = {
    "optimization_status": "Optimal",
    "objective_value": -8977.34733,  # Negative because we maximize (minimize negative)
    
    # Total acid flows
    "total_acid_delivered": 8977.34733,  # tonnes (matches objective)
    
    # Demand satisfaction (all should be exactly met)
    "demand_satisfaction": {
        "EMAPHOS": {"54_NCL": 700.0, "status": "exactly_met"},
        "U53": {"54_CL": 100.0, "status": "exactly_met"},
        "107DEF": {
            "29_STD": 200.0,
            "54_CL": 150.0, 
            "54_COC": 100.0,
            "status": "exactly_met"
        }
    },
    
    # Fertilizer acid requirements (should all be exactly met)
    "fertilizer_acid_satisfaction": {
        "U16": {
            "acid_29_std": 323.02,      # For MAP production
            "acid_29_dec": 438.6,       # For DAP production
            "acid_54_ncl": 1445.4,      # Total NCL needed
            "acid_54_cl": 902.42,       # Total CL needed
            "acid_54_dec_total": 398.39 # Total DEC_TOTAL needed
        },
        "status": "all_exactly_met"
    }
}
```

### Material Balance Validation
```python
# Key balance checks that must pass
MATERIAL_BALANCE_CHECKS = {
    "P29_mass_balance": {
        "total_input": 8706 + 3309.4,      # Production + Initial stock
        "total_output": "concentration + consumers + final_stock + transfers",
        "balance_tolerance": 0.001           # 0.1% tolerance
    },
    
    "P54_mass_balance": {
        "total_input": "concentration_output + initial_stock",
        "total_output": "consumers + processing + final_stock",
        "balance_tolerance": 0.001
    },
    
    "central_storage_balance": {
        "IR11_balance": "initial + CoC_input + DEC_CL_input = consumers + final",
        "IR12_balance": "initial + CL_input = consumers + final",
        "balance_tolerance": 0.001
    }
}
```

---

## EXCEL OUTPUT STRUCTURE

### Sheet 1: "Fertilizer_Consumer"
```python
FERTILIZER_CONSUMER_SHEET = {
    "columns": [
        "Line",           # Consumer/fertilizer line name
        "Products",       # Fertilizer products produced
        "Acid Needed",    # Total acid requirements by type
        "Acid Planned",   # Actual acid allocated by optimization
        "Acid Type",      # Type of acid (29_STD, 54_NCL, etc.)
        "Amount",         # Amount of each acid type
        "Source Line"     # Source of acid (line or storage)
    ],
    
    "data_structure": {
        "fertilizer_consumers": [
            {
                "consumer": "U16",
                "products": ["MAP_11_52_SPECIAL", "DAP_EURO"],
                "acid_need": {"acid_29_std": 323.02, "acid_29_dec": 438.6, ...},
                "acid_received": {"breakdown_by_acid_type": {...}, "sources": [...]}
            }
        ],
        "direct_consumers": [
            {
                "consumer": "EMAPHOS", 
                "acid_demand": {"54_NCL": 700},
                "acid_received": {"54_NCL": 700, "sources": [...]}
            }
        ]
    }
}
```

### Sheet 2: "Phosphoric_Production"
```python
PHOSPHORIC_PRODUCTION_SHEET = {
    "p29_section": {
        "title": "P29 ACID LINES (ACP29 BLOC)",
        "columns": [
            "Line",                     # 13AB, 13CD, etc.
            "P29 Total Production",     # Fixed daily production
            "P29 Standard (remains std)", # Standard acid not decadmiated
            "P29 Decadmiated (by system)", # Decadmiated amount (750/1500)
            "Initial Stock",            # Starting inventory
            "Interzone Transfer In",    # Acid received from other lines
            "Interzone Transfer Out",   # Acid sent to other lines
            "Sent to Fertilizer",      # Direct to fertilizer lines
            "Sent to Concentration"     # To P54 production
        ]
    },
    
    "p54_section": {
        "title": "P54 ACID LINES (ACP54 BLOC)",
        "columns": [
            "Line",                     # 14AB, 14CD, etc.
            "P54 NCL Production",       # From concentration
            "Initial Stock NCL",        # Starting NCL inventory
            "Clarification Input",      # NCL sent for clarification
            "Co-crystallization Input", # NCL sent for co-crystallization
            "NCL Sent to Fertilizer",   # Direct NCL to fertilizer
            "Final Stock NCL"           # Ending NCL inventory
        ]
    }
}
```

### Sheet 3: "Acid29_Stocks"
```python
ACID29_STOCKS_SHEET = {
    "columns": [
        "Line",                    # P29 line identifier
        "Type",                   # Standard or Decadmiated
        "Initial Stock",          # Starting inventory
        "Production",             # Daily production
        "Transfers In",           # From other lines
        "Transfers Out",          # To other lines
        "To Concentration",       # Sent to P54 production
        "To Fertilizer",         # Direct to fertilizer
        "Final Stock",           # Ending inventory
        "Tank Utilization %"     # Stock level as % of capacity
    ],
    
    "validation": {
        "mass_balance": "Initial + Production + In = Out + Concentration + Fertilizer + Final",
        "capacity_check": "Final Stock <= Tank Capacity",
        "minimum_stock": "Final Stock >= Minimum Safety Stock"
    }
}
```

### Sheet 4: "Acid54_Stocks"
```python
ACID54_STOCKS_SHEET = {
    "columns": [
        "Line",                    # P54 line identifier
        "Type",                   # NCL, DEC_CL
        "Initial Stock",          # Starting inventory  
        "From Concentration",     # Input from P29 concentration
        "Clarification In",       # Sent to clarification
        "Clarification Out",      # Received from clarification
        "Co-crystallization In",  # Sent to co-crystallization
        "Co-crystallization Out", # Received from co-crystallization
        "To Fertilizer",         # Direct to fertilizer
        "Final Stock",           # Ending inventory
        "Tank Utilization %"     # Stock level as % of capacity
    ]
}
```

### Sheet 5: "Central_Storage"
```python
CENTRAL_STORAGE_SHEET = {
    "ir11_section": {
        "title": "IR11 STORAGE (CoC + DEC_CL)",
        "columns": [
            "Storage Type",          # CoC or DEC_CL
            "Initial Stock",         # Starting inventory
            "Input from Lines",      # From co-crystallization/clarification
            "To Fertilizer",        # Sent to fertilizer production
            "To Direct Consumers",  # Sent to direct consumers
            "Final Stock",          # Ending inventory
            "Utilization %"         # As % of IR11 capacity
        ]
    },
    
    "ir12_section": {
        "title": "IR12 STORAGE (Clarified)",
        "columns": [
            "Initial Stock",         # Starting CL inventory
            "Input from Clarification", # From clarification process
            "To Fertilizer",        # To fertilizer production
            "To Direct Consumers",  # To U53, 107DEF
            "Final Stock",          # Ending inventory
            "Utilization %"         # As % of IR12 capacity
        ]
    }
}
```

### Sheet 6: "Flow_Analysis"
```python
FLOW_ANALYSIS_SHEET = {
    "interzone_transfers": {
        "title": "P29 INTERZONE TRANSFERS",
        "matrix_format": "From/To matrix showing transfer amounts",
        "columns": ["From Line", "To Line", "Amount (tonnes)", "% of Production"]
    },
    
    "processing_flows": {
        "title": "PROCESSING FLOWS",
        "sections": [
            "Concentration (P29 → P54)",
            "Clarification (P54 NCL → CL)",
            "Co-crystallization (P54 NCL → CoC)"
        ]
    },
    
    "consumer_flows": {
        "title": "CONSUMER DELIVERY FLOWS", 
        "breakdown": "By acid type and source line"
    }
}
```

### Sheet 7: "KPI_Dashboard"
```python
KPI_DASHBOARD_SHEET = {
    "key_metrics": [
        "Total Acid Delivered",      # Sum of all acid to consumers
        "Demand Satisfaction Rate",  # % of demand met
        "Production Utilization",    # % of capacity used
        "Storage Utilization",       # % of tank capacity used
        "Transfer Efficiency",       # Transfers vs production ratio
        "Process Yield Achievement"  # Actual vs expected yields
    ],
    
    "validation_status": [
        "Mass Balance Status",       # Pass/Fail for each unit
        "Capacity Compliance",      # Pass/Fail for limits
        "Quality Compliance",       # Pass/Fail for restrictions
        "Optimization Status"       # Optimal/Infeasible/etc.
    ]
}
```

---

## VALIDATION NUMBERS

### Expected Final Results (Test Reference)
```python
# These numbers should match the test system output
EXPECTED_FINAL_NUMBERS = {
    "total_acid_delivered": 8977.35,    # Total acid sent to consumers
    "p29_production_total": 8706.0,     # Sum of all P29 production
    "p54_production_total": ~4830.0,    # Estimated P54 NCL production
    "central_storage_usage": ~1200.0,   # IR11 + IR12 usage
    "interzone_transfers": ~1500.0,     # Total P29 transfers
    
    # Key consumer deliveries
    "emaphos_delivery": 700.0,          # Exactly as demanded
    "u53_delivery": 100.0,              # Exactly as demanded
    "107def_total": 450.0,              # 200 + 150 + 100
    
    # Fertilizer acid totals
    "u16_total_acid": ~3507.84,         # All acid types to U16
    "u116a_total_acid": ~2268.75,       # All acid types to U116A
    "u116bc_total_acid": ~2416.23       # All acid types to U116BC
}
```

---

## SUCCESS CRITERIA

### Primary Success Indicators
```python
SUCCESS_CRITERIA = {
    "optimization_status": {
        "expected": "Optimal",
        "critical": True,
        "description": "Solver must find optimal solution"
    },
    
    "exact_demand_satisfaction": {
        "tolerance": 0.01,
        "critical": True,
        "check": "all planned amounts = required amounts ± 0.01"
    },
    
    "mass_balance_validation": {
        "tolerance": 0.001,
        "critical": True,
        "check": "input = output for all process units"
    },
    
    "capacity_compliance": {
        "tolerance": 0.0,
        "critical": True,
        "check": "no capacity limits exceeded"
    },
    
    "excel_generation": {
        "required_sheets": 7,
        "critical": False,
        "check": "all 7 sheets generated with correct structure"
    }
}
```

### Validation Commands
```python
def validate_test_results(results, excel_path):
    """Validate optimization results against test reference"""
    
    # Check optimization status
    assert results["optimization_status"] == "Optimal"
    
    # Check objective value (within tolerance)
    expected_objective = -8977.34733
    actual_objective = results["objective_value"]
    assert abs(actual_objective - expected_objective) < 1.0
    
    # Check demand satisfaction
    for consumer in ACID_DEMAND_TEST:
        for acid_type, required in ACID_DEMAND_TEST[consumer].items():
            planned = get_planned_amount(results, consumer, acid_type)
            assert abs(planned - required) < 0.01
    
    # Check Excel file existence and structure
    assert os.path.exists(excel_path)
    wb = openpyxl.load_workbook(excel_path)
    expected_sheets = ["Fertilizer_Consumer", "Phosphoric_Production", 
                      "Acid29_Stocks", "Acid54_Stocks", "Central_Storage",
                      "Flow_Analysis", "KPI_Dashboard"]
    for sheet_name in expected_sheets:
        assert sheet_name in wb.sheetnames
    
    print("✅ All validation checks passed")
    return True
```

---

**This document provides the exact test reference data and expected output structure that any AI tool can use to validate their implementation. The test system serves as the definitive reference for "correct" optimization behavior.**
