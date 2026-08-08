# CORE FIXED ELEMENTS REFERENCE
## Definitive System Constants for AI Implementation

---

## TABLE OF CONTENTS
1. [Production Lines & Echelons](#production-lines--echelons)
2. [Interzone Balancing Matrix](#interzone-balancing-matrix)
3. [Fertilizer Interconnection Matrix](#fertilizer-interconnection-matrix)
4. [Tank Specifications](#tank-specifications)
5. [Process Constraints](#process-constraints)
6. [Quality Profiles](#quality-profiles)
7. [Acid Types and Stock Management](#acid-types-and-stock-management)

---

## PRODUCTION LINES & ECHELONS

### P29 Lines (6 lines)
```python
P29_LINES = ['13AB', '13CD', '13XY', '13ZU', '13E', '13F']

# Fixed daily production (tonnes/day) - CANNOT be changed by optimization
P29_PRODUCTION = {
    '13AB': 1198,
    '13CD': 1530, 
    '13XY': 1427,
    '13ZU': 1479,
    '13E': 1642,
    '13F': 1430
}
```

### P54 Lines (5 lines)  
```python
P54_LINES = ['14AB', '14CD', '14XY', '14ZU', '14EXT']

# Line mapping (fixed mapping)
P29_TO_P54_MAPPING = {
    '13AB': '14AB',
    '13CD': '14CD', 
    '13XY': '14XY',
    '13ZU': '14ZU',
    '13E': '14EXT',
    '13F': None  # 13F has no P54 line - direct P29 use only
}
```

### P29 to P54 Process Logic
```python
# P29 and P54 production levels are FIXED (cannot be optimized)
# What is optimized:
# 1. P29 stock usage - how much stock to use when P29 production < P54 demand
# 2. Interzone transfers - balancing P29 between lines
# 3. Storage management - when to store vs send to fertilizer

# Process scenarios:
# Case 1: P29 production >= P54 demand
#   - P54 gets required P29 directly
#   - Excess P29 can be stored or sent to fertilizer
#   - Storage acts as buffer for future needs

# Case 2: P29 production < P54 demand  
#   - P54 gets all P29 production
#   - Additional P29 needed from stock
#   - Optimization decides how much stock to use
#   - Interzone transfers help balance shortages

# The constraint: P29 to P54 flow = P54 demand (fixed)
# The optimization: P29 stock usage and interzone balancing
# P29 contains both acid std and acid dec 
# the sum of acid 29 dec and Acid std went to concentration must meet the P54 total production planned based on working hours 
```

### Echelon Structure
```python
# Echelon capacities (tonnes/hour) - corrected
ECHELON_CAPACITY = {
    "C": 250, "D": 250, "M": 290, "N": 250       # CD echelons
    "X": 300, "Y": 250, "P": 250, "Q": 250,      # XY echelons
    "Z": 250, "U": 300, "R": 250, "S": 300, "V": 590, "W": 590,  # ZU echelons
    # (regular)

    "E": 420, "F": 420, "G": 420, "H": 420,      # EXT echelons
    "A": 300, "B": 300, "K": 300, "L": 300, "I": 590, "J": 590,     # AB echelons 
    #(CoC capable)
}

# Echelon groups by line - corrected
ECHELON_GROUPS = {
    "EXT": {
        "echelons": ["E", "F", "G", "H"], 
        "source_29": ["13E"], 
        "cocrystallization_echelons": 4    # All 4 for CoC by default but can have less 
    },
    "AB": {
        "echelons": ["A", "B", "I", "J", "K", "L"], 
        "source_29": ["13AB"], 
        "cocrystallization_echelons": 2    # can have more or less but default is 2 or 3
    },
    "CD": {
        "echelons": ["C", "D", "M", "N"], 
        "source_29": ["13CD"], 
        "cocrystallization_echelons": 0    # No CoC
    },
    "XY": {
        "echelons": ["X", "Y", "P", "Q"], 
        "source_29": ["13XY"], 
        "cocrystallization_echelons": 0    # No CoC
    },
    "ZU": {
        "echelons": ["Z", "U", "R", "S", "V", "W"], 
        "source_29": ["13ZU"], 
        "cocrystallization_echelons": 0    # No CoC
    }
}
```

---

## INTERZONE BALANCING MATRIX

### P29 Transfer Matrix (Core Fixed Element)
```python
# "x" = transfer allowed, None = no transfer allowed
INTER_ZONE_OPERATIONS = {
    "E": {"E": None, "F": None, "AB": "x", "CD": "x", "XY": None, "ZU": None},
    "F": {"E": "x", "F": None, "AB": "x", "CD": None, "XY": "x", "ZU": "x"},
    "AB": {"E": "x", "F": None, "AB": None, "CD": "x", "XY": None, "ZU": None},
    "CD": {"E": "x", "F": None, "AB": "x", "CD": None, "XY": "x", "ZU": None},
    "XY": {"E": None, "F": None, "AB": None, "CD": "x", "XY": None, "ZU": "x"},
    "ZU": {"E": None, "F": None, "AB": None, "CD": None, "XY": "x", "ZU": None}
}
```

### Transfer Constraints
```python
# Minimum transfer amounts (tonnes)
MIN_TRANSFER_ACID_29 = 100.0
MIN_TRANSFER_LINE_STORAGE = 100.0
MIN_TRANSFER_CENTRAL_STORAGE = 100.0

# **Important**: Only STANDARD P29 acid can be transferred
# Decadmiated P29 acid CANNOT be transferred between lines
```

---

## FERTILIZER INTERCONNECTION MATRIX

### Fertilizer Line Connections (Core Fixed Element)
```python
FERTILIZER_CONNECTIONS = {
    'U16': {
        'acid_29_sources': ['13AB', '13CD', '13XY', '13ZU'],
        'acid_54_sources': ['14XY', '14CD', '14AB', '14EXT']
    },
    'U116A': {
        'acid_29_sources': ['13CD', '13F'],
        'acid_54_sources': ['14AB', '14CD', '14EXT']
    },
    'U116BC': {
        'acid_29_sources': ['13F', '13AB', '13XY'],
        'acid_54_sources': ['14XY', '14CD']
    },
    'IMACID': {
        'acid_29_sources': ['13E'],
        'acid_54_sources': []
    },
    'EMAPHOS': {
        'acid_29_sources': [],
        'acid_54_sources': ['14ZU', '14XY', '14AB']
    },
    'MAPS': {
        'acid_29_sources': ['13E'],
        'acid_54_sources': []
    },
    'U53': {
        'acid_29_sources': [],
        'acid_54_sources': []   # Only takes CL from IR12
    },
    '107DEF': {
        'acid_29_sources': ['13E', '13F'],
        'acid_54_sources': []  # Can receive from IR11
    },
    'JFC1-5': {
        'acid_29_sources': ['13F'],
        'acid_54_sources': []
    }
}
```

---

## TANK SPECIFICATIONS

### Volume Calculation Functions
```python
# P29 Tank conversion: meters → tonnes
get_vol_29 = lambda x: 174.11 * x * 0.33

# P54 Tank conversion: meters → tonnes (for regular P54 lines)
get_vol_54 = lambda x: 95 * x * 0.83

# CRITICAL: IR11/IR12 Central Storage - Special Conversion Formulas
# IR11 Tank conversion: meters → tonnes
get_vol_54_IR11 = lambda x: ((x - 0.25) * 706.45) * 0.855

# IR12 Tank conversion: meters → tonnes  
get_vol_54_IR12 = lambda x: ((x - 2.7) * 706.45) * 0.84
```

### Tank Physical Parameters
```python
# Acid 29% tanks
SECTION_29 = 174.11    # m²
DENSITY_29 = 1.270     # tonnes/m³
P2O5_29 = 0.26         # 26% P2O5
H_MIN_29 = 2.00        # minimum height (m)
H_MAX_29 = 8.40        # maximum height (m)

# Acid 54% tanks
SECTION_54 = 95        # m²
DENSITY_54 = 1.66      # tonnes/m³
P2O5_54 = 0.50         # 50% P2O5
H_MIN_54 = 3.00        # minimum height (m)
H_MAX_54 = 9.40        # maximum height (m)
```

### Storage Capacity Limits
```python
# Calculate minimum and maximum stock levels (2 tanks per line)
Z_MIN_29 = 2 * SECTION_29 * H_MIN_29 * P2O5_29 * DENSITY_29  # ≈ 364.5 tonnes
Z_MAX_29 = 2 * SECTION_29 * H_MAX_29 * P2O5_29 * DENSITY_29  # ≈ 1530.7 tonnes

Z_MIN_54 = 2 * SECTION_54 * H_MIN_54 * P2O5_54 * DENSITY_54  # ≈ 473.4 tonnes
Z_MAX_54 = 2 * SECTION_54 * H_MAX_54 * P2O5_54 * DENSITY_54  # ≈ 1483.6 tonnes

# Central storage bounds - CORRECTED FORMULAS
# IR11 bounds (CoC + DEC_CL)
H_MIN_54_IR11 = 0.40   # meters
H_MAX_54_IR11 = 10.80  # meters
Z_MIN_54_IR11 = get_vol_54_IR11(H_MIN_54_IR11)  # ((0.40-0.25)*706.45)*0.855 ≈ 90.8 tonnes
Z_MAX_54_IR11 = get_vol_54_IR11(H_MAX_54_IR11)  # ((10.80-0.25)*706.45)*0.855 ≈ 6,378.4 tonnes

# IR12 bounds (CL only)
H_MIN_54_IR12 = 2.00   # meters
H_MAX_54_IR12 = 10.80  # meters
Z_MIN_54_IR12 = max(0, get_vol_54_IR12(H_MIN_54_IR12))  # ((2.00-2.7)*706.45)*0.84 ≈ 0 tonnes (negative becomes 0)
Z_MAX_54_IR12 = get_vol_54_IR12(H_MAX_54_IR12)  # ((10.80-2.7)*706.45)*0.84 ≈ 4,804.3 tonnes
```

### P29 Acid Storage (Standard + Decadmiated)
```python
# Each P29 line has 2 tanks that can store BOTH standard and decadmiated acid
P29_TANK_CAPACITY_PER_TANK = 1300   # tonnes per tank
P29_TANKS_PER_LINE = 2               # 2 tanks per line
P29_TOTAL_CAPACITY_PER_LINE = 2600   # tonnes total storage per line

# Storage flexibility: Each tank can store either acid type
P29_ACID_TYPES_SUPPORTED = ['acid_29_std', 'acid_29_dec']

# IMPORTANT: Lines can produce and store BOTH standard and decadmiated acid
# - Standard acid: Always produced (production minus decadmiation amount)
# - Decadmiated acid: Only when decadmiation process is enabled
# - Both types share the same tank capacity (2600 tonnes total per line)

P29_STORAGE_CONFIGURATION = {
    'tank_flexibility': 'Each tank can store either standard or decadmiated acid',
    'shared_capacity': 'Total 2600 tonnes shared between both acid types',
    'inventory_tracking': 'Separate tracking for acid_29_std and acid_29_dec stocks',
    'operational_rule': 'acid_29_std_stock + acid_29_dec_stock ≤ 2600 tonnes per line'
}
```

### P54 Acid Storage (NCL + Processed Types)
```python
# Each P54 line has different tank configurations
P54_TANK_CONFIGURATIONS = {
    '14AB': {'capacity_per_tank': 1850, 'tanks': 2, 'total_capacity': 3700},
    '14CD': {'capacity_per_tank': 1850, 'tanks': 2, 'total_capacity': 3700}, 
    '14XY': {'capacity_per_tank': 1850, 'tanks': 2, 'total_capacity': 3700},
    '14ZU': {'capacity_per_tank': 1850, 'tanks': 2, 'total_capacity': 3700},
    '14EXT': {'capacity_per_tank': 1850, 'tanks': 2, 'total_capacity': 3700}
}

# P54 acid types that can be stored locally at production lines
P54_LOCAL_STORAGE_TYPES = ['acid_54_ncl']  # Only NCL stored locally

# Processed acid types go to central storage
P54_CENTRAL_STORAGE_TYPES = ['acid_54_cl', 'acid_54_coc', 'acid_54_dec_cl']

# IMPORTANT: DEC_CL (decadmiated clarified) goes directly to IR11, no local storage
P54_STORAGE_RULES = {
    'local_storage': 'Only acid_54_ncl stored at production lines',
    'clarified_acid': 'acid_54_cl goes to IR12 central storage',
    'coc_acid': 'acid_54_coc goes to IR11 central storage',
    'dec_cl_acid': 'acid_54_dec_cl goes directly to IR11 (no local storage)'
}
```

### Central Storage Specifications
```python
# IR11: Combined storage for CoC and DEC_CL - CORRECTED CAPACITY
IR11_STORAGE = {
    'total_capacity': 6378,  # tonnes (using corrected formula: get_vol_54_IR11(10.80))
    'acid_types': ['acid_54_coc', 'acid_54_dec_cl'],
    'shared_capacity': True,  # Both types share the same tank space
    'operational_rule': 'coc_stock + dec_cl_stock ≤ 6378 tonnes'
}

# IR12: Clarified acid storage - CORRECTED CAPACITY
IR12_STORAGE = {
    'total_capacity': 4804,  # tonnes (using corrected formula: get_vol_54_IR12(10.80))
    'acid_types': ['acid_54_cl'],
    'dedicated_storage': True
}

# Storage inventory tracking
CENTRAL_STORAGE_TRACKING = {
    'IR11': ['acid_54_coc_stock', 'acid_54_dec_cl_stock'],
    'IR12': ['acid_54_cl_stock']
}
```

---

## PROCESS CONSTRAINTS

### Fixed Process Yields
```python
# Process yields (FIXED - cannot be optimized)
CONCENTRATION_YIELD = 1.0      # 100% mass transfer P29 → P54
CLARIFICATION_YIELD = 0.90     # 90% CL + 10% sludge
CLARIFICATION_SLUDGE = 0.10    # 10% returns to P29
COCRYSTALLIZATION_YIELD = 0.80 # 80% CoC + 20% sludge
COCRYSTALLIZATION_SLUDGE = 0.20 # 20% returns to P54 NCL

# EMAPHOS return ratios
EMAPHOS_SLUDGE_RETURN_RATE = 0.15   # 15% returns as sludge to 13XY
EMAPHOS_ARP1_RETURN_RATE = 0.125    # 12.5% returns as ARP1 to 13AB
EMAPHOS_ARP2_RETURN_RATE = 0.125    # 12.5% returns as ARP2 to 13CD
```

### Decadmiation Configuration (Configurable Parameters)
```python
# Fixed decadmiation levels (CORE CONSTRAINT)
DECADMIATION_LEVELS = [750, 1500]  # tonnes - ONLY these levels allowed
# Note: 0 means no decadmiation (all production remains standard)

# Decadmiation capability configuration (CONFIGURABLE)
# Default: All P29 lines can perform decadmiation
DECADMIATION_CAPABILITY = {
    'default_enabled_lines': ['13AB', '13CD', '13XY', '13ZU', '13E', '13F'],
    'configurable': True,
    'note': 'Can be configured to enable/disable decadmiation for specific lines'
}

# Example configurations:
DECADMIATION_SCENARIOS = {
    'all_lines_enabled': ['13AB', '13CD', '13XY', '13ZU', '13E', '13F'],
    'limited_lines': ['13AB', '13CD', '13XY'],  # Only some lines can decadmiate
    'single_line': ['13E'],  # Only one line configured for decadmiation
    'no_decadmiation': []  # All lines produce only standard acid
}

# Operational rules:
DECADMIATION_RULES = {
    'enabled_lines': 'Can choose 0, 750, or 1500 tonnes decadmiation per day',
    'disabled_lines': 'Can only produce standard acid (decadmiation = 0)',
    'production_split': 'standard_acid = total_production - decadmiation_amount',
    'storage_requirement': 'Both acid types can be stored in same tanks'
}
```

### Clarification Configuration (Configurable Parameters)
```python
# Clarification process parameters
CLARIFICATION_YIELD = 0.90     # 90% CL + 10% sludge return to P29
CLARIFICATION_SLUDGE = 0.10    # 10% returns to P29 as standard acid

# Clarification capability configuration (CONFIGURABLE)
# Default: All P54 lines can perform clarification
CLARIFICATION_CAPABILITY = {
    'default_enabled_lines': ['14AB', '14CD', '14XY', '14ZU', '14EXT'],
    'configurable': True,
    'note': 'Can be configured to enable/disable clarification for specific lines'
}

# Clarification capacity limits per line
CLARIFICATION_CAPACITY_PER_DECANTER = 500  # T/h per decanter
DECANTERS_PER_LINE = 2                     # 2 decanters per line  
HOURS_PER_DAY = 24
MAX_CLARIFICATION_PER_LINE = 1000  # tonnes/day (500 * 2 decanters)

# Example configurations:
CLARIFICATION_SCENARIOS = {
    'all_lines_enabled': ['14AB', '14CD', '14XY', '14ZU', '14EXT'],
    'limited_lines': ['14AB', '14CD'],  # Only some lines can clarify
    'high_capacity_only': ['14AB', '14EXT'],  # Only high-capacity lines
    'no_clarification': []  # No clarification available
}

# Operational rules:
CLARIFICATION_RULES = {
    'enabled_lines': 'Can send NCL acid to clarification up to capacity limit',
    'disabled_lines': 'Cannot perform clarification (NCL only for direct use or CoC)',
    'capacity_constraint': 'clarification_amount ≤ 1000 tonnes/day per enabled line',
    'yield_rule': 'clarified_output = 0.9 * ncl_input, sludge_return = 0.1 * ncl_input'
}
```

### Co-crystallization Configuration
```python
# Fixed co-crystallization echelon assignment (CORE CONSTRAINT)
COCRYSTALLIZATION_ECHELON_ENABLED = {
    'EXT': {'E': True, 'F': True, 'G': True, 'H': True},  # All 4 echelons default 
    'AB': {
        'I': True, 'J': True,           # CoC echelons
        'A': False, 'B': False, 'K': False, 'L': False  # Regular NCL echelons
    }
}

# Co-crystallization yield and process rules
COCRYSTALLIZATION_YIELD = 0.80     # 80% CoC + 20% sludge
COCRYSTALLIZATION_SLUDGE = 0.20    # 20% returns to P54 NCL

# **Critical Rule**: When echelons are enabled for CoC, they process ALL their NCL acid
# This is systematic operation, not demand-driven from fertilizer
# CoC production = NCL_input × 0.8 (no fixed capacity limits)
```

---

## QUALITY PROFILES

### Acid Types (Core System Types)
```python
ACID_TYPES = [
    'acid_29_std',      # Standard 29% acid
    'acid_29_dec',      # Decadmiated 29% acid
    'acid_54_ncl',      # Non-clarified 54% acid
    'acid_54_cl',       # Clarified 54% acid (from IR12)
    'acid_54_dec_cl',   # Decadmiated clarified 54% acid (from IR11)
    'acid_54_coc'       # Co-crystallized 54% acid (from IR11)
]
```

### Key Fertilizer Quality Profiles (Test Reference)
```python
# From quality_profiles_v2.json - exact values used in test system
QUALITY_PROFILES_TEST = {
    "MAP_11_52_SPECIAL": {
        "acid_29_std": 0.625,     # 625 kg acid 29 std per tonne MAP
        "acid_29_dec": 0.0,
        "acid_54_ncl": 0.0,
        "acid_54_cl": 0.0,
        "acid_54_dec_total": 0.0,
    },
    "DAP_EURO": {
        "acid_29_std": 0.0,
        "acid_29_dec": 0.12,      # 120 kg acid 29 dec per tonne DAP
        "acid_54_ncl": 0.0,
        "acid_54_cl": 0.0,
        "acid_54_dec_total": 0.109,  # 109 kg dec_total per tonne DAP
    },
    "NPK_14_18_18_6S_1B2O3_AFRIQUE": {
        "acid_29_std": 0.0,
        "acid_29_dec": 0.0,
        "acid_54_ncl": 0.0,
        "acid_54_cl": 0.0,
        "acid_54_dec_total": 0.513,  # 513 kg dec_total per tonne NPK
    }
}
# **Critical**: acid_54_dec_total can be supplied by EITHER:
# - acid_54_dec_cl (from IR11)
# - acid_54_coc (from IR11)
# The sum of both must equal the dec_total requirement

# **Acid Type Mapping**: Quality profiles use different names than model variables
# Quality Profile → Model Variable:
# - "acid_29" → "acid_29_std" (standard 29% acid)
# - "acid_29_dec" → "acid_29_dec" (decadmiated 29% acid)
# - "acid_54_ncl" → "acid_54_ncl" (non-clarified 54% acid)
# - "acid_54_cl" → "acid_54_cl" (clarified 54% acid)
# - "acid_54_dec_total" → "acid_54_dec_cl" OR "acid_54_coc" (combined requirement)
```
```

### Consumer Acid Types (What Each Consumer Needs)
```python
CONSUMER_ACID_TYPES = {
    'EMAPHOS': ['54_NCL'],                    # ONLY NCL acid
    'U53': ['54_CL'],                         # ONLY CL acid from IR12
    'IMACID': ['29_STD'],                     # ONLY standard 29 acid
    'MAPS': ['29_STD'],                       # ONLY standard 29 acid
    'JFC1-5': ['29_STD'],                     # ONLY standard 29 acid
    '107DEF': ['29_STD', '54_CL', '54_COC']   # Multiple types allowed
}
```

---

## ACID TYPES AND STOCK MANAGEMENT

### P29 Acid Types (29% Concentration)
```python
# P29 acid types that can be produced and stored
P29_ACID_TYPES = {
    'acid_29_std': {
        'description': 'Standard 29% phosphoric acid',
        'production': 'Always produced: total_production - decadmiation_amount',
        'storage': 'Can be stored in P29 line tanks',
        'uses': 'Fertilizer production, concentration to P54, direct consumers'
    },
    
    'acid_29_dec': {
        'description': 'Decadmiated 29% phosphoric acid (reduced cadmium)',
        'production': 'Only when decadmiation enabled: 0, 750, or 1500 tonnes/day',
        'storage': 'Can be stored in P29 line tanks (shares capacity with standard)',
        'uses': 'Specific fertilizer formulations requiring low-cadmium acid'
    }
}

# Stock management rules
P29_STOCK_MANAGEMENT = {
    'shared_capacity': 'acid_29_std_stock + acid_29_dec_stock ≤ tank_capacity per line',
    'separate_tracking': 'Each acid type tracked independently',
    'inventory_balance': 'initial_stock + production = final_stock + usage + transfers',
    'minimum_stock': 'Typically maintain some minimum level for operational flexibility'
}
```

### P54 Acid Types (54% Concentration)
```python
# P54 acid types in the system
P54_ACID_TYPES = {
    'acid_54_ncl': {
        'description': 'Non-clarified 54% phosphoric acid',
        'production': 'From P29 concentration (yield varies by line)',
        'storage': 'Stored at P54 production lines',
        'processing': 'Can be sent to clarification or co-crystallization',
        'uses': 'Direct to fertilizer, processing input'
    },
    
    'acid_54_cl': {
        'description': 'Clarified 54% phosphoric acid',
        'production': 'From NCL clarification (90% yield)',
        'storage': 'Central storage IR12 only',
        'uses': 'Fertilizer production, direct consumers'
    },
    
    'acid_54_coc': {
        'description': 'Co-crystallized 54% phosphoric acid',
        'production': 'From NCL co-crystallization (80% yield)',
        'storage': 'Central storage IR11 only',
        'uses': 'Fertilizer production, direct consumers'
    },
    
    'acid_54_dec_cl': {
        'description': 'Decadmiated clarified 54% phosphoric acid',
        'production': 'From decadmiated NCL clarification (90% yield)',
        'storage': 'Central storage IR11 only (no local storage)',
        'uses': 'Specific fertilizer formulations requiring low-cadmium clarified acid'
    },
    
    'acid_54_dec_total': {
        'description': 'Combined decadmiated 54% acid types',
        'composition': 'Sum of all decadmiated P54 acids available',
        'note': 'Used in quality profiles to specify total decadmiated P54 requirement'
    }
}
```

---

## CORE FIXED REFERENCE VALUES

### Real System Initial Conditions (Current Reference)
```python
# Real system initial stocks (converted from heights using correct conversion formulas)
REAL_INITIAL_STOCK_29 = {
    '13AB': 790.2,    # get_vol_29(13.75)
    '13CD': 387.9,    # get_vol_29(6.75)
    '13XY': 290.2,    # get_vol_29(5.05)
    '13ZU': 816.0,    # get_vol_29(14.20)
    '13E': 442.5,     # get_vol_29(7.70)
    '13F': 827.7      # get_vol_29(14.40)
}

REAL_INITIAL_STOCK_54_NCL = {
    '14AB': 901.1,    # get_vol_54(11.43)
    '14CD': 369.0,    # get_vol_54(4.68)
    '14XY': 298.0,    # get_vol_54(3.78)
    '14ZU': 918.4,    # get_vol_54(11.65)
    '14EXT': 220.7    # get_vol_54(2.80)
}

REAL_INITIAL_CENTRAL_STORAGE = {
    'IR11': 5500.8,   # get_vol_54_IR11(9.38) - Combined CoC + DEC_CL using CORRECT formula
    'IR12': 4004.1    # get_vol_54_IR12(9.14) - Clarified acid using CORRECT formula
}
```

### Real System Demand (Current Reference)
```python
# Direct acid demand (tonnes) - from hybrid_real_scenario.py
REAL_ACID_DEMAND = {
    'IMACID': {'acid_29_std': 700},
    'EMAPHOS': {'acid_54_ncl': 700},
    'MAPS': {'acid_29_std': 0},
    'U53': {'acid_54_cl': 1500},
    '107DEF': {'acid_29_std': 0, 'acid_54_cl': 0, 'acid_54_coc': 0},
    'JFC1-5': {'acid_29_std': 0}
}

# Fertilizer demand (tonnes of fertilizer) - from hybrid_real_scenario.py
REAL_FERTILIZER_DEMAND = {
    'U16': {
        'DAP_STANDARD': 3057,
        'TSP_EURO': 1200
    },
    'U116A': {
        'MAP_11_54_NE_EU': 3037
    },
    'U116BC': {
        'NPK_12_24_12_EU': 1540,
        'NPK_15_15_15_EU_20_MGKP2O5': 2126
    }
}

# Real P29 Production (tonnes/day) - from hybrid_real_scenario.py
REAL_P29_PRODUCTION = {
    '13AB': 1500,
    '13CD': 1500,
    '13XY': 1500,
    '13ZU': 800,
    '13E': 1500,
    '13F': 1500
}
```

### Real System Working Hours (Current Reference)
```python
REAL_ECHELON_WORKING_HOURS = {
    # EXT echelons (all enabled for co-crystallization) - from hybrid_real_scenario.py
    "E": 24, "F": 24, "G": 24, "H": 14,
    
    # AB echelons (I,J for CoC; A,K,B,L for regular)
    "I": 24, "J": 14, "A": 24, "K": 24, "B": 24, "L": 24,
    
    # CD echelons (no co-crystallization)
    "C": 24, "M": 24, "D": 24, "N": 24,
    
    # XY echelons (no co-crystallization)
    "X": 14, "P": 14, "Y": 24, "Q": 24,
    
    # ZU echelons (no co-crystallization)
    "Z": 14, "R": 14, "U": 24, "S": 24, "V": 24, "W": 0
}
```

---

**This document contains the complete set of core fixed elements that define the phosphoric acid optimization system. These values are extracted directly from the core implementation files and represent the exact constraints and parameters that any AI tool must use to rebuild the model accurately.**
