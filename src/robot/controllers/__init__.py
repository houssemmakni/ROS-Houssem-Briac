"""
Package controllers - Couche Contrôleur de l'architecture MVC.
Gère les interactions utilisateur et les stratégies de navigation.
"""

from robot.controllers.controleur import Controleur
from robot.controllers.controleur_terminal import ControleurTerminal
from robot.controllers.controleur_clavier_pygame import ControleurClavierPygame
from robot.controllers.controleur_pid import ControleurPID
from robot.controllers.strategy import Strategy
from robot.controllers.avoid_strategy import AvoidStrategy
from robot.controllers.free_direction_strategy import FreeDirectionStrategy
from robot.controllers.goal_strategy import GoalStrategy
from robot.controllers.navigator import Navigator
