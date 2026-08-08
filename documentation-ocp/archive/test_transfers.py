#!/usr/bin/env python3
"""
Test script for interzone transfer planning
"""

import sys
sys.path.append('.')

from core_fixed_elements import P29_LINES, Z_MIN_29, Z_MAX_29, INTER_ZONE_OPERATIONS, MIN_TRANSFER, MAX_TRANSFER

def test_transfer_planning():
    """Test the transfer planning logic with actual final stocks"""
    
    # Actual final stocks from the optimization results
    final_stocks = {
        '13AB': 160.65,
        '13CD': 1035.33,
        '13XY': 1073.75,
        '13ZU': 200.88,
        '13E': 38.99,
        '13F': 2327.95
    }
    
    # Line to zone mapping
    line_to_zone = {
        '13E': 'E', '13F': 'F', '13AB': 'AB', 
        '13CD': 'CD', '13XY': 'XY', '13ZU': 'ZU'
    }
    
    print("=== TRANSFER PLANNING TEST ===")
    print(f"Z_MIN_29: {Z_MIN_29:.1f} tonnes")
    print(f"Z_MAX_29: {Z_MAX_29:.1f} tonnes")
    print(f"MIN_TRANSFER: {MIN_TRANSFER} tonnes")
    print(f"MAX_TRANSFER: {MAX_TRANSFER} tonnes")
    
    # Step 1: Identify lines needing transfers
    excess_lines = []    # Lines that need to send out: (line, excess_amount)
    deficit_lines = []   # Lines that need to receive: (line, deficit_amount)
    
    print(f"\nStock Analysis:")
    for line in P29_LINES:
        stock = final_stocks.get(line, 0)
        if stock > Z_MAX_29:
            excess_amount = stock - Z_MAX_29
            excess_lines.append((line, excess_amount))
            print(f"  {line}: {stock:.1f} -> OVERFILLED by {excess_amount:.1f} (needs to send)")
        elif stock < Z_MIN_29:
            deficit_amount = Z_MIN_29 - stock
            deficit_lines.append((line, deficit_amount))
            print(f"  {line}: {stock:.1f} -> DEPLETED by {deficit_amount:.1f} (needs to receive)")
        else:
            print(f"  {line}: {stock:.1f} -> GREEN ZONE (OK)")
    
    # Step 2: Plan optimal transfers
    planned_transfers = {}
    
    print(f"\nPlanning optimal transfers:")
    
    # Sort by urgency (biggest violations first)
    excess_lines.sort(key=lambda x: x[1], reverse=True)
    deficit_lines_copy = deficit_lines.copy()
    deficit_lines_copy.sort(key=lambda x: x[1], reverse=True)
    
    for from_line, excess_needed in excess_lines:
        # Process all lines that are overfilled, even if excess < MIN_TRANSFER
        # They can still send MIN_TRANSFER to help balance the system
        if excess_needed <= 0:
            continue
            
        from_zone = line_to_zone.get(from_line)
        if not from_zone:
            continue
        
        # For lines with small excess, they can still send MIN_TRANSFER to help system balance
        can_send = max(excess_needed, MIN_TRANSFER) if excess_needed > 0 else 0
        remaining_to_send = can_send
        print(f"\n  Planning transfers from {from_line} (excess: {excess_needed:.1f}, can send: {can_send:.1f}):")
        
        # First priority: help deficit lines
        for i, (to_line, deficit_needed) in enumerate(deficit_lines_copy):
            if remaining_to_send < MIN_TRANSFER:
                continue
            # Allow small deficit transfers if we have excess capacity
            if deficit_needed <= 0:
                continue
                
            to_zone = line_to_zone.get(to_line)
            if not to_zone:
                continue
            
            # Check if transfer is allowed
            allowed = INTER_ZONE_OPERATIONS[from_zone].get(to_zone, '-')
            if allowed == 'x':
                # Calculate optimal transfer amount - strategic distribution to leave room for other senders
                if deficit_needed < MIN_TRANSFER:
                    # Small deficits get minimum transfer
                    transfer_amount = min(remaining_to_send, MIN_TRANSFER, MAX_TRANSFER)
                else:
                    # For larger deficits, check if other lines can also send to this destination
                    other_senders_count = 0
                    for other_line, other_excess in excess_lines:
                        if other_line != from_line and other_excess >= MIN_TRANSFER:
                            other_zone = line_to_zone.get(other_line)
                            if other_zone and INTER_ZONE_OPERATIONS[other_zone].get(to_zone, '-') == 'x':
                                other_senders_count += 1
                    
                    if other_senders_count > 0:
                        # Leave room for others: send strategic amount (like 500) instead of full deficit
                        strategic_amount = min(500, deficit_needed)
                        transfer_amount = min(remaining_to_send, strategic_amount, MAX_TRANSFER)
                    else:
                        # No other senders, can send full deficit
                        transfer_amount = min(remaining_to_send, deficit_needed, MAX_TRANSFER)
                
                if transfer_amount >= MIN_TRANSFER:
                    # Record transfer
                    if from_line not in planned_transfers:
                        planned_transfers[from_line] = {}
                    planned_transfers[from_line][to_line] = transfer_amount
                    
                    # Update remaining amounts
                    remaining_to_send -= transfer_amount
                    deficit_lines_copy[i] = (to_line, deficit_needed - transfer_amount)
                    
                    print(f"    -> {to_line}: {transfer_amount:.1f} tonnes")
                    
                    if remaining_to_send < MIN_TRANSFER:
                        break
            else:
                print(f"    -> {to_line}: NOT ALLOWED (interzone matrix)")
        
        # Second priority: send to any line that won't exceed Z_MAX (if still have excess)
        if remaining_to_send >= MIN_TRANSFER:
            print(f"    Remaining excess: {remaining_to_send:.1f} tonnes - trying overflow protection")
            
            for to_line in P29_LINES:
                if to_line == from_line or remaining_to_send < MIN_TRANSFER:
                    continue
                    
                to_zone = line_to_zone.get(to_line)
                allowed = INTER_ZONE_OPERATIONS[from_zone].get(to_zone, '-')
                if allowed != 'x':
                    continue
                
                # Check if this line can receive without exceeding Z_MAX
                current_to_stock = final_stocks.get(to_line, 0)
                # Account for any transfers already planned to this line
                net_transfer_to_line = 0
                for sender, transfers in planned_transfers.items():
                    net_transfer_to_line += transfers.get(to_line, 0)
                    if sender == to_line:
                        net_transfer_to_line -= sum(transfers.values())
                
                projected_to_stock = current_to_stock + net_transfer_to_line
                available_capacity = Z_MAX_29 - projected_to_stock
                
                # Reserve some capacity for smaller excess lines that will be processed later
                reserved_capacity = 0
                for other_line, other_excess in excess_lines:
                    if other_line != from_line and other_excess < MIN_TRANSFER and other_excess > 0:
                        other_zone = line_to_zone.get(other_line)
                        if other_zone and INTER_ZONE_OPERATIONS[other_zone].get(to_zone, '-') == 'x':
                            reserved_capacity += min(other_excess, MIN_TRANSFER)
                
                effective_capacity = available_capacity - reserved_capacity
                
                if effective_capacity >= MIN_TRANSFER:
                    transfer_amount = min(
                        remaining_to_send,
                        effective_capacity,
                        MAX_TRANSFER
                    )
                    
                    if transfer_amount >= MIN_TRANSFER:
                        # Record transfer
                        if from_line not in planned_transfers:
                            planned_transfers[from_line] = {}
                        
                        existing = planned_transfers[from_line].get(to_line, 0)
                        planned_transfers[from_line][to_line] = existing + transfer_amount
                        
                        remaining_to_send -= transfer_amount
                        print(f"    -> {to_line}: {transfer_amount:.1f} tonnes (overflow protection)")
                        
                        if remaining_to_send < MIN_TRANSFER:
                            break
            
            if remaining_to_send >= MIN_TRANSFER:
                print(f"    Final remaining excess: {remaining_to_send:.1f} tonnes (unresolved)")
    
    # Step 3: Calculate final stocks after transfers
    print(f"\nTransfer Summary:")
    if planned_transfers:
        total_transferred = 0
        for from_line, transfers in planned_transfers.items():
            for to_line, amount in transfers.items():
                print(f"  {from_line} -> {to_line}: {amount:.1f} tonnes")
                total_transferred += amount
        print(f"  Total transferred: {total_transferred:.1f} tonnes")
        
        # Calculate final stocks after transfers
        final_stocks_after = final_stocks.copy()
        for from_line, transfers in planned_transfers.items():
            for to_line, amount in transfers.items():
                final_stocks_after[from_line] -= amount
                final_stocks_after[to_line] += amount
        
        print(f"\nFinal stocks after transfers:")
        violations_resolved = 0
        total_violations = len(excess_lines) + len(deficit_lines)
        
        for line in P29_LINES:
            stock = final_stocks_after.get(line, 0)
            original_stock = final_stocks[line]
            
            if stock > Z_MAX_29:
                excess = stock - Z_MAX_29
                print(f"  {line}: {stock:.1f} -> STILL OVERFILLED by {excess:.1f}")
            elif stock < Z_MIN_29:
                deficit = Z_MIN_29 - stock
                print(f"  {line}: {stock:.1f} -> STILL DEPLETED by {deficit:.1f}")
            else:
                print(f"  {line}: {stock:.1f} -> GREEN ZONE ✓")
                # Check if this was previously violated
                if original_stock > Z_MAX_29 or original_stock < Z_MIN_29:
                    violations_resolved += 1
        
        print(f"\nViolations resolved: {violations_resolved}/{total_violations}")
        
    else:
        print("  No transfers planned")
    
    return planned_transfers

if __name__ == "__main__":
    test_transfer_planning()