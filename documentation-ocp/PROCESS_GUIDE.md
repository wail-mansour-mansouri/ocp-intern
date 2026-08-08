# PHOSPHORIC ACID INDUSTRIAL PROCESS FLOW GUIDE

## Purpose
This document describes the **actual industrial process flow** for the phosphoric acid production and distribution system. This is the definitive reference for how the physical/chemical process operates in reality, serving as the truth standard that any optimization software must follow.

**Important**: This document describes the real-world industrial process, not software or optimization logic.

---

## PROCESS OVERVIEW

The phosphoric acid production system consists of a two-stage process:

1. **P29 Production**: Raw phosphoric acid production (29% P2O5)
2. **P54 Production**: Concentrated phosphoric acid production (54% P2O5)

Both stages include processing options (decadmiation, clarification, co-crystallization) and feed a distribution network serving fertilizer plants and industrial customers.

---

## 1. P29 ACID PRODUCTION STAGE

### 1.1 Production Lines
Six production lines produce P29 acid (29% P2O5):
- **13AB, 13CD, 13XY, 13ZU, 13E, 13F**

### 1.2 Production Capabilities
Each line can produce:
- **Standard P29 acid** (regular phosphoric acid)
- **Decadmiated P29 acid** (cadmium-reduced acid)

### 1.3 Decadmiation Process
- **What it is**: A purification process that removes cadmium contamination from phosphoric acid
- **When it happens**: At the P29 stage, after production
- **Result**: Decadmiated P29 acid with reduced cadmium content
- **Use**: Required for certain high-purity fertilizer quality profils 
- **Production Levels**: Decadmiation operates at fixed levels (750 tonnes or 1500 tonnes) using 1 or 2 filters respectively
- **Control**: The Production of Acid 29 is systematic (depends on capacity), but decadmiation depends on fertilizer needs
- **Optimization Note**: We don't act on P29 production (fixed inputs) but we can act on P29dec based on fertilizer needs

### 1.4 Local Storage
- Each P29 line has its own storage tank for acid standard or decadmiated
- Standard and decadmiated acids are stored separately
- Sludge from downstream processes returns to the standard tanks

