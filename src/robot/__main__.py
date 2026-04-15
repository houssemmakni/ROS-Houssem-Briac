"""
Point d'entrée du programme.
Lance la simulation Robot Zombie Survival.

Usage:
    python -m robot
    python -m robot --debug
    python -m robot --moteur differentiel
"""

import argparse
import sys

from robot.logging_config import configurer_logs


def parse_args():
    parser = argparse.ArgumentParser(description="Robot Zombie Survival - Simulation robotique MVC")
    parser.add_argument("--moteur", type=str, default="omni",
                        choices=["differentiel", "omni"],
                        help="Type de moteur (differentiel ou omni)")
    parser.add_argument("--debug", action="store_true",
                        help="Active les logs de niveau DEBUG")
    parser.add_argument("--dt", type=float, default=None,
                        help="Pas de temps de la simulation (auto si non spécifié)")
    return parser.parse_args()


def main():
    args = parse_args()
    configurer_logs(debug=args.debug)

    from robot.game import Game
    game = Game(type_moteur=args.moteur)
    game.run()


if __name__ == "__main__":
    main()
