"""
Classe GrilleOccupation - Structure de données pour la carte 2D.
Chaque cellule : -1 (Inconnu), 0 (Libre), 1 (Occupé).
Gère le stockage spatial, la matrice en mémoire et les conversions de coordonnées.
"""

import numpy as np


class GrilleOccupation:
    """Grille d'occupation pour la cartographie du robot."""

    INCONNU = -1
    LIBRE = 0
    OCCUPE = 1

    def __init__(self, largeur_m, hauteur_m, resolution=0.1, origin_x=None, origin_y=None):
        self.__largeur_m = largeur_m
        self.__hauteur_m = hauteur_m
        self.__resolution = resolution

        # Taille de la matrice en nombre de cellules
        self.__nx = int(largeur_m / resolution)
        self.__ny = int(hauteur_m / resolution)

        # Origine du repère
        # Par défaut : centre de la grille (robot explorant autour de (0,0))
        # Pour une map fixe : origin_x=0, origin_y=0 (grille couvre [0, largeur] x [0, hauteur])
        self.__origin_x = origin_x if origin_x is not None else largeur_m / 2.0
        self.__origin_y = origin_y if origin_y is not None else hauteur_m / 2.0

        # Grille initialisée à INCONNU (-1)
        self.__grid = np.full((self.__nx, self.__ny), self.INCONNU, dtype=np.int8)

    # --- Properties (encapsulation) ---
    @property
    def largeur_m(self):
        return self.__largeur_m

    @property
    def hauteur_m(self):
        return self.__hauteur_m

    @property
    def resolution(self):
        return self.__resolution

    @property
    def nx(self):
        return self.__nx

    @property
    def ny(self):
        return self.__ny

    @property
    def grid(self):
        """Retourne une copie de la grille (lecture seule)."""
        return self.__grid.copy()

    # --- Conversions et Accesseurs ---
    def coord2index(self, x, y):
        """Convertit (x, y) en mètres vers (ix, iy) en indices.
        Bride les valeurs (clip) pour ne pas sortir de la matrice."""
        ix = int((x + self.__origin_x) / self.__resolution)
        iy = int((y + self.__origin_y) / self.__resolution)
        ix = max(0, min(ix, self.__nx - 1))
        iy = max(0, min(iy, self.__ny - 1))
        return ix, iy

    def index2coord(self, ix, iy):
        """Convertit (ix, iy) indices vers (x, y) en mètres (centre de la cellule)."""
        x = ix * self.__resolution - self.__origin_x + self.__resolution / 2.0
        y = iy * self.__resolution - self.__origin_y + self.__resolution / 2.0
        return x, y

    def get_cellule(self, ix, iy):
        """Retourne l'état de la cellule aux indices donnés."""
        return self.__grid[ix, iy]

    def set_cellule(self, ix, iy, etat):
        """Modifie l'état de la cellule aux indices donnés."""
        self.__grid[ix, iy] = etat

    def est_dans_grille(self, ix, iy):
        """Vérifie si les indices sont dans la grille."""
        return 0 <= ix < self.__nx and 0 <= iy < self.__ny

    def __str__(self):
        libre = np.sum(self.__grid == self.LIBRE)
        occupe = np.sum(self.__grid == self.OCCUPE)
        inconnu = np.sum(self.__grid == self.INCONNU)
        return (f"GrilleOccupation({self.__nx}x{self.__ny}, "
                f"res={self.__resolution}m, "
                f"libre={libre}, occupé={occupe}, inconnu={inconnu})")
