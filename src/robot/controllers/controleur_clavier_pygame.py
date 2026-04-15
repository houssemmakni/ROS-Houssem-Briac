"""
Classe ControleurClavierPygame - Contrôle clavier + souris via Pygame.
"""

import math
import pygame

from robot.controllers.controleur import Controleur


class ControleurClavierPygame(Controleur):
    """Contrôleur clavier + souris pour le jeu zombie survival."""

    def __init__(self, vitesse_deplacement=3.0):
        self.__vitesse = vitesse_deplacement
        self.__tir_demande = False
        self.__changement_arme = -1
        self.__quitter = False
        self.__restart = False
        self.__demarrer = False

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

    def lire_commande(self):
        """Lit les entrées clavier/souris et retourne une commande."""
        self.__tir_demande = False
        self.__changement_arme = -1
        self.__restart = False
        self.__demarrer = False

        # Événements
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
                elif event.key == pygame.K_1:
                    self.__changement_arme = 0
                elif event.key == pygame.K_2:
                    self.__changement_arme = 1
                elif event.key == pygame.K_3:
                    self.__changement_arme = 2
                elif event.key == pygame.K_4:
                    self.__changement_arme = 3

        # Tir continu avec clic gauche maintenu
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            self.__tir_demande = True

        # Mouvement ZQSD + flèches
        keys = pygame.key.get_pressed()
        vx = 0.0
        vy = 0.0

        if keys[pygame.K_z] or keys[pygame.K_UP]:
            vy += 1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            vy -= 1.0
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            vx -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            vx += 1.0

        # Normaliser la diagonale
        if vx != 0 and vy != 0:
            norm = math.sqrt(vx * vx + vy * vy)
            vx /= norm
            vy /= norm

        return {
            "vx": vx * self.__vitesse,
            "vy": vy * self.__vitesse,
            "omega": 0.0,
        }
