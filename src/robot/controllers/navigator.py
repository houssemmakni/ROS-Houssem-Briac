"""
Classe Navigator - Context du Design Pattern Strategy.
Utilise une stratégie de navigation sans connaître son implémentation.
Permet de changer de stratégie dynamiquement.
"""

from robot.controllers.strategy import Strategy


class Navigator:
    """Context du pattern Strategy : délègue la décision de navigation à une stratégie."""

    def __init__(self, strategy: Strategy):
        self.__strategy = strategy

    @property
    def strategy(self):
        return self.__strategy

    def set_strategy(self, strategy: Strategy):
        """Change la stratégie de navigation dynamiquement."""
        self.__strategy = strategy

    def step(self, observation):
        """Demande une commande à la stratégie courante.

        Paramètres:
            observation: dict avec les données capteurs du robot

        Retourne:
            dict avec 'v' et 'omega'
        """
        return self.__strategy.compute_command(observation)
