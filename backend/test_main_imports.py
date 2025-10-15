#!/usr/bin/env python
"""Test main.py imports to identify router loading issues"""
import sys
import traceback

print("Testing main.py imports...")
print("=" * 60)

try:
    from app import main
    print("SUCCESS: main.py imported")
    
    # Count loaded routers
    router_vars = [
        'property_router', 'clients_router', 'transactions_router',
        'intelligence_router', 'chat_sessions_router', 'health_v1_router'
    ]
    
    loaded = 0
    for var_name in router_vars:
        if hasattr(main, var_name):
            router = getattr(main, var_name)
            if router is not None:
                print(f"  ✓ {var_name}: LOADED")
                loaded += 1
            else:
                print(f"  ✗ {var_name}: None")
        else:
            print(f"  ✗ {var_name}: NOT FOUND")
    
    print(f"\nLoaded routers: {loaded}/{len(router_vars)}")
    
except Exception as e:
    print(f"ERROR importing main.py:")
    print(traceback.format_exc())
    sys.exit(1)
