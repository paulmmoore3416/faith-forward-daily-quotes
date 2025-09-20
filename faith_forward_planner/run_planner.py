#!/usr/bin/env python3
"""
Faith Forward Planner - Launcher Script
Launches the GTK-based Faith Forward Planner application
"""

import sys
import os

# Add the planner module to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from planner.main import main

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nExiting Faith Forward Planner...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting Faith Forward Planner: {e}")
        sys.exit(1)