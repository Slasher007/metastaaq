#!/usr/bin/env python3
"""
Script de test pour vérifier les imports nécessaires
"""

def test_imports():
    """Test des imports nécessaires"""
    print("🔍 Test des imports...")
    
    try:
        import pandas as pd
        print("✅ pandas: OK")
    except ImportError as e:
        print(f"❌ pandas: {e}")
    
    try:
        import matplotlib.pyplot as plt
        print("✅ matplotlib: OK")
    except ImportError as e:
        print(f"❌ matplotlib: {e}")
    
    try:
        import seaborn as sns
        print("✅ seaborn: OK")
    except ImportError as e:
        print(f"❌ seaborn: {e}")
    
    try:
        import openpyxl
        print("✅ openpyxl: OK")
    except ImportError as e:
        print(f"❌ openpyxl: {e}")
    
    try:
        import numpy as np
        print("✅ numpy: OK")
    except ImportError as e:
        print(f"❌ numpy: {e}")

if __name__ == "__main__":
    test_imports() 