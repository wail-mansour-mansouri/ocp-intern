# Comprehensive System Simulation: Full Pipeline Example
## Complete A-to-Z Calculation with All System Components

### Initial Setup and Configuration

**Line Capabilities Configuration**:
- **DEC 29 Enabled**: 13CD, 13XY (can produce acid 29 dec)
- **NCL Clarification Enabled**: 14CD, 14ZU (can clarify NCL to CL)  
- **DEC CL Enabled**: 14XY (can send dec to concentration for clarification)

**Fixed Production (P29)**:
```
13AB: 1500 tonnes/day
13CD: 1500 tonnes/day
13XY: 1500 tonnes/day
13ZU: 800 tonnes/day
13E: 1500 tonnes/day
13F: 1500 tonnes/day
Total: 8,300 tonnes/day
```

**Initial Stocks**:
```
P29 Standard: 13AB(790), 13CD(388), 13XY(290), 13ZU(816), 13E(443), 13F(828) = 3,555 tonnes
P29 Dec: 13CD(345), 13XY(457) = 802 tonnes
P54 NCL: 14AB(901), 14CD(369), 14XY(298), 14ZU(918), 14EXT(221) = 2,707 tonnes
IR11 (CoC+DEC_CL): 5,501 tonnes
IR12 (CL): 4,004 tonnes
```

**Working Hours (Echelons)**:
```
14EXT: E(24h), F(24h), G(24h), H(14h) → All 4 for CoC
14AB: I(24h), J(14h), A(24h), K(24h) for CoC; B(24h), L(24h) for NCL
14CD: C(24h), M(24h), D(24h), N(24h) → All NCL
14XY: X(14h), P(14h), Y(24h), Q(24h) → All NCL
14ZU: Z(14h), R(14h), U(24h), S(24h), V(24h), W(0h) → All NCL
```

**Demands**:
```
Direct Industrial:
- IMACID: 700 tonnes acid_29_std
- EMAPHOS: 700 tonnes acid_54_ncl
- U53: 1500 tonnes acid_54_cl (from IR12)

Fertilizer (after quality profile conversion):
- U16: DAP(388 t acid_29_std, 1082 t acid_54_ncl), TSP(455 t acid_54_dec_total)
- U116A: MAP(91 t acid_29_dec, 392 t acid_54_dec_total)
- U116BC: NPK1(140 t acid_54_dec_total), NPK2(364 t acid_29_dec)

Total Acid Requirements:
- acid_29_std: 1,088 tonnes
- acid_29_dec: 455 tonnes
- acid_54_ncl: 1,782 tonnes
- acid_54_cl: 1,500 tonnes (IR12)
- acid_54_dec_total: 987 tonnes (IR11)
```

### Step 1: P54 Production Calculation (Deterministic)

**Formula**: P54 = Σ(Capacity × Working_Hours / 24)

```
14AB: (300×24 + 300×24 + 590×24 + 590×14 + 300×24 + 300×24)/24 = 2,077 tonnes NCL
14CD: (250×24 + 250×24 + 290×24 + 250×24)/24 = 1,040 tonnes NCL
14XY: (300×14 + 250×14 + 250×24 + 250×24)/24 = 779 tonnes NCL
14ZU: (250×14 + 300×24 + 250×14 + 300×24 + 590×24 + 590×0)/24 = 1,375 tonnes NCL
14EXT: (420×24 + 420×24 + 420×24 + 420×14)/24 = 1,365 tonnes NCL

Total P54 Production: 6,636 tonnes/day NCL
```

### Step 2: Systematic Co-crystallization (Deterministic)

**14EXT (All 4 echelons)**:
- Input: 1,365 tonnes NCL
- Output: 1,092 tonnes CoC (80% yield) → IR11
- Sludge: 273 tonnes (20%) → returns to 13E P29 standard stock

**14AB (I,J,A,K echelons for CoC)**:
- I,J,A,K production: (590×24 + 590×14 + 300×24 + 300×24)/24 = 1,535 tonnes NCL
- Output: 1,228 tonnes CoC (80% yield) → IR11
- Sludge: 307 tonnes (20%) → returns to 13AB P29 standard stock
- Remaining NCL from B,L: 600 tonnes (available for other uses)

**Total Systematic CoC**: 2,320 tonnes → IR11

### Step 3: Concentration Planning (P29 → P54)

