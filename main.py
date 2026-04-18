"""
Point d'entree principal du projet Robot Zombie Survival.
Lance la simulation avec l'architecture MVC.

Usage:
    uv run python main.py
    uv run python main.py --debug
    uv run python main.py --moteur differentiel
"""

from robot.__main__ import main

if __name__ == "__main__":
    main()
