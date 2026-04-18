"""
Classe PreEntrainement - Simulation acceleree sans affichage pour entrainer
les agents RL avant de lancer le jeu.

Simule des milliers de parties en quelques secondes :
- Le robot apprend a survivre (esquiver, se positionner)
- Les zombies apprennent a traquer le robot
"""

import math
import random
import logging

logger = logging.getLogger(__name__)


class PreEntrainement:
    """Simulateur headless pour pre-entrainer les agents Q-learning."""

    def __init__(self, largeur=20.0, hauteur=15.0):
        self.__largeur = largeur
        self.__hauteur = hauteur
        # Obstacles simplifies (rectangles comme bounding boxes)
        self.__obstacles = [
            (4.0, 6.0, 6.0, 6.3),
            (14.0, 6.0, 16.0, 6.3),
            (8.5, 3.0, 11.5, 4.0),
            (8.5, 11.0, 11.5, 12.0),
        ]

    def _collision(self, x, y, rayon):
        """Test de collision simplifie."""
        if x - rayon < 0 or x + rayon > self.__largeur:
            return True
        if y - rayon < 0 or y + rayon > self.__hauteur:
            return True
        for x1, y1, x2, y2 in self.__obstacles:
            # Point le plus proche sur le rectangle
            cx = max(x1, min(x, x2))
            cy = max(y1, min(y, y2))
            dx = x - cx
            dy = y - cy
            if dx * dx + dy * dy <= rayon * rayon:
                return True
        return False

    def _obstacle_devant(self, x, y, angle, dist=1.5):
        """Verifie s'il y a un obstacle dans la direction donnee."""
        check_x = x + math.cos(angle) * dist
        check_y = y + math.sin(angle) * dist
        return self._collision(check_x, check_y, 0.3)

    def _espace_confine(self, x, y, nb_directions=8, seuil=3.0):
        """Verifie si le robot est dans un espace confine (simule le Lidar).
        Moyenne des distances dans 8 directions < seuil = confine."""
        total = 0.0
        for i in range(nb_directions):
            angle = i * (2 * math.pi / nb_directions)
            for d_test in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]:
                cx = x + math.cos(angle) * d_test
                cy = y + math.sin(angle) * d_test
                if self._collision(cx, cy, 0.1):
                    total += d_test
                    break
            else:
                total += 4.0
        moyenne = total / nb_directions
        return moyenne < seuil

    def entrainer_robot(self, agent, nb_episodes=2000, max_steps=300):
        """Pre-entraine l'agent du robot.

        Simule des episodes ou le robot doit survivre face a des zombies
        qui foncent vers lui en ligne droite.
        """
        logger.info(f"Pre-entrainement robot : {nb_episodes} episodes...")

        for episode in range(nb_episodes):
            # Position initiale du robot
            rx, ry = 10.0, 7.5
            rpv = 100
            nb_zombies_initial = 3 + (episode // 200)
            nb_zombies_initial = min(nb_zombies_initial, 10)

            # Generer des zombies aux bords
            zombies = []
            for _ in range(nb_zombies_initial):
                bord = random.randint(0, 3)
                if bord == 0:
                    zx, zy = random.uniform(1, 19), 14.0
                elif bord == 1:
                    zx, zy = random.uniform(1, 19), 1.0
                elif bord == 2:
                    zx, zy = 1.0, random.uniform(1, 14)
                else:
                    zx, zy = 19.0, random.uniform(1, 14)
                zombies.append([zx, zy, 30])  # x, y, pv

            ancien_pv = rpv
            ancien_nb = len(zombies)

            for step in range(max_steps):
                if rpv <= 0 or not zombies:
                    break

                # Trouver le zombie le plus proche
                dist_min = float("inf")
                angle_min = 0.0
                nb_proches = 0
                for zx, zy, zpv in zombies:
                    d = math.sqrt((zx - rx) ** 2 + (zy - ry) ** 2)
                    if d < dist_min:
                        dist_min = d
                        angle_min = math.atan2(zy - ry, zx - rx)
                        if angle_min < 0:
                            angle_min += 2 * math.pi
                    if d < 3.0:
                        nb_proches += 1

                # Simuler le Lidar (8 directions)
                obstacle_devant = self._obstacle_devant(rx, ry, angle_min, 1.5)
                espace_confine = self._espace_confine(rx, ry)

                # Etat et action du robot (action = mouvement + arme + Lidar)
                ratio_pv = rpv / 100.0
                etat = agent.discretiser_etat(angle_min, dist_min, nb_proches, ratio_pv,
                                              obstacle_devant=obstacle_devant,
                                              espace_confine=espace_confine)
                action = agent.choisir_action(etat)
                direction = agent.get_direction(action)
                arme_idx = agent.get_arme(action)

                # Deplacer le robot
                collision_mur = False
                if direction is not None:
                    new_rx = rx + math.cos(direction) * 3.5 * (1 / 60)
                    new_ry = ry + math.sin(direction) * 3.5 * (1 / 60)
                    if not self._collision(new_rx, new_ry, 0.3):
                        rx, ry = new_rx, new_ry
                    else:
                        collision_mur = True

                # Stats des armes : (degats, portee, proba_toucher)
                armes_stats = [
                    (25, 12.0, 0.30),  # 0: fusil
                    (15, 5.0, 0.50),   # 1: fusil a pompe (5 projectiles -> plus de chance)
                    (35, 15.0, 0.25),  # 2: laser
                    (8, 3.0, 0.70),    # 3: lance-flamme (3 particules -> haute proba)
                ]
                degats_arme, portee_arme, proba_arme = armes_stats[arme_idx]

                # Le robot tire avec l'arme choisie par le RL
                zombies_vivants = []
                for zx, zy, zpv in zombies:
                    d = math.sqrt((zx - rx) ** 2 + (zy - ry) ** 2)
                    if d <= portee_arme and d == dist_min and random.random() < proba_arme:
                        zpv -= degats_arme
                    if zpv > 0:
                        zombies_vivants.append([zx, zy, zpv])

                # Deplacer les zombies vers le robot
                for z in zombies_vivants:
                    dx = rx - z[0]
                    dy = ry - z[1]
                    d = math.sqrt(dx * dx + dy * dy)
                    if d > 0.6:
                        speed = 1.0 * (1 / 60)
                        z[0] += (dx / d) * speed
                        z[1] += (dy / d) * speed

                # Degats de contact
                for z in zombies_vivants:
                    d = math.sqrt((z[0] - rx) ** 2 + (z[1] - ry) ** 2)
                    if d < 0.6:
                        rpv -= 5

                # Recompense
                est_mort = rpv <= 0
                nb_actuel = len(zombies_vivants)
                recompense = agent.calculer_recompense(
                    ancien_pv, rpv, ancien_nb, nb_actuel, est_mort,
                    collision_mur=collision_mur,
                )

                # Nouvel etat
                if zombies_vivants:
                    d2 = float("inf")
                    a2 = 0.0
                    np2 = 0
                    for zx, zy, zpv in zombies_vivants:
                        d = math.sqrt((zx - rx) ** 2 + (zy - ry) ** 2)
                        if d < d2:
                            d2 = d
                            a2 = math.atan2(zy - ry, zx - rx)
                            if a2 < 0:
                                a2 += 2 * math.pi
                        if d < 3.0:
                            np2 += 1
                    obs2 = self._obstacle_devant(rx, ry, a2, 1.5)
                    esp2 = self._espace_confine(rx, ry)
                    etat2 = agent.discretiser_etat(a2, d2, np2, rpv / 100.0,
                                                   obstacle_devant=obs2, espace_confine=esp2)
                else:
                    etat2 = agent.discretiser_etat(0, 20, 0, rpv / 100.0,
                                                   obstacle_devant=False, espace_confine=False)

                agent.mettre_a_jour(etat, action, recompense, etat2)

                kills = ancien_nb - nb_actuel
                for _ in range(kills):
                    agent.ajouter_kill()

                ancien_pv = rpv
                ancien_nb = nb_actuel
                zombies = zombies_vivants

        logger.info(f"Pre-entrainement robot termine : {agent}")

    def entrainer_zombies(self, agent, nb_episodes=2000, max_steps=200):
        """Pre-entraine l'agent des zombies.

        Simule des episodes ou un zombie doit atteindre le robot
        qui bouge aleatoirement.
        """
        logger.info(f"Pre-entrainement zombies : {nb_episodes} episodes...")

        for episode in range(nb_episodes):
            # Robot a une position aleatoire
            rx = random.uniform(3, 17)
            ry = random.uniform(3, 12)
            # Zombie spawn sur un bord
            bord = random.randint(0, 3)
            if bord == 0:
                zx, zy = random.uniform(1, 19), 14.0
            elif bord == 1:
                zx, zy = random.uniform(1, 19), 1.0
            elif bord == 2:
                zx, zy = 1.0, random.uniform(1, 14)
            else:
                zx, zy = 19.0, random.uniform(1, 14)

            for step in range(max_steps):
                dx = rx - zx
                dy = ry - zy
                dist = math.sqrt(dx * dx + dy * dy)

                if dist < 0.6:
                    # Touche le robot
                    angle = math.atan2(dy, dx)
                    if angle < 0:
                        angle += 2 * math.pi
                    obs_devant = self._obstacle_devant(zx, zy, angle)
                    etat = agent.discretiser_etat(angle, dist, obs_devant)
                    action = agent.choisir_action(etat)
                    r = agent.calculer_recompense(dist, 0.0, False, True)
                    agent.mettre_a_jour(etat, action, r, etat)
                    break

                angle = math.atan2(dy, dx)
                if angle < 0:
                    angle += 2 * math.pi
                obs_devant = self._obstacle_devant(zx, zy, angle)
                etat = agent.discretiser_etat(angle, dist, obs_devant)
                action = agent.choisir_action(etat)

                # Deplacer le zombie
                move_angle = agent.get_direction_angle(action)
                speed = 1.5 * (1 / 60)
                new_zx = zx + math.cos(move_angle) * speed
                new_zy = zy + math.sin(move_angle) * speed

                collision = self._collision(new_zx, new_zy, 0.3)
                if not collision:
                    zx, zy = new_zx, new_zy

                # Nouvelle distance
                new_dist = math.sqrt((rx - zx) ** 2 + (ry - zy) ** 2)
                new_angle = math.atan2(ry - zy, rx - zx)
                if new_angle < 0:
                    new_angle += 2 * math.pi
                new_obs = self._obstacle_devant(zx, zy, new_angle)
                etat2 = agent.discretiser_etat(new_angle, new_dist, new_obs)

                r = agent.calculer_recompense(dist, new_dist, collision, False)
                agent.mettre_a_jour(etat, action, r, etat2)

                # Le robot bouge aleatoirement
                rx += random.uniform(-0.03, 0.03)
                ry += random.uniform(-0.03, 0.03)
                rx = max(1, min(rx, 19))
                ry = max(1, min(ry, 14))

        logger.info(f"Pre-entrainement zombies termine : {agent}")