**P29 Available for Concentration**:
```
Line     Initial_Stock + Production = Available_P29
13AB     790          + 1500       = 2,290 tonnes
13CD     388          + 1500       = 1,888 tonnes  
13XY     290          + 1500       = 1,790 tonnes
13ZU     816          + 800        = 1,616 tonnes
13E      443          + 1500       = 1,943 tonnes
13F      828          + 1500       = 2,328 tonnes
Total Available P29: 12,855 tonnes
```

**P54 Planned Production** (from working hours - Step 1):
```
14AB:  2,077 tonnes P54 planned (requires 2,077 tonnes P29)
14CD:  1,040 tonnes P54 planned (requires 1,040 tonnes P29)
14XY:    779 tonnes P54 planned (requires 779 tonnes P29)
14ZU:  1,375 tonnes P54 planned (requires 1,375 tonnes P29)
14EXT: 1,365 tonnes P54 planned (requires 1,365 tonnes P29)
Total P54 Planned: 6,636 tonnes (requires 6,636 tonnes P29)
```

**P29 Balance Check**:
```
Line     Available - P54_Required = Surplus_for_Other_Uses
13AB     2,290    - 2,077        = 213 tonnes
13CD     1,888    - 1,040        = 848 tonnes
13XY     1,790    - 779          = 1,011 tonnes
13ZU     1,616    - 1,375        = 241 tonnes
13E      1,943    - 1,365        = 578 tonnes  
13F      2,328    - 0            = 2,328 tonnes (no P54 line)
Total Surplus: 5,219 tonnes (available for decadmiation, fertilizer, transfers)
```

### Step 4: Decadmiation Planning (Optimization Decision)

**Need acid_54_dec_total**: 987 tonnes (from IR11)
- Current IR11 stock has CoC and DEC_CL
- **Mandatory DEC CL Production**: Even though systematic CoC production (2,320 tonnes) is very high and could theoretically meet all acid_54_dec_total demands, DEC CL production is mandatory for process quality
- **Quality Consideration**: IR11 must contain a mix of CoC and DEC CL. Without DEC CL, IR11 would contain only CoC, which decreases acid quality
- **Process Logic**: The optimizer cannot simply rely on high CoC production and skip DEC CL - some DEC CL must be produced

**Decision Variables**:
- 13CD can decadmiate: 0, 750, or 1500 tonnes
- 13XY can decadmiate: 0, 750, or 1500 tonnes

**For acid_29_dec needs (455 tonnes)**:
- Must come from 13CD or 13XY dec stocks + new decadmiation

**For DEC_CL needs**:
- Only 14XY can produce DEC_CL (has DEC CL capability)
- To get X tonnes DEC_CL: need X/0.9 tonnes P54 NCL DEC input

**Decanter Limitation Impact**:
- If 14XY decadmiates 1500 tonnes but decanters can only clarify 1000 tonnes:
  - Send 1000/0.9 = 1111 tonnes to clarification → ~1000 tonnes DEC_CL
  - Remaining 1500 - 1111 = 389 tonnes stays as acid 29 dec in storage
- This example shows how decanter capacity limits affect high decadmiation levels

**Optimization Logic (Conservative Approach)**:
1. 13CD decadmiates 750 tonnes → 455 to fertilizer, 295 to storage
2. 13XY decadmiates 750 tonnes → send to concentration for DEC_CL
   - 750 tonnes P29 DEC → 750 tonnes P54 NCL DEC
   - 750 tonnes P54 NCL DEC → 675 tonnes DEC_CL + 75 tonnes sludge to P29

### Step 5: Clarification Planning with Shared Constraint

**Need for IR12**: 1,500 tonnes CL (for U53 demand)
- Required NCL input: 1,500/0.9 = 1,667 tonnes

**14XY Clarification Balance**:
- Mandatory DEC clarification: 750 tonnes (P54 NCL DEC → DEC CL)
- Remaining decanter capacity: 1000 - 750 = 250 tonnes available
- NCL clarification capacity used: 0 tonnes (not needed since other lines handle CL demand)

**Clarification Distribution for CL Production**:
- 14CD: 1,000 tonnes NCL → 900 tonnes CL (full capacity)
- 14ZU: 667 tonnes NCL → 600 tonnes CL
- 14XY: 0 tonnes NCL → 0 tonnes CL (capacity reserved for DEC)
- Total: 1,667 tonnes NCL → 1,500 tonnes CL ✓

