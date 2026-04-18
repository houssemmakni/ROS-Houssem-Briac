"""
Classe Game - Boucle principale du jeu.
Orchestre le pattern MVC : Controleur -> Modele -> Vue.
Supporte le mode auto-play (robot pilote par Q-learning).
"""

import math
import os
import logging

import pygame

from robot.models import (
    RobotMobile,
    MoteurOmnidirectionnel,
    MoteurDifferentiel,
    Environnement,
    ObstacleRectangle,
    ObstacleCirculaire,
    Lidar,
    Fusil,
    FusilAPompe,
    Laser,
    LanceFlamme,
    WaveManager,
    GrilleOccupation,
    Cartographe,
    PlanificateurAStar,
)
from robot.models.difficulte import Difficulte
from robot.models.rl.rl_agent import RLAgent
from robot.models.rl.rl_robot_agent import RLRobotAgent
from robot.models.rl.pre_entrainement import PreEntrainement
from robot.controllers import ControleurClavierPygame
from robot.controllers.controleur_auto_rl import ControleurAutoRL
from robot.views import VuePygame

logger = logging.getLogger(__name__)

# Chemins des sauvegardes Q-table
SAVE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "saves")
SAVE_ROBOT = os.path.join(SAVE_DIR, "rl_robot.npz")
SAVE_ZOMBIE = os.path.join(SAVE_DIR, "rl_zombie.npz")


