"""
Point d'entrée principal du projet Robot Zombie Survival.
Lance la simulation avec l'architecture MVC.

Usage:
    python main.py
    python main.py --debug
    python main.py --moteur differentiel
"""

import sys
import os

# Ajouter src/ au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from robot.__main__ import main

if __name__ == "__main__":
    main()
