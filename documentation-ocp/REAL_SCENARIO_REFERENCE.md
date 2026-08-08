# REAL SCENARIO REFERENCE & SYSTEM VALIDATION
## Hybrid Real Scenario Input Data and Expected System Behavior

---

## TABLE OF CONTENTS
1. [Real System Input Data](#real-system-input-data)
2. [Expected System Behavior](#expected-system-behavior)
3. [Validation Framework](#validation-framework)
4. [Success Criteria](#success-criteria)
5. [System Capacity Analysis](#system-capacity-analysis)

---

## REAL SYSTEM INPUT DATA

### Production Levels (Fixed Daily Production)
```python
# P29 Production (Fixed - Cannot Change) - from hybrid_real_scenario.py
REAL_P29_PRODUCTION = {
    '13AB': 1500,   # tonnes/day
    '13CD': 1500,   # tonnes/day
    '13XY': 1500,   # tonnes/day
    '13ZU': 800,    # tonnes/day
    '13E': 1500,    # tonnes/day
    '13F': 1500     # tonnes/day
}
# Total P29 Production: 8,300 tonnes/day
```

### Initial Stock Levels (Real Tank Measurements)
```python
# Initial Stock Heights (meters) - from hybrid_real_scenario.py
REAL_INITIAL_STOCK_HEIGHTS = {
    # P29 tank heights (meters) - use get_vol_29(height) to convert to tonnes
    'P29_heights': {
        '13AB': 13.75,  # meters → get_vol_29(13.75) = 790.2 tonnes standard
        '13CD': 6.75,   # meters → get_vol_29(6.75) = 387.9 tonnes standard
        '13XY': 5.05,   # meters → get_vol_29(5.05) = 290.2 tonnes standard
        '13ZU': 14.20,  # meters → get_vol_29(14.20) = 816.0 tonnes standard
        '13E': 7.70,    # meters → get_vol_29(7.70) = 442.5 tonnes standard
        '13F': 14.40    # meters → get_vol_29(14.40) = 827.7 tonnes standard
    },
    
    # P29 decadmiated stock heights (meters) - all start at 0
    'P29_dec_heights': {
        '13AB': 0,      # meters → get_vol_29(0) = 0 tonnes decadmiated
        '13CD': 6.00,   # meters → get_vol_29(6.00) = 344.6 tonnes decadmiated
        '13XY': 7.95,   # meters → get_vol_29(7.95) = 456.8 tonnes decadmiated
        '13ZU': 0,      # meters → get_vol_29(0) = 0 tonnes decadmiated
        '13E': 0,       # meters → get_vol_29(0) = 0 tonnes decadmiated
        '13F': 0        # meters → get_vol_29(0) = 0 tonnes decadmiated
    },
    
    # P54 tank heights (meters) - use get_vol_54(height) to convert to tonnes
    'P54_heights': {
        '14AB': 11.43,  # meters → get_vol_54(11.43) = 901.1 tonnes NCL
        '14CD': 4.68,   # meters → get_vol_54(4.68) = 369.0 tonnes NCL
        '14XY': 3.78,   # meters → get_vol_54(3.78) = 298.0 tonnes NCL
        '14ZU': 11.65,  # meters → get_vol_54(11.65) = 918.4 tonnes NCL
        '14EXT': 2.80   # meters → get_vol_54(2.80) = 220.7 tonnes NCL
    },
    
    # Central storage heights (meters) - use CORRECTED conversion formulas
    'central_storage_heights': {
        'IR11': 9.38,   # meters → get_vol_54_IR11(9.38) = 5500.8 tonnes (CoC + DEC_CL)
        'IR12': 9.14    # meters → get_vol_54_IR12(9.14) = 4004.1 tonnes (CL)
    }
}

# Converted Initial Stocks (tonnes)
REAL_INITIAL_STOCKS = {
    'p29': {
        '13AB': {'acid_29_std': 790.2, 'acid_29_dec': 0.0},
        '13CD': {'acid_29_std': 387.9, 'acid_29_dec': 344.6},
        '13XY': {'acid_29_std': 290.2, 'acid_29_dec': 456.8},
        '13ZU': {'acid_29_std': 816.0, 'acid_29_dec': 0.0},
        '13E': {'acid_29_std': 442.5, 'acid_29_dec': 0.0},
        '13F': {'acid_29_std': 827.7, 'acid_29_dec': 0.0}
    },
    'p54': {
        '14AB': 901.1,
        '14CD': 369.0,
        '14XY': 298.0,
        '14ZU': 918.4,
        '14EXT': 220.7
    },
    'central': {
        'IR11': 5500.8,  # Using corrected formula get_vol_54_IR11(9.38)
        'IR12': 4004.1   # Using corrected formula get_vol_54_IR12(9.14)
    }
}
# Total Initial P29 Stock: 4,355.9 tonnes (std + dec)
# Total Initial P54 Stock: 2,707.2 tonnes (NCL)
# Total Initial Central Storage: 9,504.9 tonnes
```

### Demand Requirements (Real Production Demands)
```python
# Direct Acid Demand (tonnes) - from hybrid_real_scenario.py
REAL_DIRECT_DEMAND = {
    'IMACID': {'acid_29_std': 700},           # 700 tonnes standard P29
    'EMAPHOS': {'acid_54_ncl': 700},          # 700 tonnes NCL acid
    'MAPS': {'acid_29_std': 0},               # 0 tonnes
    'U53': {'acid_54_cl': 1500},              # 1500 tonnes CL acid from IR12
    '107DEF': {                               # Direct consumer
        'acid_29_std': 0,                     # 0 tonnes standard P29
        'acid_54_cl': 0,                      # 0 tonnes CL from IR12
        'acid_54_coc': 0                      # 0 tonnes CoC from IR11
    },
    'JFC1-5': {'acid_29_std': 0}              # 0 tonnes
}
# Total Direct Acid Demand: 2,900 tonnes

# Fertilizer Production Demand (tonnes of fertilizer) - from hybrid_real_scenario.py
REAL_FERTILIZER_DEMAND = {
    'U16': {
        'DAP_STANDARD': 3057,     # 3,057 tonnes DAP
        'TSP_EURO': 1200          # 1,200 tonnes TSP
    },
    'U116A': {
        'MAP_11_52_EU': 3037   # 3,037 tonnes MAP
    },
    'U116BC': {
        'NPK_12_24_12_EU': 1540,                    # 1,540 tonnes NPK
        'NPK_15_15_15_EU_20_MGKP2O5': 2126         # 2,126 tonnes NPK
    }
}
# Total Fertilizer Demand: 10,960 tonnes

# Fertilizer Acid Requirements (calculated from quality profiles)
REAL_FERTILIZER_ACID_REQUIREMENTS = {
    'U16': {
        'DAP_STANDARD': {
            'acid_29_std': 0.127 * 3057,      # = 388.24 tonnes
            'acid_54_ncl': 0.354 * 3057       # = 1082.18 tonnes
        },
        'TSP_EURO': {
            'acid_54_dec_total': 0.379 * 1200 # = 454.8 tonnes
        }
    },
    'U116A': {
        'MAP_11_54_NE_EU': {
            'acid_29_dec': 0.03 * 3037,       # = 91.11 tonnes
            'acid_54_dec_total': 0.129 * 3037 # = 391.77 tonnes
        }
    },
    'U116BC': {
        'NPK_12_24_12_EU': {
            'acid_54_dec_total': 0.091 * 1540 # = 140.14 tonnes
        },
        'NPK_15_15_15_EU_20_MGKP2O5': {
            'acid_29_dec': 0.171 * 2126       # = 363.55 tonnes
        }
    }
}
# Total Fertilizer Acid Requirements: ~2911 tonnes
```

### Working Hours Configuration (Real Operations)
```python
# Echelon Working Hours (hours/day) - from hybrid_real_scenario.py
REAL_WORKING_HOURS = {
    # EXT echelons (14EXT - all enabled for co-crystallization)
    "E": 24, "F": 24, "G": 24, "H": 14,
    
    # AB echelons (14AB - I,J A K , for CoC, others regular NCL)
    "I": 24, "J": 14, "A": 24, "K": 24, "B": 24, "L": 24,
    
    # CD echelons (14CD - no co-crystallization)
    "C": 24, "M": 24, "D": 24, "N": 24,
    
    # XY echelons (14XY - no co-crystallization)
    "X": 14, "P": 14, "Y": 24, "Q": 24,
    
    # ZU echelons (14ZU - no co-crystallization)
    "Z": 14, "R": 14, "U": 24, "S": 24, "V": 24, "W": 0
}

# Calculated P54 Production (based on working hours and capacities)
EXPECTED_P54_PRODUCTION = {
    '14AB': "Capacity × working_hours / 24",    # ~1475 tonnes/day NCL
    '14CD': "Capacity × working_hours / 24",    # ~1410 tonnes/day NCL
    '14XY': "Capacity × working_hours / 24",    # ~1050 tonnes/day NCL (reduced hours)
    '14ZU': "Capacity × working_hours / 24",    # ~850 tonnes/day NCL (reduced hours)
    '14EXT': "Capacity × working_hours / 24"    # ~1520 tonnes/day NCL
}
# Estimated Total P54 Production: ~6,305 tonnes/day NCL
```

### Process Configuration (Real System Settings)
```python
# Line Capability Configuration for real system (NEW)
REAL_LINE_CAPABILITIES = {
    # DEC 29 capability: lines that can produce acid 29 dec for fertilizer
    'DEC_29_ENABLED': ['13CD', '13XY'],  # CD and XY have filters for acid 29 dec
    
    # NCL clarification capability: lines that can clarify NCL to CL
    'NCL_CLARIFICATION_ENABLED': ['14CD', '14ZU'],  # CD and ZU can clarify NCL
    
    # DEC CL capability: lines that can send dec acid to concentration for clarification
    'DEC_CL_ENABLED': ['14XY'],  # XY can do full dec process to DEC CL
    
    'note': 'Example configuration showing three types of line capabilities'
}

# Decadmiation configuration for real system
REAL_DECADMIATION_CONFIG = {
    'enabled_lines': ['13AB', '13CD', '13XY', '13ZU', '13F'],  # Real enabled lines
    'initial_dec_stock': {  # Real initial dec stock from measurements
        '13AB': 0.0, '13CD': 344.6, '13XY': 456.8, 
        '13ZU': 0.0, '13E': 0.0, '13F': 0.0
    },
    'levels_allowed': [0, 750, 1500],  # Possible decadmiation amounts per day
    'note': 'Real scenario with some lines having initial decadmiated stock'
}

# Clarification configuration for real system  
REAL_CLARIFICATION_CONFIG = {
    'enabled_lines': ['14AB', '14CD', '14XY', '14ZU'],  # Real enabled lines (no 14EXT)
    'capacity_per_line': 1000,      # tonnes/day max clarification per line (NCL + DEC combined)
    'decanter_capacity': 500,       # tonnes/day per decanter (2 per line)
    'yield': 0.90,                  # 90% yield (10% sludge return to P29)
    'sludge_return_to': 'P29_standard_stock',  # Sludge returns as standard acid
    'shared_capacity_constraint': 'Total clarification (NCL + DEC) ≤ 1000 tonnes/day per line',
    'note': '14EXT not enabled for clarification in real system'
}

# Co-crystallization configuration for real system
REAL_COCRYSTALLIZATION_CONFIG = {
    'enabled_echelons': {
        'EXT': ['E', 'F', 'G', 'H'],     # All 4 echelons enabled for CoC
        'AB': ['I', 'J', 'A', 'K']       # 4 echelons enabled for CoC (I,J,A,K), B,L regular NCL
    },
    'disabled_lines': ['14CD', '14XY', '14ZU'],  # No CoC capability
    'yield': 0.80,                      # 80% yield (20% sludge return to P29)
    'sludge_return_to': 'P29_standard_stock', # Sludge returns to P29 standard acid stock
    'note': 'Real configuration: EXT (all echelons) and AB (I,J,A,K) perform co-crystallization'
}
```

---

## EXPECTED SYSTEM BEHAVIOR

### Capacity Analysis
```python
# System capacity vs demand analysis
CAPACITY_ANALYSIS = {
    "total_p29_production": 8300,       # tonnes/day
    "total_p54_production": ~6305,      # tonnes/day (estimated from working hours)
    "total_direct_demand": 2900,        # tonnes
    "total_fertilizer_acid_demand": ~2911,  # tonnes (from quality profiles)
    "total_acid_demand": ~5811,         # tonnes
    
    "capacity_utilization": {
        "p29_utilization": "~70% (5811/8300)",
        "p54_utilization": "~92% (5811/6305)",
        "system_bottleneck": "P54 production (higher utilization)"
    }
}
```

### Expected Optimization Behavior
```python
EXPECTED_OPTIMIZATION_BEHAVIOR = {
    "optimization_status": "Optimal",
    "demand_satisfaction": "100% (all demands should be met)",
    
    "expected_decisions": {
        "decadmiation_levels": {
            "description": "Lines will decadmiate to meet dec_total requirements",
            "estimated_total": "~850 tonnes/day decadmiation",
            "lines_active": "Based on demand for acid_29_dec and acid_54_dec_total"
        },
        
        "manual_clarification": {
            "description": "Clarification to meet CL demand from IR12",
            "estimated_total": "~1670 tonnes/day clarification (1500 for U53 + safety)",
            "enabled_lines": "14AB, 14CD, 14XY, 14ZU"
        },
        
        "systematic_processing": {
            "cocrystallization": "Automatic CoC from EXT (all echelons) and AB (I,J)",
            "automatic_dec_clarification": "Decadmiated acid auto-clarified to IR11"
        }
    },
    
    "expected_flows": {
        "p29_to_concentration": "~6305 tonnes (to meet P54 demand)",
        "p29_to_fertilizer": "~479 tonnes direct (acid_29_std + acid_29_dec)",
        "p54_ncl_to_fertilizer": "~1082 tonnes direct",
        "ir12_deliveries": "~1500 tonnes (primarily U53)",
        "ir11_deliveries": "~987 tonnes (dec_total requirements)"
    }
}
```

### Stock Movement Expectations
```python
EXPECTED_STOCK_MOVEMENTS = {
    "p29_stocks": {
        "initial_total": 4355.9,       # tonnes (std + dec)
        "final_expected": "~6000-7000", # tonnes (production surplus after demands)
        "stock_violations": "None expected (sufficient capacity)"
    },
    
    "p54_stocks": {
        "initial_total": 2707.2,       # tonnes NCL
        "final_expected": "~1500-2500", # tonnes (after processing and deliveries)
        "stock_violations": "Possible if high clarification demand"
    },
    
    "central_storage": {
        "ir11_initial": 5500.8,        # tonnes
        "ir11_final": "~5000-6000",    # tonnes (CoC input - deliveries)
        "ir12_initial": 4004.1,        # tonnes
        "ir12_final": "~3500-4500",    # tonnes (CL input - U53 delivery)
        "violations": "None expected (high capacity with corrected formulas)"
    }
}
```

---

## VALIDATION FRAMEWORK

### Primary Validation Checks
```python
VALIDATION_FRAMEWORK = {
    "optimization_status": {
        "requirement": "Must achieve Optimal status",
        "tolerance": "No tolerance - must be exactly 'Optimal'",
        "failure_action": "Review capacity constraints and demand feasibility"
    },
    
    "demand_satisfaction": {
        "requirement": "All consumer demands exactly satisfied",
        "tolerance": "±0.01 tonnes per acid type",
        "check": "For each consumer: delivered_acid ≥ required_acid * 0.9999"
    },
    
    "mass_balance_validation": {
        "requirement": "Conservation of mass at every node",
        "tolerance": "±0.1% for each line",
        "check": "For each line: input + initial_stock = output + final_stock ± transfers"
    },
    
    "capacity_compliance": {
        "requirement": "No capacity violations",
        "tolerance": "0 (strict)",
        "check": "All usage ≤ available_capacity"
    },
    
    "stock_constraint_validation": {
        "requirement": "All final stocks ≥ 0",
        "tolerance": "±0.01 tonnes",
        "check": "final_stock[line][acid_type] ≥ -0.01 for all combinations"
    }
}
```

### Process Validation Requirements
```python
PROCESS_VALIDATION = {
    "decadmiation_validation": {
        "requirement": "Decadmiation levels must be 0, 750, or 1500 only",
        "check": "All decadmiation_levels[line] in [0, 750, 1500]"
    },
    
    "clarification_validation": {
        "requirement": "Clarification amounts ≤ 1000 tonnes per enabled line",
        "check": "manual_clarification[line] ≤ 1000 for enabled lines"
    },
    
    "systematic_processing_validation": {
        "requirement": "Systematic CoC and DEC_CL follow process rules",
        "check": "CoC only from enabled echelons, DEC_CL automatic after concentration"
    },
    
    "yield_validation": {
        "requirement": "All process yields exactly followed",
        "check": "clarification_output = 0.9 × input, cocrystallization_output = 0.8 × input"
    }
}
```

---

## SUCCESS CRITERIA

### Quantitative Success Indicators
```python
SUCCESS_CRITERIA = {
    "primary_success": {
        "optimization_status": "Optimal",
        "demand_satisfaction_rate": "100.0%",
        "mass_balance_errors": "< 0.1%",
        "capacity_violations": "0"
    },
    
    "expected_objective_value": {
        "description": "Total acid delivered to all consumers",
        "minimum_expected": 5811,      # Total demand
        "optimal_range": "5811-6000",  # Total demand + potential surplus
        "units": "tonnes"
    },
    
    "performance_indicators": {
        "production_utilization": "70-95%",
        "stock_turnover": "Reasonable final stock levels",
        "processing_efficiency": "All enabled processes utilized appropriately"
    }
}
```

### Operational Success Indicators
```python
OPERATIONAL_SUCCESS = {
    "solution_feasibility": "Model finds feasible solution within constraints",
    "computation_time": "Optimization completes within 2 minutes",
    "solution_stability": "Consistent results with same input data",
    "excel_generation": "All 5 sheets generated with proper formatting",
    "data_consistency": "All output values mathematically consistent"
}
```

---

## SYSTEM CAPACITY ANALYSIS

### Bottleneck Analysis
```python
BOTTLENECK_ANALYSIS = {
    "production_bottlenecks": {
        "p29_capacity": "8,300 tonnes/day (sufficient)",
        "p54_capacity": "~6,305 tonnes/day (potential bottleneck)",
        "clarification_capacity": "4,000 tonnes/day max (4 lines × 1000)",
        "cocrystallization_capacity": "Unlimited (yield-based)"
    },
    
    "storage_bottlenecks": {
        "p29_storage": "15,600 tonnes total (6 lines × 2,600)",
        "p54_storage": "18,500 tonnes total (5 lines × 3,700)",
        "ir11_capacity": "6,378 tonnes (corrected formula)",
        "ir12_capacity": "4,804 tonnes (corrected formula)"
    },
    
    "expected_constraints": {
        "active_constraints": [
            "P54 production capacity (high utilization)",
            "U53 CL demand (1500 tonnes requires significant clarification)",
            "Decadmiation requirements (for fertilizer dec_total)"
        ],
        "non_binding_constraints": [
            "P29 production capacity (low utilization)",
            "Central storage capacity (high capacity with corrected formulas)",
            "Clarification capacity (sufficient for expected demand)"
        ]
    }
}
```

### Expected Solution Characteristics
```python
EXPECTED_SOLUTION = {
    "decision_patterns": {
        "decadmiation_strategy": "Activate decadmiation on lines with lowest opportunity cost",
        "clarification_strategy": "Distribute clarification across enabled lines to meet IR12 demand",
        "transfer_strategy": "Minimal interzone transfers due to sufficient local production",
        "storage_strategy": "Utilize high central storage capacity efficiently"
    },
    
    "resource_utilization": {
        "high_utilization": ["P54 production", "Manual clarification", "IR12 storage"],
        "moderate_utilization": ["P29 production", "Decadmiation", "IR11 storage"],
        "low_utilization": ["Interzone transfers", "Local P29/P54 storage"]
    }
}
```

---

**This real scenario reference provides the exact input data and expected behavior for the hybrid phosphoric acid optimization system. Any AI implementation should validate against these specific values and behavioral expectations to ensure correctness.**