class Game:
    """Classe principale du jeu - orchestre MVC."""

    def __init__(self, type_moteur="omni"):
        self.__type_moteur = type_moteur
        self.__running = False
        self.__etat = "titre"
        self.__difficulte = None
        self.__rl_agent = None          # RL pour les zombies (mode Impossible)
        self.__rl_robot_agent = None    # RL pour le robot (mode auto-play)
        self.__auto_play = False

    # ===================== RL : CHARGEMENT / SAUVEGARDE / PRE-ENTRAINEMENT ====

    def _charger_ou_entrainer_agents(self):
        """Charge les Q-tables depuis le disque, ou pre-entraine si pas de sauvegarde."""
        os.makedirs(SAVE_DIR, exist_ok=True)

        # --- Agent robot ---
        self.__rl_robot_agent = RLRobotAgent()
        if os.path.exists(SAVE_ROBOT):
            self.__rl_robot_agent.charger(SAVE_ROBOT)
            logger.info(f"Robot RL charge : {self.__rl_robot_agent}")
        else:
            logger.info("Pas de sauvegarde robot RL, pre-entrainement...")
            entraineur = PreEntrainement()
            entraineur.entrainer_robot(self.__rl_robot_agent, nb_episodes=3000)
            self.__rl_robot_agent.sauvegarder(SAVE_ROBOT)
            logger.info(f"Robot RL pre-entraine et sauvegarde : {self.__rl_robot_agent}")

        # --- Agent zombies ---
        self.__rl_agent = RLAgent()
        if os.path.exists(SAVE_ZOMBIE):
            self.__rl_agent.charger(SAVE_ZOMBIE)
            logger.info(f"Zombie RL charge : {self.__rl_agent}")
        else:
            logger.info("Pas de sauvegarde zombie RL, pre-entrainement...")
            entraineur = PreEntrainement()
            entraineur.entrainer_zombies(self.__rl_agent, nb_episodes=3000)
            self.__rl_agent.sauvegarder(SAVE_ZOMBIE)
            logger.info(f"Zombie RL pre-entraine et sauvegarde : {self.__rl_agent}")

    def _sauvegarder_agents(self):
        """Sauvegarde les Q-tables sur disque."""
        os.makedirs(SAVE_DIR, exist_ok=True)
        if self.__rl_robot_agent:
            self.__rl_robot_agent.sauvegarder(SAVE_ROBOT)
        if self.__rl_agent:
            self.__rl_agent.sauvegarder(SAVE_ZOMBIE)
        logger.info("Agents RL sauvegardes")

    # ===================== CREATION DES ENTITES =====================

    def _creer_environnement(self):
        env = Environnement(largeur=20.0, hauteur=15.0)
        env.ajouter_obstacle(ObstacleRectangle(4.0, 6.0, 2.0, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(14.0, 6.0, 2.0, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(4.0, 9.0, 2.0, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(14.0, 9.0, 2.0, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(8.5, 3.0, 3.0, 1.0))
        env.ajouter_obstacle(ObstacleRectangle(8.5, 11.0, 3.0, 1.0))
        env.ajouter_obstacle(ObstacleCirculaire(3.0, 3.0, 0.5))
        env.ajouter_obstacle(ObstacleCirculaire(17.0, 3.0, 0.5))
        env.ajouter_obstacle(ObstacleCirculaire(3.0, 12.0, 0.5))
        env.ajouter_obstacle(ObstacleCirculaire(17.0, 12.0, 0.5))
        env.ajouter_obstacle(ObstacleCirculaire(10.0, 7.5, 0.6))
        env.ajouter_obstacle(ObstacleRectangle(1.0, 1.0, 1.5, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(1.0, 1.0, 0.3, 1.5))
        env.ajouter_obstacle(ObstacleRectangle(17.5, 1.0, 1.5, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(18.7, 1.0, 0.3, 1.5))
        env.ajouter_obstacle(ObstacleRectangle(1.0, 13.7, 1.5, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(1.0, 13.2, 0.3, 1.5))
        env.ajouter_obstacle(ObstacleRectangle(17.5, 13.7, 1.5, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(18.7, 13.2, 0.3, 1.5))
        return env

    def _creer_robot(self, pv_max):
        moteur = MoteurDifferentiel() if self.__type_moteur == "differentiel" else MoteurOmnidirectionnel()
        robot = RobotMobile(x=10.0, y=5.5, orientation=0.0, rayon=0.3,
                            moteur=moteur, pv_max=pv_max)
        lidar = Lidar(robot, nb_rayons=36, max_range=8.0)
        robot.ajouter_capteur(lidar)
        return robot

    def _creer_cartographie(self, env):
        grille = GrilleOccupation(largeur_m=env.largeur, hauteur_m=env.hauteur,
                                  resolution=0.4, origin_x=0, origin_y=0)
        for ix in range(grille.nx):
            for iy in range(grille.ny):
                x, y = grille.index2coord(ix, iy)
                if env.collision_obstacles(x, y, 0.35):
                    grille.set_cellule(ix, iy, GrilleOccupation.OCCUPE)
                else:
                    grille.set_cellule(ix, iy, GrilleOccupation.LIBRE)
        return grille, Cartographe(grille), PlanificateurAStar(grille)

    def _creer_armes(self):
        return [Fusil(), FusilAPompe(), Laser(), LanceFlamme()]

    # ===================== RESET =====================

    def _reset(self, niveau):
        self.__difficulte = niveau
        config = Difficulte.get_config(niveau)

        self.__env = self._creer_environnement()
        self.__robot = self._creer_robot(pv_max=config["robot_pv"])
        self.__env.ajouter_robot(self.__robot)
        self.__armes = self._creer_armes()
        self.__index_arme = 0

        self.__wave_manager = WaveManager(config=config)
        if config["use_rl"]:
            if self.__rl_agent is None:
                self.__rl_agent = RLAgent()
            self.__wave_manager.set_rl_agent(self.__rl_agent)
        self.__wave_manager.demarrer()

        self.__grille, self.__cartographe, self.__planificateur = \
            self._creer_cartographie(self.__env)
        self.__lidar = self.__robot.capteurs[0]

        # Reset du controleur auto-play si actif
        if self.__auto_play and self.__controleur_auto:
            self.__controleur_auto.reset()

        self.__etat = "jeu"
        logger.info(f"Jeu demarre en mode {config['nom']}"
                     f"{' [AUTO-PLAY RL]' if self.__auto_play else ''}")

    # ===================== BOUCLE PRINCIPALE =====================

    def run(self):
        vue = VuePygame(largeur=1000, hauteur=750, scale=50)
        controleur = ControleurClavierPygame(vitesse_deplacement=3.5)

        # Charger ou pre-entrainer les agents RL
        self._charger_ou_entrainer_agents()
        self.__controleur_auto = ControleurAutoRL(self.__rl_robot_agent)

        self.__env = None
        self.__robot = None
        self.__armes = []
        self.__index_arme = 0
        self.__wave_manager = None
        self.__grille = None
        self.__cartographe = None
        self.__planificateur = None
        self.__lidar = None
        self.__running = True
        self.__difficulte_selectionnee = 0

        logger.info("Demarrage du jeu Robot Zombie Survival")

        while self.__running:
            dt = 1.0 / 60.0

            # Lire les deux controleurs (clavier toujours pour les menus)
            commande = controleur.lire_commande()
            commande_auto = self.__controleur_auto.lire_commande()

            # Quitter
            if controleur.quitter or self.__controleur_auto.quitter:
                self.__running = False
                break

            # =================== ECRAN TITRE ===================
            if self.__etat == "titre":
                if controleur.demarrer:
                    self.__etat = "difficulte"
                vue.dessiner_ecran_titre()
                vue.tick(60)
                continue

            # =================== SELECTION DIFFICULTE ===================
            elif self.__etat == "difficulte":
                niveaux = [Difficulte.FACILE, Difficulte.DIFFICILE, Difficulte.IMPOSSIBLE]

                if controleur.changement_arme == 0:
                    self.__difficulte_selectionnee = 0
                elif controleur.changement_arme == 1:
                    self.__difficulte_selectionnee = 1
                elif controleur.changement_arme == 2:
                    self.__difficulte_selectionnee = 2

                # Toggle auto-play avec [TAB]
                keys = pygame.key.get_pressed()
                if keys[pygame.K_TAB]:
                    if not getattr(self, '_tab_pressed', False):
                        self.__auto_play = not self.__auto_play
                        self._tab_pressed = True
                        logger.info(f"Auto-play: {'ON' if self.__auto_play else 'OFF'}")
                else:
                    self._tab_pressed = False

                if controleur.demarrer:
                    self._reset(niveaux[self.__difficulte_selectionnee])
                else:
                    vue.dessiner_ecran_difficulte(
                        self.__difficulte_selectionnee,
                        self.__rl_agent,
                        auto_play=self.__auto_play,
                        rl_robot_agent=self.__rl_robot_agent,
                    )
                vue.tick(60)
                continue

            # =================== GAME OVER ===================
            elif self.__etat == "game_over":
                if controleur.restart or self.__controleur_auto.restart:
                    self.__etat = "difficulte"
                vue.dessiner_game_over(self.__wave_manager, self.__difficulte,
                                       self.__rl_agent,
                                       auto_play=self.__auto_play,
                                       rl_robot_agent=self.__rl_robot_agent)
                vue.tick(60)

                # Auto-restart en mode auto-play apres 3 secondes
                if self.__auto_play:
                    if not hasattr(self, '_auto_restart_timer'):
                        self._auto_restart_timer = 0
                    self._auto_restart_timer += dt
                    if self._auto_restart_timer > 3.0:
                        self._auto_restart_timer = 0
                        self.__etat = "difficulte"
                continue

            # =================== JEU EN COURS ===================
            # Retour au menu avec [Y]
            if controleur.retour_menu:
                self._sauvegarder_agents()
                self.__etat = "difficulte"
                continue

            vx, vy = 0.0, 0.0
            etat_avant = self.__robot.sauvegarder_etat()

            if self.__auto_play:
                # === MODE AUTO-PLAY : le RL pilote le robot (avec Lidar) ===
                # Le Lidar est lu AVANT pour que le RL puisse l'utiliser
                self.__lidar.lire(self.__env)
                lidar_dists = self.__lidar.distances

                vx, vy, angle_visee, arme_idx = self.__controleur_auto.calculer_action(
                    self.__robot, self.__env.zombies,
                    lidar_distances=lidar_dists,
                )

                # Changement d'arme auto (appris par RL)
                if arme_idx >= 0 and arme_idx < len(self.__armes):
                    self.__index_arme = arme_idx

                arme_courante = self.__armes[self.__index_arme]

                # Utiliser le Lidar pour corriger la direction si obstacle
                from robot.models.rl.rl_robot_agent import RLRobotAgent
                angle_mouvement = math.atan2(vy, vx) if (abs(vx) > 0.01 or abs(vy) > 0.01) else None
                obs_devant, _, dir_libre = RLRobotAgent.analyser_lidar(
                    lidar_dists, self.__robot.orientation, angle_mouvement
                )
                if obs_devant and angle_mouvement is not None:
                    # Rediriger vers la direction libre detectee par le Lidar
                    vx = math.cos(dir_libre) * self.__controleur_auto._ControleurAutoRL__vitesse
                    vy = math.sin(dir_libre) * self.__controleur_auto._ControleurAutoRL__vitesse

                # Appliquer le mouvement
                theta = self.__robot.orientation
                vx_robot = vx * math.cos(theta) + vy * math.sin(theta)
                vy_robot = -vx * math.sin(theta) + vy * math.cos(theta)
                self.__robot.commander(vx=vx_robot, vy=vy_robot, omega=0.0)

                # Tir auto
                if self.__controleur_auto.tir_demande and arme_courante.peut_tirer():
                    tir_x = self.__robot.x + math.cos(angle_visee) * (self.__robot.rayon + 0.1)
                    tir_y = self.__robot.y + math.sin(angle_visee) * (self.__robot.rayon + 0.1)
                    for p in arme_courante.tirer(tir_x, tir_y, angle_visee):
                        self.__env.ajouter_projectile(p)

            else:
                # === MODE MANUEL : le joueur pilote ===
                if controleur.changement_arme >= 0 and controleur.changement_arme < len(self.__armes):
                    self.__index_arme = controleur.changement_arme

                arme_courante = self.__armes[self.__index_arme]

                # Mouvement
                if self.__type_moteur == "differentiel":
                    vx, vy = commande["vx"], commande["vy"]
                    if abs(vx) > 0.01 or abs(vy) > 0.01:
                        angle_cible = math.atan2(vy, vx)
                        diff_angle = angle_cible - self.__robot.orientation
                        while diff_angle > math.pi:
                            diff_angle -= 2 * math.pi
                        while diff_angle < -math.pi:
                            diff_angle += 2 * math.pi
                        v = math.sqrt(vx * vx + vy * vy)
                        self.__robot.commander(v=v, omega=diff_angle * 5.0)
                    else:
                        self.__robot.commander(v=0.0, omega=0.0)
                else:
                    vx_world, vy_world = commande["vx"], commande["vy"]
                    theta = self.__robot.orientation
                    vx_robot = vx_world * math.cos(theta) + vy_world * math.sin(theta)
                    vy_robot = -vx_world * math.sin(theta) + vy_world * math.cos(theta)
                    self.__robot.commander(vx=vx_robot, vy=vy_robot, omega=0.0)

                # Tir manuel
                if controleur.tir_demande and arme_courante.peut_tirer():
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    mx, my = vue.convertir_ecran_vers_monde(mouse_x, mouse_y)
                    angle_tir = math.atan2(my - self.__robot.y, mx - self.__robot.x)
                    tir_x = self.__robot.x + math.cos(angle_tir) * (self.__robot.rayon + 0.1)
                    tir_y = self.__robot.y + math.sin(angle_tir) * (self.__robot.rayon + 0.1)
                    for p in arme_courante.tirer(tir_x, tir_y, angle_tir):
                        self.__env.ajouter_projectile(p)

            # =================== MODELE ===================
            # Lidar scan + cartographie
            self.__lidar.lire(self.__env)
            self.__cartographe.mise_a_jour(self.__env, self.__lidar)

            # Signaler au RL si le robot est bloque par un mur
            if self.__auto_play:
                etat_apres = self.__robot.sauvegarder_etat()
                bloque = (abs(etat_avant[0] - etat_apres[0]) < 0.001 and
                          abs(etat_avant[1] - etat_apres[1]) < 0.001 and
                          (abs(vx) > 0.1 or abs(vy) > 0.1))
                self.__controleur_auto.signaler_collision_mur(bloque)
            self.__env.mettre_a_jour(dt, grille=self.__grille,
                                     planificateur=self.__planificateur)
            self.__wave_manager.mettre_a_jour(self.__env, dt)
            for arme in self.__armes:
                arme.regenerer(dt)

            if not self.__robot.est_vivant:
                self.__etat = "game_over"
                self._auto_restart_timer = 0
                self._sauvegarder_agents()
                logger.info(f"Game Over! Score: {self.__wave_manager.score}, "
                            f"Vague: {self.__wave_manager.vague_actuelle}")

            # =================== VUE ===================
            vue.dessiner(self.__env, self.__wave_manager, arme_courante,
                         self.__armes, self.__index_arme,
                         grille=self.__grille,
                         difficulte=self.__difficulte,
                         rl_agent=self.__rl_agent,
                         auto_play=self.__auto_play,
                         rl_robot_agent=self.__rl_robot_agent)
            vue.tick(60)

        # Sauvegarde finale a la fermeture
        self._sauvegarder_agents()
        vue.fermer()
        logger.info("Jeu termine")