### Step 6: EMAPHOS Processing (Special Case)

**EMAPHOS receives**: 700 tonnes P54 NCL
**Returns** (40% total):
- ARP1 to 13AB: 87.5 tonnes (12.5%)
- ARP2 to 13CD: 87.5 tonnes (12.5%)
- Sludge to 13XY: 105 tonnes (15%)

### Step 7: Interzone Transfers (If Needed)

Check if any P29 line needs transfers to feed P54 production:
- 13AB needs to send: 2,077 tonnes to 14AB
- 13CD needs to send: 1,040 tonnes to 14CD
- 13XY needs to send: 779 + 750 (DEC) = 1,529 tonnes to 14XY
- 13ZU needs to send: 1,375 tonnes to 14ZU
- 13E needs to send: 1,365 tonnes to 14EXT

**Transfer Analysis**: 
- 13XY might need transfers IN as it needs 1,529 but only produces 1,500
- Can receive from 13CD or 13ZU based on matrix

### Step 8: Final Mass Balance

**P29 Level**:
```
Line    Initial + Production + EMAPHOS_Returns + CoC_Sludge + Clarif_Sludge - Decad - To_P54 - To_Fert = Final
13AB    790    + 1500      + 87.5            + 307         + 0             - 0     - 2077   - 0      = 607.5
13CD    388    + 1500      + 87.5            + 0           + 167           - 750   - 1040   - 0      = 352.5
13XY    290    + 1500      + 105             + 0           + 108           - 750   - 779    - 0      = 474
13ZU    816    + 800       + 0               + 0           + 42            - 0     - 1375   - 0      = 283
13E     443    + 1500      + 0               + 273         + 0             - 0     - 1365   - 700    = 151
13F     828    + 1500      + 0               + 0           + 0             - 0     - 0      - 388    = 1940
```

**P54 Level** (Note: Sludge now returns to P29, not P54):
```
Line     Initial + From_P29 - CoC   - Clarif - To_Fert = Final
14AB     901    + 2077     - 1228  - 0      - 1082    = 668
14CD     369    + 1040     - 0     - 1000   - 0       = 409
14XY     298    + 1529     - 0     - 1000   - 0       = 827
14ZU     918    + 1375     - 0     - 417    - 700     = 1176
14EXT    221    + 1365     - 1092  - 0      - 0       = 494
```

**Central Storage**:
```
IR11: 5501 + 2320(CoC) + 675(DEC_CL) - 987(to_fert) = 7509
IR12: 4004 + 1500(CL) - 1500(to_fert) = 4004
```

### Key Findings and System Optimization

1. **P29 Balance**: With sludge returns to P29, all lines maintain positive stock levels
2. **Fertilizer Delivery Optimization**: Redistributed 1,082 tonnes fertilizer delivery from 14EXT to 14AB to avoid stock violation
3. **Line Utilization**: 14AB efficiently handles additional delivery due to high available stock (1750 → 668 tonnes final)
4. **Mandatory DEC CL**: Despite high CoC production (2,320 tonnes), DEC CL production remains mandatory for quality reasons
5. **Decanter Constraint Impact**: 14XY limited to 250 tonnes NCL clarification due to mandatory 750 tonnes DEC clarification
6. **Stock Distribution**: Final stocks well-distributed across lines, avoiding bottlenecks

### Feasibility Conclusion

The scenario demonstrates the full system complexity:
- **Deterministic Components**: P29 production, P54 production, systematic CoC are fixed based on inputs
- **Optimization Decisions**: Decadmiation levels, clarification distribution, interzone transfers
- **Process Constraints**: Capacity limits, yield factors, interconnection matrices, transfer bounds
- **Special Processes**: EMAPHOS returns, sludge recycling, mandatory processing sequences
- **Stock Management**: Multiple acid types across local and central storage systems
- **Demand Satisfaction**: Direct industrial + fertilizer demands with quality profile conversion

Key system interactions:
- P29 decadmiation decisions affect P54 clarification capacity
- Systematic CoC competes with manual clarification for NCL input
- Central storage (IR11/IR12) serves as distribution hubs
- Mass balance must be maintained across all process levels
- Line capabilities determine feasible process configurations
- Delivery optimization leverages stock levels across lines to avoid violations

This comprehensive example demonstrates how the phosphoric acid optimization system integrates production planning, process control, and distribution logistics in a complex industrial setting requiring careful coordination of all subsystems.