### 1.5 Interzone Transfers
- P29 acid can be transferred between production lines
- Purpose: Balance inventory (depletion and overfill) and to feed the production of acid 54 with the acid 29 needed. 
- **Important**: Only for standard P29 acid, not decadmiated acid
- **Reason**: Decadmiated acid is processed immediately and cannot be transferred between lines
- **Constraints**: Not every line is linked, so there are interconnection constraints
- **Minimum Transfer**: There are minimum amounts required for interzone balancing (e.g., can't suggest sending 4 tonnes from AB to CD)
- **Maximum Transfer**: There are maximum amounts reqired for interzone balancing (e.g., can't suggest sending 4000 tonnes from AB to CD)

---

## 2. P54 ACID PRODUCTION STAGE

### 2.1 Concentration Process
- **Input**: P29 acid (standard or decadmiated) from any P29 line
- **Process**: Concentration to 54% P2O5 performed by echelons
- **Output**: P54 acid (Non-Clarified = NCL)
- **Yield**: 100% mass transfer (1 ton P29 → 1 ton P54)
- **Echelons**: Physical concentration units that convert P29 to P54
- **Production Formula**: P54u(E) = C × wh / 24 (where C = capacity, wh = working hours)

### 2.2 Production Line Mapping
P29 lines feed specific P54 lines:
- **13AB** → **14AB**
- **13CD** → **14CD**
- **13XY** → **14XY**
- **13ZU** → **14ZU**
- **13E** → **14EXT**
- **13F** → No P54 line (direct P29 use only)

### 2.3 Decadmiated Acid Processing with Decanter Limitations
**Industrial Rule**: When decadmiated P29 acid is concentrated:
- It becomes decadmiated P54 NCL (P54 NCL DEC)
- It is **always clarified** immediately after concentration (subject to decanter limitations)
- Result: Decadmiated Clarified P54 (DEC_CL) sent directly to IR11 central storage
- **Critical**: We never send decadmiated acid without clarification (no local storage for P54 NCL DEC)
- **Process Sequence**: Decadmiation (at P29) → Concentration → P54 NCL DEC → Mandatory Clarification → DEC_CL → IR11
- **No Local Storage**: P54 NCL DEC is not stored locally - it goes directly through clarification to IR11
- **Key Principle**: All decadmiated acid 54 must be clarified before use

**Important Decanter Limitation**: 
- The total clarification capacity is shared between NCL clarification and DEC clarification
- Maximum clarification per line: 1000 tonnes/day (2 decanters × 500 tonnes each)
- This 1000 tonnes limit applies to the combined clarification of NCL and DEC acid
- The optimizer must respect this shared capacity constraint

---

## 3. P54 ACID PROCESSING OPTIONS

### 3.1 Clarification Process
- **Purpose**: Remove impurities from NCL acid
- **Input**: NCL P54 acid from local stock
- **Process**: Physical/chemical separation of impurities
- **Output**: 
  - 90% Clarified acid (CL) → sent to IR12 central storage
  - 10% Sludge → returns to corresponding P29 standard acid stock
- **Availability**: All P54 lines (14AB, 14CD, 14XY, 14ZU, 14EXT)
- **Capacity**: Each line has 2 decanters with maximum capacity of 500 tonnes/day each
- **Total Clarification Limit**: 1000 tonnes/day per line (before yield)
- **Shared Capacity**: This 1000 tonnes limit is shared between:
  - Manual NCL clarification (NCL → CL)
  - Mandatory DEC clarification (P54 NCL DEC → DEC CL)
- **Critical Constraint**: Total clarification (NCL + DEC) ≤ 1000 tonnes/day per line

### 3.2 Co-crystallization Process
- **Purpose**: Produce ultra-high-purity crystallized acid
- **Input**: NCL P54 acid from local stock
- **Process**: Crystallization to remove trace impurities
- **Output**:
  - 80% Co-crystallized acid (CoC) → sent to IR11 central storage
  - 20% Sludge → returns to corresponding P29 standard acid stock
- **Availability**: Only lines 14EXT and 14AB (not necessarily all their acid 54 production get processed)
- **Key Restriction**: We don't co-crystallize decadmiated acid or clarified acid only ncl acid.

### 3.3 Co-crystallization Operating Philosophy
**Industrial Reality**: Co-crystallization operates systematically (based on the availability of treatment units), not on-demand:

- **Echelon System**: Echelons are the physical concentration units that produce P54 acid from P29 acid
  - **14EXT**: Has 4 echelons (E, F, G, H) - all or subset of echelons can feed co-crystallization units
  - **14AB**: Has 6 echelons (A, B, I, J, K, L) - subset of echelons (e.g., I, J, A, K) can feed co-crystallization units
- **Physical Reality**: Co-crystallization treatment units exist only in 14EXT and 14AB plants
- **Systematic Operation**: When echelons are operational, the co-crystallization units process ALL available NCL acid from the designated echelons
- **Echelon Selection** (Scenario-dependent): 
  - **14EXT**: Number of echelons feeding co-crystallization varies by scenario
  - **14AB**: Number of echelons feeding co-crystallization varies by scenario (could be 2, 4, or other combinations)
- **Not Demand-Driven**: Co-crystallization doesn't wait for CoC demand from fertilizer - it processes acid continuously when the treatment units for the designated echelons are enabled
- **Treatment Capacity**: Each co-crystallization unit processes acid from multiple echelons
- **Process Restriction**: Co-crystallized acid cannot be clarified (it serves the same purpose as DEC_CL)
- **Remaining NCL**: After systematic CoC processing, any remaining NCL from non-CoC echelons can be clarified, used directly, or stored
- **Operational Constraints**: Co-crystallization stations can sometimes be non-operational due to constraints; in this case, acid from echelons stays P54NCL and is ready for other processing (clarification) or direct use or storage.

### 3.4 Line Processing Capabilities
**Three Types of Line Capabilities**:

1. **DEC 29 Enabled Lines**:
   - Lines that can produce decadmiated acid 29 to meet fertilizer demand
   - The decadmiated acid 29 can be stored in dedicated P29 DEC tanks
   - If the line also has P54 production but no DEC CL capability, the remaining DEC acid after fertilizer needs stays in P29 DEC storage
   - Example lines: CD and XY (contain filters dedicated to meet acid 29 dec fertilizer needs)

2. **NCL Clarification Enabled Lines**:
   - Lines that can clarify their NCL produced acid to acid 54 CL
   - This clarification uses the decanter capacity (max 1000 tonnes/day per line)
   - The clarified acid (CL) is sent to IR12 central storage
   - Example lines: CD and ZU

3. **DEC CL Enabled Lines (Mandatory Production)**:
   - Lines that can both decadmiate acid 29 AND concentrate it to P54 for clarification
   - The decadmiated P29 is concentrated to P54 NCL DEC and must be clarified to DEC CL
   - This mandatory clarification also uses the shared decanter capacity
   - The DEC CL is sent to IR11 central storage
   - **Process Logic**: DEC CL production is mandatory because CoC and DEC CL mix in IR11 to meet acid_54_dec_total demands
   - **Quality Consideration**: Without DEC CL production, IR11 would contain only CoC, which decreases acid quality
   - **Systematic CoC Impact**: Since systematic CoC production is already high, the optimizer might avoid DEC CL production, but this violates process logic
   - **Decanter Limitation with High Decadmiation**: If line decadmiates 1500 tonnes but decanters can only handle 1000 tonnes:
     - Send 1000/0.9 = 1111 tonnes to clarification → ~1000 tonnes DEC CL
     - Remaining ~389 tonnes stays as acid 29 dec in storage
   - Example line: XY

**Important Notes**:
- A line can have multiple capabilities (e.g., XY has both DEC 29 and DEC CL capabilities)
- The 1000 tonnes/day clarification limit is shared between NCL and DEC clarification
- The optimizer must determine which lines to use for each purpose based on demand and constraints
- A line could theoretically have all three capabilities if configured appropriately

### 3.5 Acid Types Summary
**Total Acid Types**: We have 4 types of Acid 54:
- **P54NCL**: Non-clarified acid
- **P54CL**: Clarified acid
- **P54DEC_CL**: Decadmiated clarified acid
- **P54CoC**: Co-crystallized acid (equivalent to P54 acid dec CL)

---

## 4. CENTRAL STORAGE SYSTEM

### 4.1 IR11 Storage Tank
**Contents**:
- Co-crystallized acid (CoC) from 14EXT and 14AB
- Decadmiated Clarified acid (DEC_CL) from all P54 lines

**Function**: Strategic storage for high-value, high-purity acid products

**Stock Balance Formula**:
```
IR11 = initial_IR11 + P54(coc) - P54(coc to fertilizer) + P54(dec_cl) - P54(dec_cl to fertilizer)
```

### 4.2 IR12 Storage Tank
**Contents**:
- Regular clarified acid (CL) from all P54 lines

**Function**: Primary storage for standard clarified acid

**Stock Balance Formula**:
```
IR12 = initial_IR12 + P54(CL) - P54(CL to fertilizer)
```

### 4.3 Local Storage
**P54 Local Storage**:
- Each line has two storage tanks:
  - **ACP54NCL**: For non-clarified acid
  - **ACP54DEC**: For decadmiated acid (if exists)

**Stock Balance Formulas**:
```
Z54(NCL) = Z54(i) + P54(NCL) - P54(NCL to fertilizer)
Z54(dec) = Z54(i) + P54(dec) - P54(dec to fertilizer)
```

**Note**: We don't account sludge in P54 stock calculations because sludge created at P54 level gets returned to P29 storage.

---

## 5. DISTRIBUTION AND CONSUMPTION

### 5.1 Acid Supply Sources
Consumers can receive acid from:
- **Direct from P29 lines** (standard or decadmiated P29)
- **Direct from P54 lines** (NCL or DEC_CL)
- **From IR12 central storage** (CL)
- **From IR11 central storage** (CoC or DEC_CL)

**Key Principle**: We don't send processed acid directly from lines - they get sent either from IR11 or IR12

### 5.2 Fertilizer Consumers
Various fertilizer production units requiring specific acid types and purities based on their product specifications.

**Fertilizer Profile System**:
- Fertilizers (U16, U116A, U116BC) express requirements with quality profiles
- Each profile specifies amounts of different acid types:
  - x1 = Amount Acid 29 std
  - x2 = Amount Acid 29 dec
  - y1 = Amount Acid 54 NCL
  - y2 = Amount Acid 54 CL
  - y3 = Amount Acid 54 dec
  - y4 = Amount Acid 54 coc

### 5.3 Industrial Acid Consumers
- **IMACID**: Uses P29 acid only
- **EMAPHOS**: Uses P54 acid only
- **MAPS**: Uses P29 acid only  
- **U53**: Uses clarified P54 acid from IR12
- **107DEF**: Can use either P29 standard or clarified P54 (IR12) acid or cocristallized acid (IR11)
- **JFC1-5**: Uses P29 acid only

### 5.4 EMAPHOS Processing Details
**Industrial Reality**: EMAPHOS is a special consumer that processes P54 NCL acid and returns sludge to P29 storage:

**EMAPHOS Process Flow**:
- **Input**: EMAPHOS receives P54 NCL acid directly from production lines (14ZU, 14XY, 14AB)
- **Processing**: 100% of received acid is processed by EMAPHOS
- **Returns**: 40% of processed acid returns as sludge to P29 storage:
  - **ARP1**: 12.5% → returns to 13AB acid 29 standard storage
  - **ARP2**: 12.5% → returns to 13CD acid 29 standard storage  
  - **Extra Sludge**: 15% → returns to 13XY acid 29 standard storage
- **Mass Balance**: Total returns = 40% (12.5% + 12.5% + 15% = 40%)

**Example**: If EMAPHOS receives 700 tonnes P54 NCL:
- EMAPHOS gets: 700 tonnes P54 NCL (full delivery)
- ARP1 to 13AB: 700 × 0.125 = 87.5 tonnes standard acid
- ARP2 to 13CD: 700 × 0.125 = 87.5 tonnes standard acid
- Sludge to 13XY: 700 × 0.15 = 105 tonnes standard acid
- Total returns: 280 tonnes to P29 storage
- System impact: 700 tonnes delivered, 280 tonnes recovered

**Critical Modeling Points**:
- EMAPHOS consumption happens at P54 level (subtracted from P54 NCL stock)
- EMAPHOS returns happen at P29 level (added to P29 standard acid stock)
- This creates a cross-level material flow that must be carefully modeled
- Optimization focus: deliver the full amount and account for returns

---

## 6. MATERIAL BALANCE PRINCIPLES

### 6.1 Mass Conservation
- **Input = Output + Stock Change** for every process unit
- **Yield factors** are fixed based on industrial experience
- **Sludge returns** are accounted for in mass balance

### 6.2 Process Yields (Industrial Standards)
- **P29 to P54 concentration**: 100% (1:1 mass ratio)
- **P54 clarification**: 90% CL + 10% sludge
- **P54 co-crystallization**: 80% CoC + 20% sludge
- **EMAPHOS processing**: 100% product + 40% returns (25% ARP + 15% sludge eg : we send the full amount then we calculate the sluge and byproduct since the processing is done at emaphos level)
- **Decadmiation levels**: 750 tonnes (1 filter) or 1500 tonnes (2 filters)

### 6.3 Quality Segregation
- **Decadmiated acids** are kept separate from standard acids
- **Different purity levels** (P29, NCL, CL, CoC) are not mixed
- **Contamination prevention** throughout the process chain

---

## 7. OPERATIONAL CONSTRAINTS

### 7.1 Physical Constraints
- **Production capacity limits** for each line
- **Storage tank capacity limits**
- **Processing rate limits** for clarification and co-crystallization
- **Working hours** how much each echelon will stay working
- **Hourly flow rate constraints** for transferring acids to fertilizer lines or in inter-zone balancing

### 7.2 Quality Requirements
- **Acid specifications** must be met for each consumer
- **Purity levels** maintained throughout processing
- **Contamination control** especially for decadmiated products

### 7.3 Process Sequence Rules
- **Concentration before processing**: P29 must be concentrated before clarification/co-crystallization
- **Mandatory DEC clarification**: P54 NCL DEC must be clarified after concentration (no local storage)
- **Decanter capacity**: Maximum 1000 tonnes/day per line for all clarification (NCL + DEC combined)
- **Systematic co-crystallization**: Only designated echelons feed co-crystallization (4/4 for EXT, 2 for AB)
- **Co-crystallization restriction**: Co-crystallized acid cannot be clarified (serves same purpose as DEC_CL)
- **Sludge recycling**: Returns to appropriate upstream stocks
- **Decadmiation levels**: Fixed at 750 tonnes (1 filter) or 1500 tonnes (2 filters)

### 7.4 Interconnection Constraints
- **P54 NCL and DEC**: Interconnection constraints apply (not every fertilizer line is connected to every phosphoric acid line)
- **P54 CL and CoC**: No interconnection constraints since they go directly from IR11 and IR12 to all fertilizer lines
- **P29 std and dec**: Interconnection constraints apply since they are in local storage

---

## 8. PROCESS FLOW LOGIC SUMMARY

### 8.1 Normal Flow Path
1. **P29 Production** → Local storage
2. **Concentration** → P54 NCL storage
3. **Processing Options**:
   - Clarification → IR12 storage
   - Co-crystallization (systematic) → IR11 storage
   - Direct use → Consumers
4. **Distribution** → Meet consumer demands

### 8.2 Special Cases
- **Decadmiated P29**: P29 DEC → Concentration → P54 NCL DEC → Mandatory Clarification → DEC_CL → IR11 (no local storage)
- **Decanter constraint**: All clarification types share the same 1000 tonnes/day capacity per line
- **Line capabilities**: Lines can have DEC 29 only, NCL clarification only, DEC CL capability, or combinations
- **Co-crystallization**: Systematic processing when designated echelons are enabled (4/4 for EXT, 2 for AB)
- **Co-crystallization restriction**: Co-crystallized acid cannot be clarified (equivalent to DEC_CL)
- **Sludge returns**: Recycled to appropriate upstream stocks (including 15% EMAPHOS sludge to 13XY)
- **Interzone transfers**: Balance standard P29 acid between lines (decadmiated acid cannot be transferred)
- **Decadmiation levels**: Fixed production levels of 750 or 1500 tonnes

### 8.3 Optimization Setup Requirements
**For the Optimizer**:
- **P29**: Production of Acid 29 planned
- **P54**: Production of Acid 54 planned
- **S29**: Storage of Acid 29
- **S29dec**: Storage of Acid 29 dec (if exists)
- **S54**: Storage of Acid 54 NCL
- **Line Capabilities**: Specify which lines have:
  - DEC 29 capability (can produce acid 29 dec for fertilizer)
  - NCL clarification capability (can clarify NCL to CL)
  - DEC CL capability (can send dec acid to concentration for clarification)
- **Decanter constraint**: Maximum 1000 tonnes/day per line for all clarification
- **IR11**: Storage of CoC and DEC_CL
- **IR12**: Storage of clarified acid

**Manual Selections Required**:
- Selection of line capabilities (DEC 29, NCL clarification, DEC CL)
- Setup the working hours of echelons

**Optimization Goals**:
- Determine which lines to use for each capability based on demand
- Calculate the amount for decadmiation based on fertilizer demand
- Find optimal solution for acid transfers between lines
- Calculate the final stock for all storage locations

---

## CONCLUSION

This process guide describes the actual industrial process flow for phosphoric acid production and distribution. The process operates according to physical/chemical principles and industrial best practices, not software optimization logic.

**Key Principles**:
- **Mass balance** must be maintained at all process units
- **Quality segregation** prevents contamination
- **Systematic processing** (especially co-crystallization) follows industrial reality
- **Sludge recycling** maintains material efficiency
- **Consumer demands** must be met with appropriate acid types
- **Interconnection constraints** limit direct transfers between certain lines
- **Central storage distribution** for processed acids (IR11/IR12)

**For Optimization Software**: Any optimization system must follow this process flow exactly. The optimizer's job is to find the best way to operate within these industrial constraints, not to change the process itself.

---

**Document Status**: This is the definitive reference for the phosphoric acid industrial process flow. Any questions about "how the process should work" should be answered by referring to this document.
