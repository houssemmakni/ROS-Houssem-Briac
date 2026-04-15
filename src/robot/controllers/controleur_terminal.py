"""
Classe ControleurTerminal - Contrôle du robot via le terminal.
"""

from robot.controllers.controleur import Controleur


class ControleurTerminal(Controleur):
    """Contrôleur terminal (entrée texte)."""

    def lire_commande(self):
        print("Commande differentiel : v omega (ex: 1.0 0.5)")
        try:
            entree = input("> ").strip().split()
            v = float(entree[0])
            omega = float(entree[1])
        except (IndexError, ValueError):
            v, omega = 0.0, 0.0
        return {"v": v, "omega": omega}
