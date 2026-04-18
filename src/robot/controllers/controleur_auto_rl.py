"""
Classe ControleurAutoRL - Le robot joue tout seul via Q-learning.
Utilise le Lidar pour percevoir les obstacles et les integre dans le RL.
"""

import math
import pygame

from robot.controllers.controleur import Controleur


class ControleurAutoRL(Controleur):
    """Controleur automatique : le robot est pilote par un agent RL.
    Integre les donnees Lidar dans la prise de decision."""

    def __init__(self, rl_robot_agent, vitesse=3.5):
        self.__agent = rl_robot_agent
        self.__vitesse = vitesse
        self.__dernier_etat = None
        self.__derniere_action = None
        self.__ancien_pv = None
        self.__ancien_nb_zombies = None
        self.__derniere_collision_mur = False

        self.__tir_demande = True
        self.__changement_arme = -1
        self.__arme_actuelle = 0
        self.__arme_cooldown = 0.0  # cooldown entre changements d'arme
        self.__quitter = False
        self.__restart = False
        self.__demarrer = False
        self.__angle_visee = 0.0

    @property
    def agent(self):
        return self.__agent

    @property
    def tir_demande(self):
        return self.__tir_demande

    @property
    def changement_arme(self):
        return self.__changement_arme

    @property
    def quitter(self):
        return self.__quitter

    @property
    def restart(self):
        return self.__restart

    @property
    def demarrer(self):
        return self.__demarrer

    @property
    def angle_visee(self):
        return self.__angle_visee

    def lire_commande(self):
        self.__restart = False
        self.__demarrer = False
        self.__changement_arme = -1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__quitter = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.__quitter = True
                elif event.key == pygame.K_r:
                    self.__restart = True
                elif event.key == pygame.K_SPACE:
                    self.__demarrer = True

        return {"vx": 0.0, "vy": 0.0, "omega": 0.0}

    def calculer_action(self, robot, zombies, lidar_distances=None):
        """Calcule mouvement + arme via RL en utilisant le Lidar.
        Retourne (vx, vy, angle_visee, index_arme)."""
        rx, ry = robot.x, robot.y
        ratio_pv = robot.pv / robot.pv_max
        nb_zombies = len(zombies)

        # Trouver le zombie le plus proche
        plus_proche = None
        dist_min = float("inf")
        nb_proches = 0

        for z in zombies:
            dx = z.x - rx
            dy = z.y - ry
            d = math.sqrt(dx * dx + dy * dy)
            if d < dist_min:
                dist_min = d
                plus_proche = z
            if d < 3.0:
                nb_proches += 1

        # Visee auto sur le plus proche
        if plus_proche:
            angle_zombie = math.atan2(plus_proche.y - ry, plus_proche.x - rx)
            if angle_zombie < 0:
                angle_zombie += 2 * math.pi
            self.__angle_visee = math.atan2(plus_proche.y - ry, plus_proche.x - rx)
        else:
            angle_zombie = None
            dist_min = None
            self.__angle_visee = 0.0

        # === ANALYSER LE LIDAR ===
        obstacle_devant = False
        espace_confine = False
        from robot.models.rl.rl_robot_agent import RLRobotAgent
        if lidar_distances:
            obstacle_devant, espace_confine, _ = RLRobotAgent.analyser_lidar(
                lidar_distances, robot.orientation, angle_mouvement=None
            )

        # Discretiser l'etat (avec les donnees Lidar)
        etat = self.__agent.discretiser_etat(
            angle_zombie, dist_min, nb_proches, ratio_pv,
            obstacle_devant=obstacle_devant,
            espace_confine=espace_confine,
        )

        # Apprentissage sur la transition precedente
        if self.__dernier_etat is not None:
            est_mort = not robot.est_vivant
            recompense = self.__agent.calculer_recompense(
                self.__ancien_pv, robot.pv,
                self.__ancien_nb_zombies, nb_zombies,
                est_mort,
                collision_mur=self.__derniere_collision_mur,
            )
            self.__agent.mettre_a_jour(
                self.__dernier_etat, self.__derniere_action, recompense, etat
            )
            kills = self.__ancien_nb_zombies - nb_zombies
            for _ in range(max(0, kills)):
                self.__agent.ajouter_kill()

        self.__dernier_etat = etat
        self.__ancien_pv = robot.pv
        self.__ancien_nb_zombies = nb_zombies

        # Choisir une action composite (mouvement + arme)
        action = self.__agent.choisir_action(etat)
        self.__derniere_action = action

        # Decoder : mouvement
        direction = self.__agent.get_direction(action)
        if direction is not None:
            vx = math.cos(direction) * self.__vitesse
            vy = math.sin(direction) * self.__vitesse
        else:
            vx, vy = 0.0, 0.0

        # Decoder : arme (appris par RL, avec cooldown de 1s)
        arme_voulue = self.__agent.get_arme(action)
        self.__arme_cooldown -= 1.0 / 60.0
        if arme_voulue != self.__arme_actuelle and self.__arme_cooldown <= 0:
            self.__arme_actuelle = arme_voulue
            self.__changement_arme = arme_voulue
            self.__arme_cooldown = 1.0  # 1 seconde avant le prochain changement
        else:
            self.__changement_arme = -1  # pas de changement cette frame

        # Tir auto
        self.__tir_demande = plus_proche is not None

        return vx, vy, self.__angle_visee, self.__changement_arme

    def signaler_collision_mur(self, collision):
        """Appele par game.py quand le robot est bloque par un mur.
        L'agent recoit une penalite pour apprendre a eviter les murs via le Lidar."""
        self.__derniere_collision_mur = collision

    def reset(self):
        self.__dernier_etat = None
        self.__derniere_action = None
        self.__ancien_pv = None
        self.__ancien_nb_zombies = None
        self.__derniere_collision_mur = False
