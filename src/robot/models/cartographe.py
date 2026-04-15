"""
Classe Cartographe - Algorithme de cartographie par lancer de rayon (Bresenham).
Utilise la composition : le Cartographe possède une GrilleOccupation.
"""

from robot.models.grille_occupation import GrilleOccupation


class Cartographe:
    """Algorithme de cartographie utilisant les données du Lidar
    pour remplir une GrilleOccupation via l'algorithme de Bresenham."""

    def __init__(self, grille: GrilleOccupation):
        self.__grille = grille  # Relation de composition

    @property
    def grille(self):
        return self.__grille

    def mise_a_jour(self, env, lidar):
        """Met à jour la grille à partir des rayons du Lidar."""
        rays = lidar.get_rays_world(env)
        for x1, y1, x2, y2, dist in rays:
            self._bresenham_update(x1, y1, x2, y2, dist, lidar.max_range)

    def _bresenham_update(self, x1, y1, x2, y2, dist, max_range):
        """Applique l'algorithme de Bresenham pour tracer le rayon dans la grille.
        Les cellules traversées sont marquées LIBRE, le point final est OCCUPE
        si le rayon a touché un obstacle (dist < max_range)."""

        # Convertir les coordonnées monde en indices de grille
        ix0, iy0 = self.__grille.coord2index(x1, y1)
        ix1, iy1 = self.__grille.coord2index(x2, y2)

        # Algorithme de Bresenham
        dx = abs(ix1 - ix0)
        dy = abs(iy1 - iy0)
        sx = 1 if ix0 < ix1 else -1
        sy = 1 if iy0 < iy1 else -1
        err = dx - dy

        while True:
            # Marquer la cellule courante comme LIBRE
            if self.__grille.est_dans_grille(ix0, iy0):
                self.__grille.set_cellule(ix0, iy0, GrilleOccupation.LIBRE)

            # Fin du rayon
            if ix0 == ix1 and iy0 == iy1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                ix0 += sx
            if e2 < dx:
                err += dx
                iy0 += sy

        # Si le rayon a touché un obstacle, marquer le point final comme OCCUPE
        if dist < max_range * 0.99:
            if self.__grille.est_dans_grille(ix1, iy1):
                self.__grille.set_cellule(ix1, iy1, GrilleOccupation.OCCUPE)
