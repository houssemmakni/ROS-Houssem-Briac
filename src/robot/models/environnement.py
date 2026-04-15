"""
Classe Environnement - Gestionnaire central de la simulation.
Contient le robot, les obstacles, les zombies et les projectiles.
Gère les collisions et la validation des mouvements.
"""

import logging

logger = logging.getLogger(__name__)


class Environnement:
    """Le monde simulé contenant toutes les entités."""

    def __init__(self, largeur=20.0, hauteur=15.0):
        self.__largeur = largeur
        self.__hauteur = hauteur
        self.__robot = None
        self.__obstacles = []
        self.__zombies = []
        self.__projectiles = []

    @property
    def largeur(self):
        return self.__largeur

    @property
    def hauteur(self):
        return self.__hauteur

    @property
    def robot(self):
        return self.__robot

    @property
    def obstacles(self):
        return self.__obstacles

    @property
    def zombies(self):
        return list(self.__zombies)

    @property
    def projectiles(self):
        return list(self.__projectiles)

    def ajouter_robot(self, robot):
        self.__robot = robot
        logger.info("Robot ajouté à l'environnement")

    def ajouter_obstacle(self, obstacle):
        self.__obstacles.append(obstacle)

    def ajouter_zombie(self, zombie):
        self.__zombies.append(zombie)

    def ajouter_projectile(self, projectile):
        self.__projectiles.append(projectile)

    def retirer_zombie(self, zombie):
        if zombie in self.__zombies:
            self.__zombies.remove(zombie)

    def retirer_projectile(self, projectile):
        if projectile in self.__projectiles:
            self.__projectiles.remove(projectile)

    def collision_obstacles(self, x, y, rayon) -> bool:
        """Vérifie si un cercle (x, y, rayon) entre en collision avec un obstacle."""
        # Limites du monde
        if x - rayon < 0 or x + rayon > self.__largeur:
            return True
        if y - rayon < 0 or y + rayon > self.__hauteur:
            return True
        # Obstacles
        for obs in self.__obstacles:
            if obs.collision(x, y, rayon):
                return True
        return False

    def collision_point_obstacles(self, x, y) -> bool:
        """Vérifie si un point est dans un obstacle ou hors limites."""
        if x < 0 or x > self.__largeur or y < 0 or y > self.__hauteur:
            return True
        for obs in self.__obstacles:
            if obs.collision(x, y, 0.05):
                return True
        return False

    def mettre_a_jour(self, dt, grille=None, planificateur=None):
        """Met à jour toutes les entités de l'environnement."""
        # 1. Mise à jour du robot avec validation collision
        if self.__robot:
            etat = self.__robot.sauvegarder_etat()
            self.__robot.mettre_a_jour(dt)

            # Clamp aux limites du monde
            r = self.__robot.rayon
            self.__robot.x = max(r, min(self.__robot.x, self.__largeur - r))
            self.__robot.y = max(r, min(self.__robot.y, self.__hauteur - r))

            # Annuler si collision avec obstacle
            if self._collision_robot_obstacles():
                self.__robot.restaurer_etat(etat)

        # 2. Mise à jour des zombies (avec pathfinding A* si disponible)
        zombies_morts = []
        for zombie in self.__zombies:
            zombie.mettre_a_jour(self, dt, grille=grille, planificateur=planificateur)
            if not zombie.est_vivant:
                zombies_morts.append(zombie)
        for z in zombies_morts:
            self.__zombies.remove(z)

        # 3. Mise à jour des projectiles
        projectiles_a_retirer = []
        for proj in self.__projectiles:
            proj.mettre_a_jour(dt)
            # Hors limites
            if (proj.x < -1 or proj.x > self.__largeur + 1 or
                    proj.y < -1 or proj.y > self.__hauteur + 1):
                projectiles_a_retirer.append(proj)
                continue
            # Collision obstacle
            if self.collision_point_obstacles(proj.x, proj.y):
                projectiles_a_retirer.append(proj)
                continue
            # Collision avec zombies (projectiles du joueur)
            if proj.est_joueur:
                for zombie in self.__zombies:
                    dx = proj.x - zombie.x
                    dy = proj.y - zombie.y
                    dist = (dx * dx + dy * dy) ** 0.5
                    if dist < zombie.rayon + 0.1:
                        zombie.subir_degat(proj.degats)
                        projectiles_a_retirer.append(proj)
                        break
            # Collision avec robot (projectiles ennemis)
            elif self.__robot and self.__robot.est_vivant:
                dx = proj.x - self.__robot.x
                dy = proj.y - self.__robot.y
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < self.__robot.rayon + 0.1:
                    self.__robot.subir_degat(degats=proj.degats)
                    projectiles_a_retirer.append(proj)

        for p in projectiles_a_retirer:
            if p in self.__projectiles:
                self.__projectiles.remove(p)

        # 4. Collision directe zombie -> robot (dégâts de contact)
        if self.__robot and self.__robot.est_vivant:
            for zombie in self.__zombies:
                dx = zombie.x - self.__robot.x
                dy = zombie.y - self.__robot.y
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < zombie.rayon + self.__robot.rayon:
                    self.__robot.subir_degat(degats=5)

    def _collision_robot_obstacles(self) -> bool:
        """Vérifie collision du robot avec les obstacles."""
        if not self.__robot:
            return False
        for obs in self.__obstacles:
            if obs.collision(self.__robot.x, self.__robot.y, self.__robot.rayon):
                return True
        return False
