#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script to verify nearest maintenance calculation"""

import json
import os

def test_maintenance_logic():
    """Test the maintenance nearest calculation logic"""
    
    # Load maintenance data
    maintenance_file = os.path.join(os.path.dirname(__file__), 'data', 'belgrad', 'maintenance.json')
    with open(maintenance_file, 'r', encoding='utf-8') as f:
        maintenance_data = json.load(f)
    
    # Load km data
    km_file = os.path.join(os.path.dirname(__file__), 'data', 'belgrad', 'km_data.json')
    with open(km_file, 'r', encoding='utf-8') as f:
        km_data = json.load(f)
    
    # Maintenance levels
    maintenance_levels = sorted([k for k in maintenance_data.keys()], 
                               key=lambda x: int(x.replace('K', '')) * 1000)
    
    print("Maintenance Levels:", maintenance_levels)
    print("\n" + "="*80)
    
    # Test each tram
    for tram_id, km_info in km_data.items():
        if not tram_id or tram_id == '':
            continue
            
        current_km = km_info.get('current_km', 0)
        
        print(f"\nTramvay {tram_id}: {current_km} KM")
        print("-" * 80)
        
        all_maintenances = {}
        nearest_maintenance = None
        min_km_left = float('inf')
        
        for level in maintenance_levels:
            level_km = int(level.replace('K', '')) * 1000
            
            # Calculate multiples
            max_km = 300000  # 300K
            multiples = []
            
            for i in range(1, (max_km // level_km) + 2):
                km_value = level_km * i
                multiples.append(km_value)
            
            # Find next due
            next_due = None
            for km_value in multiples:
                if km_value > current_km:
                    next_due = km_value
                    break
            
            # Determine status
            if next_due is None:
                status = 'overdue'
                km_left = current_km - multiples[-1]
            else:
                km_left = next_due - current_km
                if km_left <= 0:
                    status = 'overdue'
                elif km_left <= 500:
                    status = 'urgent'
                elif km_left <= 2000:
                    status = 'warning'
                else:
                    status = 'normal'
            
            maint_info = {
                'level': level,
                'next_km': next_due or multiples[-1],
                'km_left': km_left if km_left > 0 else 0,
                'status': status,
                'works_count': len(maintenance_data.get(level, {}).get('works', []))
            }
            
            all_maintenances[level] = maint_info
            
            # Find nearest
            if km_left > 0 and km_left < min_km_left:
                min_km_left = km_left
                nearest_maintenance = maint_info
            
            # Print status
            status_symbol = {
                'normal': '✓',
                'warning': '⚠',
                'urgent': '🔴',
                'overdue': '✘'
            }.get(status, '?')
            
            print(f"  {level:5s}: Next {maint_info['next_km']:7d} KM | "
                  f"Left {maint_info['km_left']:6d} KM | "
                  f"{status_symbol} {status.upper():10s} | "
                  f"Works: {maint_info['works_count']}")
        
        # If no positive km_left found, use last maintenance
        if nearest_maintenance is None:
            nearest_maintenance = all_maintenances[maintenance_levels[-1]]
        
        print(f"\n  ► NEAREST: {nearest_maintenance['level']} | "
              f"Status: {nearest_maintenance['status'].upper()} | "
              f"KM Left: {nearest_maintenance['km_left']}")
        print()

if __name__ == '__main__':
    test_maintenance_logic()
    print("\n" + "="*80)
    print("Test completed successfully!")
