"""
Classe PlanificateurAStar - Planification globale avec l'algorithme A*.
Calcule un chemin optimal entre deux points sur la GrilleOccupation.
Travaille avec les indices de la grille, retourne des coordonnées en mètres.
"""

import heapq
import math

from robot.models.navigation.grille_occupation import GrilleOccupation


class PlanificateurAStar:
    """Planificateur global A* sur une grille d'occupation."""

    def __init__(self, grille: GrilleOccupation):
        self.__grille = grille

    @property
    def grille(self):
        return self.__grille

    def heuristique(self, idx_a, idx_b):
        """Calcule la distance Euclidienne entre deux indices."""
        return math.sqrt((idx_a[0] - idx_b[0]) ** 2 + (idx_a[1] - idx_b[1]) ** 2)

    def trouver_chemin(self, depart_m, arrivee_m):
        """Calcule le chemin de depart_m (x, y) vers arrivee_m (x, y) en mètres.
        Retourne une liste de points (x, y) en mètres."""

        # 1. Convertir les coordonnées métriques en indices de grille
        start_idx = self.__grille.coord2index(*depart_m)
        goal_idx = self.__grille.coord2index(*arrivee_m)

        # 2. Vérifier que l'arrivée n'est pas dans un obstacle
        if self.__grille.get_cellule(*goal_idx) == GrilleOccupation.OCCUPE:
            return []

        # 3. Initialiser la file de priorité et les dictionnaires
        open_set = []
        heapq.heappush(open_set, (0, start_idx))

        came_from = {}
        g_score = {start_idx: 0}
        f_score = {start_idx: self.heuristique(start_idx, goal_idx)}

        # Voisins : 8 directions (cardinales + diagonales)
        voisins = [(-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (-1, 1), (1, -1), (1, 1)]

        # 4. Boucle principale A*
        while open_set:
            _, current = heapq.heappop(open_set)

            # Arrivée atteinte
            if current == goal_idx:
                # Reconstruire le chemin
                chemin_indices = []
                while current in came_from:
                    chemin_indices.append(current)
                    current = came_from[current]
                chemin_indices.append(start_idx)
                chemin_indices.reverse()

                # Convertir en coordonnées monde
                chemin_metres = []
                for ix, iy in chemin_indices:
                    x, y = self.__grille.index2coord(ix, iy)
                    chemin_metres.append((x, y))
                return chemin_metres

            # Explorer les voisins
            for dx, dy in voisins:
                nx, ny = current[0] + dx, current[1] + dy
                voisin = (nx, ny)

                # Vérifier que le voisin est dans la grille
                if not self.__grille.est_dans_grille(nx, ny):
                    continue

                # Vérifier que le voisin n'est pas un obstacle
                if self.__grille.get_cellule(nx, ny) == GrilleOccupation.OCCUPE:
                    continue

                # Coût du déplacement (1.0 cardinal, sqrt(2) diagonal)
                cout = math.sqrt(dx * dx + dy * dy)
                tentative_g = g_score[current] + cout

                if voisin not in g_score or tentative_g < g_score[voisin]:
                    came_from[voisin] = current
                    g_score[voisin] = tentative_g
                    f = tentative_g + self.heuristique(voisin, goal_idx)
                    f_score[voisin] = f
                    heapq.heappush(open_set, (f, voisin))

        # Aucun chemin trouvé
        return []
