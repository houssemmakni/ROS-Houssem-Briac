"""
Classe Game - Boucle principale du jeu.
Orchestre le pattern MVC : Controleur -> Modèle -> Vue.
"""

import math
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
from robot.controllers import ControleurClavierPygame
from robot.views import VuePygame

logger = logging.getLogger(__name__)


class Game:
    """Classe principale du jeu - orchestre MVC."""

    def __init__(self, type_moteur="omni"):
        self.__type_moteur = type_moteur
        self.__running = False
        self.__etat = "titre"  # titre, jeu, game_over

    def _creer_environnement(self):
        """Crée l'environnement avec les obstacles de la map."""
        env = Environnement(largeur=20.0, hauteur=15.0)

        # --- Map : arène de survie zombie ---
        # Murs centraux (couverture)
        env.ajouter_obstacle(ObstacleRectangle(4.0, 6.0, 2.0, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(14.0, 6.0, 2.0, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(4.0, 9.0, 2.0, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(14.0, 9.0, 2.0, 0.3))

        # Bunkers (rectangles plus grands)
        env.ajouter_obstacle(ObstacleRectangle(8.5, 3.0, 3.0, 1.0))   # bunker bas
        env.ajouter_obstacle(ObstacleRectangle(8.5, 11.0, 3.0, 1.0))  # bunker haut

        # Piliers (circulaires)
        env.ajouter_obstacle(ObstacleCirculaire(3.0, 3.0, 0.5))
        env.ajouter_obstacle(ObstacleCirculaire(17.0, 3.0, 0.5))
        env.ajouter_obstacle(ObstacleCirculaire(3.0, 12.0, 0.5))
        env.ajouter_obstacle(ObstacleCirculaire(17.0, 12.0, 0.5))
        env.ajouter_obstacle(ObstacleCirculaire(10.0, 7.5, 0.6))  # pilier central

        # Murs de coin
        env.ajouter_obstacle(ObstacleRectangle(1.0, 1.0, 1.5, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(1.0, 1.0, 0.3, 1.5))
        env.ajouter_obstacle(ObstacleRectangle(17.5, 1.0, 1.5, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(18.7, 1.0, 0.3, 1.5))
        env.ajouter_obstacle(ObstacleRectangle(1.0, 13.7, 1.5, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(1.0, 13.2, 0.3, 1.5))
        env.ajouter_obstacle(ObstacleRectangle(17.5, 13.7, 1.5, 0.3))
        env.ajouter_obstacle(ObstacleRectangle(18.7, 13.2, 0.3, 1.5))

        return env

    def _creer_robot(self):
        """Crée le robot joueur avec son moteur."""
        if self.__type_moteur == "differentiel":
            moteur = MoteurDifferentiel()
        else:
            moteur = MoteurOmnidirectionnel()

        robot = RobotMobile(x=10.0, y=5.5, orientation=0.0, rayon=0.3, moteur=moteur)

        # Ajouter le Lidar
        lidar = Lidar(robot, nb_rayons=36, max_range=8.0)
        robot.ajouter_capteur(lidar)

        return robot

    def _creer_cartographie(self, env):
        """Crée la grille d'occupation et le cartographe.
        Pré-remplit la grille avec les obstacles statiques de la map."""
        grille = GrilleOccupation(
            largeur_m=env.largeur,
            hauteur_m=env.hauteur,
            resolution=0.4,
            origin_x=0,  # la grille couvre [0, largeur] x [0, hauteur]
            origin_y=0,
        )

        # Pré-remplir les obstacles statiques dans la grille pour A*
        for ix in range(grille.nx):
            for iy in range(grille.ny):
                x, y = grille.index2coord(ix, iy)
                # Vérifier si cette cellule touche un obstacle ou un mur
                if env.collision_obstacles(x, y, 0.15):
                    grille.set_cellule(ix, iy, GrilleOccupation.OCCUPE)
                else:
                    grille.set_cellule(ix, iy, GrilleOccupation.LIBRE)

        cartographe = Cartographe(grille)
        planificateur = PlanificateurAStar(grille)

        return grille, cartographe, planificateur

    def _creer_armes(self):
        """Crée l'inventaire d'armes du joueur."""
        return [Fusil(), FusilAPompe(), Laser(), LanceFlamme()]

    def _reset(self):
        """Réinitialise le jeu."""
        self.__env = self._creer_environnement()
        self.__robot = self._creer_robot()
        self.__env.ajouter_robot(self.__robot)
        self.__armes = self._creer_armes()
        self.__index_arme = 0
        self.__wave_manager = WaveManager(intervalle_vague=15.0)
        self.__wave_manager.demarrer()

        # Cartographie + A* pour les zombies
        self.__grille, self.__cartographe, self.__planificateur = \
            self._creer_cartographie(self.__env)
        self.__lidar = self.__robot.capteurs[0]  # Le Lidar du robot

        self.__etat = "jeu"
        logger.info("Jeu réinitialisé")

    def run(self):
        """Boucle principale du jeu (MVC)."""
        # Initialisation des composants MVC
        vue = VuePygame(largeur=1000, hauteur=750, scale=50)
        controleur = ControleurClavierPygame(vitesse_deplacement=3.5)

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

        logger.info("Démarrage du jeu Robot Zombie Survival")

        while self.__running:
            dt = 1.0 / 60.0  # Pas de temps fixe

            # ===== CONTROLEUR : lire les entrées =====
            commande = controleur.lire_commande()

            if controleur.quitter:
                self.__running = False
                break

            # --- État : écran titre ---
            if self.__etat == "titre":
                if controleur.demarrer:
                    self._reset()
                else:
                    vue.dessiner_ecran_titre()
                    vue.tick(60)
                    continue

            # --- État : game over ---
            elif self.__etat == "game_over":
                if controleur.restart:
                    self._reset()
                else:
                    vue.dessiner_game_over(self.__wave_manager)
                    vue.tick(60)
                    continue

            # --- État : jeu en cours ---
            # Changement d'arme
            if controleur.changement_arme >= 0 and controleur.changement_arme < len(self.__armes):
                self.__index_arme = controleur.changement_arme

            arme_courante = self.__armes[self.__index_arme]

            # Appliquer la commande de mouvement
            if self.__type_moteur == "differentiel":
                vx = commande["vx"]
                vy = commande["vy"]
                if abs(vx) > 0.01 or abs(vy) > 0.01:
                    angle_cible = math.atan2(vy, vx)
                    diff_angle = angle_cible - self.__robot.orientation
                    while diff_angle > math.pi:
                        diff_angle -= 2 * math.pi
                    while diff_angle < -math.pi:
                        diff_angle += 2 * math.pi
                    v = math.sqrt(vx * vx + vy * vy)
                    omega = diff_angle * 5.0
                    self.__robot.commander(v=v, omega=omega)
                else:
                    self.__robot.commander(v=0.0, omega=0.0)
            else:
                vx_world = commande["vx"]
                vy_world = commande["vy"]
                theta = self.__robot.orientation
                vx_robot = vx_world * math.cos(theta) + vy_world * math.sin(theta)
                vy_robot = -vx_world * math.sin(theta) + vy_world * math.cos(theta)
                self.__robot.commander(vx=vx_robot, vy=vy_robot, omega=0.0)

            # Tir
            if controleur.tir_demande and arme_courante.peut_tirer():
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mx, my = vue.convertir_ecran_vers_monde(mouse_x, mouse_y)
                angle_tir = math.atan2(my - self.__robot.y, mx - self.__robot.x)

                tir_x = self.__robot.x + math.cos(angle_tir) * (self.__robot.rayon + 0.1)
                tir_y = self.__robot.y + math.sin(angle_tir) * (self.__robot.rayon + 0.1)

                projectiles = arme_courante.tirer(tir_x, tir_y, angle_tir)
                for p in projectiles:
                    self.__env.ajouter_projectile(p)

            # ===== MODELE : mise à jour =====
            # Mise à jour du Lidar + Cartographe
            self.__lidar.lire(self.__env)
            self.__cartographe.mise_a_jour(self.__env, self.__lidar)

            # Mise à jour de l'environnement (zombies avec A*)
            self.__env.mettre_a_jour(dt,
                                     grille=self.__grille,
                                     planificateur=self.__planificateur)
            self.__wave_manager.mettre_a_jour(self.__env, dt)

            # Régénération des munitions
            for arme in self.__armes:
                arme.regenerer(dt)

            # Vérifier game over
            if not self.__robot.est_vivant:
                self.__etat = "game_over"
                logger.info(f"Game Over! Score: {self.__wave_manager.score}, "
                            f"Vague: {self.__wave_manager.vague_actuelle}")

            # ===== VUE : affichage =====
            vue.dessiner(self.__env, self.__wave_manager, arme_courante,
                         self.__armes, self.__index_arme,
                         grille=self.__grille)
            vue.tick(60)

        vue.fermer()
        logger.info("Jeu terminé")
