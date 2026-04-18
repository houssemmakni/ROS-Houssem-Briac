"""
Classes Vue - Affichage de la simulation.
VuePygame : visualisation graphique temps réel avec Pygame.
"""

import math
import pygame


class VuePygame:
    """Vue Pygame pour le jeu de survie zombie."""

    # Couleurs
    COULEUR_FOND = (30, 30, 30)
    COULEUR_SOL = (50, 55, 50)
    COULEUR_GRILLE = (40, 45, 40)
    COULEUR_MUR = (100, 100, 110)
    COULEUR_ROBOT = (0, 150, 255)
    COULEUR_ROBOT_INVINCIBLE = (100, 200, 255)
    COULEUR_ZOMBIE = (0, 200, 50)
    COULEUR_ZOMBIE_ARME = (200, 50, 0)
    COULEUR_OBSTACLE = (80, 80, 90)
    COULEUR_TEXTE = (220, 220, 220)
    COULEUR_VIE = (220, 50, 50)
    COULEUR_VIE_PERDUE = (80, 30, 30)
    COULEUR_BARRE_PV = (200, 0, 0)
    COULEUR_BARRE_PV_FOND = (60, 60, 60)

    def __init__(self, largeur=1000, hauteur=750, scale=50):
        pygame.init()
        pygame.display.set_caption("Robot Zombie Survival")
        self.__screen = pygame.display.set_mode((largeur, hauteur))
        self.__largeur = largeur
        self.__hauteur = hauteur
        self.__scale = scale
        self.__clock = pygame.time.Clock()
        self.__font = pygame.font.SysFont("monospace", 18, bold=True)
        self.__font_big = pygame.font.SysFont("monospace", 36, bold=True)
        self.__font_small = pygame.font.SysFont("monospace", 14)
        self.__font_titre = pygame.font.SysFont("monospace", 48, bold=True)
        self.__offset_x = 0
        self.__offset_y = 0

    @property
    def screen(self):
        return self.__screen

    def convertir_coordonnees(self, x, y):
        """Convertit coordonnées monde (mètres) vers pixels écran."""
        px = int(self.__offset_x + x * self.__scale)
        py = int(self.__hauteur - self.__offset_y - y * self.__scale)
        return px, py

    def convertir_ecran_vers_monde(self, px, py):
        """Convertit pixels écran vers coordonnées monde."""
        x = (px - self.__offset_x) / self.__scale
        y = (self.__hauteur - py - self.__offset_y) / self.__scale
        return x, y

    def dessiner(self, env, wave_manager, arme_courante, armes, index_arme,
                 grille=None, difficulte=None, rl_agent=None,
                 auto_play=False, rl_robot_agent=None):
        """Dessine l'etat complet du jeu."""
        self.__screen.fill(self.COULEUR_FOND)

        # Vue fixe : la map est centrée dans la fenêtre
        self.__offset_x = 0
        self.__offset_y = 0

        # Dessiner le sol
        self._dessiner_sol(env)

        # Dessiner les obstacles
        for obs in env.obstacles:
            self._dessiner_obstacle(obs)

        # Dessiner les projectiles
        for proj in env.projectiles:
            self._dessiner_projectile(proj)

        # Dessiner les zombies
        for zombie in env.zombies:
            self._dessiner_zombie(zombie)

        # Dessiner le robot
        if env.robot:
            self._dessiner_robot(env.robot, arme_courante)

        # Dessiner le HUD
        self._dessiner_hud(env, wave_manager, arme_courante, armes, index_arme,
                           difficulte=difficulte, rl_agent=rl_agent,
                           auto_play=auto_play, rl_robot_agent=rl_robot_agent)

        # Dessiner la minimap (cartographie)
        if grille:
            self._dessiner_minimap(grille, env)

        pygame.display.flip()

    def _dessiner_sol(self, env):
        """Dessine le sol avec une grille."""
        # Fond de la map
        x0, y0 = self.convertir_coordonnees(0, env.hauteur)
        w = int(env.largeur * self.__scale)
        h = int(env.hauteur * self.__scale)
        pygame.draw.rect(self.__screen, self.COULEUR_SOL, (x0, y0, w, h))

        # Grille
        for i in range(int(env.largeur) + 1):
            p1 = self.convertir_coordonnees(i, 0)
            p2 = self.convertir_coordonnees(i, env.hauteur)
            pygame.draw.line(self.__screen, self.COULEUR_GRILLE, p1, p2, 1)
        for j in range(int(env.hauteur) + 1):
            p1 = self.convertir_coordonnees(0, j)
            p2 = self.convertir_coordonnees(env.largeur, j)
            pygame.draw.line(self.__screen, self.COULEUR_GRILLE, p1, p2, 1)

        # Bordures
        coins = [
            self.convertir_coordonnees(0, 0),
            self.convertir_coordonnees(env.largeur, 0),
            self.convertir_coordonnees(env.largeur, env.hauteur),
            self.convertir_coordonnees(0, env.hauteur),
        ]
        pygame.draw.lines(self.__screen, self.COULEUR_MUR, True, coins, 3)

    def _dessiner_obstacle(self, obs):
        """Dessine un obstacle (rectangle ou cercle)."""
        from robot.models.obstacles.obstacle_rectangle import ObstacleRectangle
        from robot.models.obstacles.obstacle_circulaire import ObstacleCirculaire

        if isinstance(obs, ObstacleRectangle):
            x0, y0 = self.convertir_coordonnees(obs.x, obs.y + obs.hauteur)
            w = int(obs.largeur * self.__scale)
            h = int(obs.hauteur * self.__scale)
            pygame.draw.rect(self.__screen, self.COULEUR_OBSTACLE, (x0, y0, w, h))
            pygame.draw.rect(self.__screen, (120, 120, 130), (x0, y0, w, h), 2)

        elif isinstance(obs, ObstacleCirculaire):
            cx, cy = self.convertir_coordonnees(obs.x, obs.y)
            r = int(obs.rayon * self.__scale)
            pygame.draw.circle(self.__screen, self.COULEUR_OBSTACLE, (cx, cy), r)
            pygame.draw.circle(self.__screen, (120, 120, 130), (cx, cy), r, 2)

    def _dessiner_robot(self, robot, arme):
        """Dessine le robot joueur."""
        px, py = self.convertir_coordonnees(robot.x, robot.y)
        r = int(robot.rayon * self.__scale)

        # Corps du robot
        couleur = self.COULEUR_ROBOT_INVINCIBLE if robot.est_invincible else self.COULEUR_ROBOT
        if robot.est_invincible:
            # Effet de clignotement
            import time
            if int(time.time() * 8) % 2 == 0:
                couleur = (200, 200, 255)

        pygame.draw.circle(self.__screen, couleur, (px, py), r)
        pygame.draw.circle(self.__screen, (255, 255, 255), (px, py), r, 2)

        # Direction (orientation vers la souris)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mx, my = self.convertir_ecran_vers_monde(mouse_x, mouse_y)
        angle = math.atan2(my - robot.y, mx - robot.x)

        x_dir = px + int((r + 8) * math.cos(angle))
        y_dir = py - int((r + 8) * math.sin(angle))
        pygame.draw.line(self.__screen, (255, 255, 255), (px, py), (x_dir, y_dir), 3)

        # Nom de l'arme au-dessus du robot
        if arme:
            txt = self.__font_small.render(arme.nom, True, (200, 200, 200))
            self.__screen.blit(txt, (px - txt.get_width() // 2, py - r - 20))

    def _dessiner_zombie(self, zombie):
        """Dessine un zombie avec sa barre de vie."""
        px, py = self.convertir_coordonnees(zombie.x, zombie.y)
        r = int(zombie.rayon * self.__scale)

        # Corps - couleur différente si armé
        couleur = self.COULEUR_ZOMBIE_ARME if zombie.arme else self.COULEUR_ZOMBIE
        pygame.draw.circle(self.__screen, couleur, (px, py), r)
        pygame.draw.circle(self.__screen, (0, 100, 0), (px, py), r, 2)

        # Yeux
        eye_offset = r // 3
        angle = zombie.orientation
        ex1 = px + int(eye_offset * math.cos(angle + 0.5))
        ey1 = py - int(eye_offset * math.sin(angle + 0.5))
        ex2 = px + int(eye_offset * math.cos(angle - 0.5))
        ey2 = py - int(eye_offset * math.sin(angle - 0.5))
        pygame.draw.circle(self.__screen, (255, 0, 0), (ex1, ey1), 3)
        pygame.draw.circle(self.__screen, (255, 0, 0), (ex2, ey2), 3)

        # Barre de PV
        bar_w = r * 2
        bar_h = 4
        bar_x = px - bar_w // 2
        bar_y = py - r - 10
        ratio = zombie.pv / zombie.pv_max
        pygame.draw.rect(self.__screen, self.COULEUR_BARRE_PV_FOND, (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(self.__screen, self.COULEUR_BARRE_PV, (bar_x, bar_y, int(bar_w * ratio), bar_h))

    def _dessiner_projectile(self, proj):
        """Dessine un projectile."""
        px, py = self.convertir_coordonnees(proj.x, proj.y)
        taille = proj.taille

        if proj.est_flamme:
            # Effet de flamme avec particules
            import random
            for _ in range(3):
                ox = random.randint(-3, 3)
                oy = random.randint(-3, 3)
                r = random.randint(2, taille + 2)
                c = (255, random.randint(50, 200), 0)
                pygame.draw.circle(self.__screen, c, (px + ox, py + oy), r)
        else:
            pygame.draw.circle(self.__screen, proj.couleur, (px, py), taille)

    def _dessiner_hud(self, env, wave_manager, arme, armes, index_arme,
                      difficulte=None, rl_agent=None,
                      auto_play=False, rl_robot_agent=None):
        """Dessine l'interface utilisateur (PV, arme, vague, score, difficulte)."""
        robot = env.robot
        if not robot:
            return

        # Panneau HUD en haut
        panel_h = 60
        panel = pygame.Surface((self.__largeur, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        self.__screen.blit(panel, (0, 0))

        # Barre de PV du robot
        hp_x, hp_y = 15, 10
        hp_w, hp_h = 110, 18
        ratio_pv = robot.pv / robot.pv_max
        # Fond
        pygame.draw.rect(self.__screen, (40, 40, 40), (hp_x, hp_y, hp_w, hp_h), border_radius=3)
        # Barre (couleur selon PV restants)
        if ratio_pv > 0.5:
            couleur_hp = (50, 200, 50)
        elif ratio_pv > 0.25:
            couleur_hp = (220, 180, 30)
        else:
            couleur_hp = (220, 40, 40)
        if ratio_pv > 0:
            pygame.draw.rect(self.__screen, couleur_hp,
                             (hp_x, hp_y, int(hp_w * ratio_pv), hp_h), border_radius=3)
        # Contour
        pygame.draw.rect(self.__screen, (150, 150, 150), (hp_x, hp_y, hp_w, hp_h), 1, border_radius=3)
        # Texte PV
        pv_txt = self.__font_small.render(f"{robot.pv}/{robot.pv_max}", True, (255, 255, 255))
        self.__screen.blit(pv_txt, (hp_x + hp_w // 2 - pv_txt.get_width() // 2, hp_y + 2))

        # Vague
        vague_txt = self.__font.render(f"Vague: {wave_manager.vague_actuelle}", True, self.COULEUR_TEXTE)
        self.__screen.blit(vague_txt, (140, 5))

        # Timer prochaine vague
        timer_txt = self.__font_small.render(f"Prochaine: {wave_manager.timer:.1f}s", True, (180, 180, 180))
        self.__screen.blit(timer_txt, (140, 30))

        # Score
        score_txt = self.__font.render(f"Score: {wave_manager.score}", True, (255, 215, 0))
        self.__screen.blit(score_txt, (350, 5))

        # Zombies restants
        zr_txt = self.__font_small.render(f"Zombies: {wave_manager.zombies_restants}", True, (200, 100, 100))
        self.__screen.blit(zr_txt, (350, 30))

        # Arme courante + munitions
        if arme:
            arme_txt = self.__font.render(f"{arme.nom}: {arme.munitions}/{arme.munitions_max}", True, (255, 200, 100))
            self.__screen.blit(arme_txt, (550, 5))

            # Barre de munitions
            bar_x, bar_y = 550, 32
            bar_w, bar_h = 200, 12
            ratio = arme.munitions / arme.munitions_max
            pygame.draw.rect(self.__screen, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
            couleur_barre = (100, 255, 100) if ratio > 0.3 else (255, 100, 100)
            pygame.draw.rect(self.__screen, couleur_barre, (bar_x, bar_y, int(bar_w * ratio), bar_h))

        # Indicateur de difficulte (en haut a droite)
        if difficulte:
            from robot.models.difficulte import Difficulte
            cfg = Difficulte.get_config(difficulte)
            couleurs_diff = {
                Difficulte.FACILE: (100, 200, 100),
                Difficulte.DIFFICILE: (255, 180, 50),
                Difficulte.IMPOSSIBLE: (255, 50, 50),
            }
            c = couleurs_diff.get(difficulte, (200, 200, 200))
            diff_txt = self.__font.render(cfg["nom"], True, c)
            self.__screen.blit(diff_txt, (self.__largeur - diff_txt.get_width() - 15, 5))

            # Stats RL (mode Impossible)
            if rl_agent and difficulte == Difficulte.IMPOSSIBLE:
                rl_txt = self.__font_small.render(
                    f"RL: {rl_agent.total_updates} updates | "
                    f"explore: {rl_agent.epsilon:.0%}",
                    True, (255, 150, 150))
                self.__screen.blit(rl_txt, (self.__largeur - rl_txt.get_width() - 15, 30))

        # Indicateur auto-play
        if auto_play:
            ap_txt = self.__font.render("AUTO-PLAY (RL)", True, (0, 255, 200))
            ap_x = self.__largeur // 2 - ap_txt.get_width() // 2
            pygame.draw.rect(self.__screen, (0, 80, 60), (ap_x - 8, 3, ap_txt.get_width() + 16, 24), border_radius=4)
            self.__screen.blit(ap_txt, (ap_x, 5))

            if rl_robot_agent:
                rl_r_txt = self.__font_small.render(
                    f"Robot RL: {rl_robot_agent.total_updates} updates | "
                    f"explore: {rl_robot_agent.epsilon:.0%} | "
                    f"kills: {rl_robot_agent.kills}",
                    True, (0, 220, 180))
                self.__screen.blit(rl_r_txt, (self.__largeur // 2 - rl_r_txt.get_width() // 2, 32))

        # Selecteur d'armes en bas
        self._dessiner_selecteur_armes(armes, index_arme)

    def _dessiner_selecteur_armes(self, armes, index_arme):
        """Dessine le sélecteur d'armes en bas de l'écran."""
        y = self.__hauteur - 50
        total_w = len(armes) * 140
        start_x = (self.__largeur - total_w) // 2

        for i, a in enumerate(armes):
            x = start_x + i * 140
            w, h = 130, 40

            # Fond
            couleur_fond = (60, 80, 120) if i == index_arme else (40, 40, 50)
            pygame.draw.rect(self.__screen, couleur_fond, (x, y, w, h), border_radius=5)
            if i == index_arme:
                pygame.draw.rect(self.__screen, (100, 150, 255), (x, y, w, h), 2, border_radius=5)

            # Touche
            key_txt = self.__font_small.render(f"[{i + 1}]", True, (150, 150, 150))
            self.__screen.blit(key_txt, (x + 5, y + 3))

            # Nom
            nom_txt = self.__font_small.render(a.nom, True, (220, 220, 220))
            self.__screen.blit(nom_txt, (x + 30, y + 3))

            # Munitions
            mun_txt = self.__font_small.render(f"{a.munitions}/{a.munitions_max}", True, (180, 180, 180))
            self.__screen.blit(mun_txt, (x + 30, y + 20))

    def _dessiner_minimap(self, grille, env):
        """Dessine la minimap (grille d'occupation) en bas à droite."""
        from robot.models.navigation.grille_occupation import GrilleOccupation

        # Taille et position de la minimap
        map_w = 160
        map_h = int(map_w * grille.ny / grille.nx)
        map_x = self.__largeur - map_w - 10
        map_y = self.__hauteur - map_h - 60  # au-dessus du sélecteur d'armes

        # Fond semi-transparent
        panel = pygame.Surface((map_w + 4, map_h + 4), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        self.__screen.blit(panel, (map_x - 2, map_y - 2))

        # Taille d'une cellule en pixels
        cell_w = map_w / grille.nx
        cell_h = map_h / grille.ny

        grid_data = grille.grid
        for ix in range(grille.nx):
            for iy in range(grille.ny):
                val = grid_data[ix, iy]
                if val == GrilleOccupation.INCONNU:
                    continue  # ne pas dessiner les cellules inconnues (fond noir)
                px = int(map_x + ix * cell_w)
                # Y inversé : iy=0 en bas de la minimap
                py = int(map_y + map_h - (iy + 1) * cell_h)
                pw = max(1, int(cell_w))
                ph = max(1, int(cell_h))
                if val == GrilleOccupation.LIBRE:
                    pygame.draw.rect(self.__screen, (40, 60, 40), (px, py, pw, ph))
                elif val == GrilleOccupation.OCCUPE:
                    pygame.draw.rect(self.__screen, (180, 180, 200), (px, py, pw, ph))

        # Position du robot sur la minimap
        if env.robot:
            rx = int(map_x + (env.robot.x / grille.largeur_m) * map_w)
            ry = int(map_y + map_h - (env.robot.y / grille.hauteur_m) * map_h)
            pygame.draw.circle(self.__screen, (0, 150, 255), (rx, ry), 4)

        # Positions des zombies sur la minimap
        for zombie in env.zombies:
            zx = int(map_x + (zombie.x / grille.largeur_m) * map_w)
            zy = int(map_y + map_h - (zombie.y / grille.hauteur_m) * map_h)
            pygame.draw.circle(self.__screen, (255, 50, 50), (zx, zy), 2)

        # Bordure
        pygame.draw.rect(self.__screen, (100, 100, 100), (map_x - 2, map_y - 2, map_w + 4, map_h + 4), 1)

        # Label
        txt = self.__font_small.render("Carte", True, (150, 150, 150))
        self.__screen.blit(txt, (map_x, map_y - 16))

    def dessiner_game_over(self, wave_manager, difficulte=None, rl_agent=None,
                           auto_play=False, rl_robot_agent=None):
        """Affiche l'ecran de Game Over."""
        overlay = pygame.Surface((self.__largeur, self.__hauteur), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.__screen.blit(overlay, (0, 0))

        titre = self.__font_titre.render("GAME OVER", True, (220, 50, 50))
        self.__screen.blit(titre, (self.__largeur // 2 - titre.get_width() // 2, 180))

        score = self.__font_big.render(f"Score: {wave_manager.score}", True, (255, 215, 0))
        self.__screen.blit(score, (self.__largeur // 2 - score.get_width() // 2, 260))

        vague = self.__font.render(f"Vague atteinte: {wave_manager.vague_actuelle}", True, self.COULEUR_TEXTE)
        self.__screen.blit(vague, (self.__largeur // 2 - vague.get_width() // 2, 320))

        if difficulte:
            from robot.models.difficulte import Difficulte
            cfg = Difficulte.get_config(difficulte)
            diff_txt = self.__font.render(f"Difficulte: {cfg['nom']}", True, (180, 180, 180))
            self.__screen.blit(diff_txt, (self.__largeur // 2 - diff_txt.get_width() // 2, 360))

        if rl_agent and difficulte == "impossible":
            rl_txt = self.__font_small.render(
                f"RL: {rl_agent.total_updates} mises a jour | "
                f"Les zombies continueront d'apprendre a la prochaine partie!",
                True, (255, 150, 150))
            self.__screen.blit(rl_txt, (self.__largeur // 2 - rl_txt.get_width() // 2, 395))

        restart = self.__font.render("[R] Choisir difficulte  |  [ECHAP] Quitter", True, (180, 180, 180))
        self.__screen.blit(restart, (self.__largeur // 2 - restart.get_width() // 2, 440))

        pygame.display.flip()

    def dessiner_ecran_titre(self):
        """Affiche l'ecran titre."""
        self.__screen.fill(self.COULEUR_FOND)

        titre = self.__font_titre.render("ROBOT ZOMBIE SURVIVAL", True, (0, 200, 100))
        self.__screen.blit(titre, (self.__largeur // 2 - titre.get_width() // 2, 150))

        instructions = [
            "ZQSD / Fleches : Se deplacer",
            "Souris : Viser",
            "Clic gauche : Tirer",
            "1-2-3-4 : Changer d'arme",
            "",
            "Survivez aux vagues de zombies!",
            "100 PV - Munitions auto-regen",
            "",
            "Appuyez sur [ESPACE] pour continuer",
        ]

        for i, line in enumerate(instructions):
            couleur = (255, 215, 0) if "ESPACE" in line else self.COULEUR_TEXTE
            txt = self.__font.render(line, True, couleur)
            self.__screen.blit(txt, (self.__largeur // 2 - txt.get_width() // 2, 280 + i * 30))

        pygame.display.flip()

    def dessiner_ecran_difficulte(self, selection, rl_agent=None,
                                  auto_play=False, rl_robot_agent=None):
        """Affiche l'ecran de selection de difficulte."""
        self.__screen.fill(self.COULEUR_FOND)

        titre = self.__font_titre.render("DIFFICULTE", True, self.COULEUR_TEXTE)
        self.__screen.blit(titre, (self.__largeur // 2 - titre.get_width() // 2, 80))

        niveaux = [
            {
                "nom": "FACILE",
                "desc": ["Zombies lents, peu de PV", "150 PV robot", "Vagues toutes les 20s", "Pas de zombies armes"],
                "couleur": (100, 220, 100),
                "touche": "[1]",
            },
            {
                "nom": "DIFFICILE",
                "desc": ["Zombies rapides et resistants", "80 PV robot", "Vagues toutes les 12s", "Armes des la vague 3"],
                "couleur": (255, 180, 50),
                "touche": "[2]",
            },
            {
                "nom": "IMPOSSIBLE (RL)",
                "desc": ["Zombies avec Intelligence Artificielle", "60 PV robot", "Vagues toutes les 10s",
                         "Q-Learning : ils apprennent en jouant!"],
                "couleur": (255, 50, 50),
                "touche": "[3]",
            },
        ]

        card_w, card_h = 260, 200
        total_w = len(niveaux) * (card_w + 20) - 20
        start_x = (self.__largeur - total_w) // 2
        start_y = 180

        for i, niv in enumerate(niveaux):
            x = start_x + i * (card_w + 20)
            y = start_y
            selected = (i == selection)

            # Carte
            fond = (50, 60, 70) if selected else (35, 40, 45)
            pygame.draw.rect(self.__screen, fond, (x, y, card_w, card_h), border_radius=8)
            if selected:
                pygame.draw.rect(self.__screen, niv["couleur"], (x, y, card_w, card_h), 3, border_radius=8)

            # Touche
            key = self.__font_small.render(niv["touche"], True, (150, 150, 150))
            self.__screen.blit(key, (x + 10, y + 10))

            # Nom
            nom = self.__font_big.render(niv["nom"], True, niv["couleur"])
            scale_factor = min(1.0, (card_w - 20) / max(nom.get_width(), 1))
            if scale_factor < 1.0:
                nom = self.__font.render(niv["nom"], True, niv["couleur"])
            self.__screen.blit(nom, (x + card_w // 2 - nom.get_width() // 2, y + 35))

            # Description
            for j, line in enumerate(niv["desc"]):
                txt = self.__font_small.render(line, True, (180, 180, 180))
                self.__screen.blit(txt, (x + card_w // 2 - txt.get_width() // 2, y + 85 + j * 22))

        # RL info
        if rl_agent:
            rl_info = self.__font_small.render(
                f"Agent RL existant : {rl_agent.total_updates} mises a jour, "
                f"exploration: {rl_agent.epsilon:.0%}",
                True, (255, 150, 150))
            self.__screen.blit(rl_info, (self.__largeur // 2 - rl_info.get_width() // 2, 420))

        # Toggle auto-play
        ap_color = (0, 255, 200) if auto_play else (120, 120, 120)
        ap_status = "ON" if auto_play else "OFF"
        ap_txt = self.__font.render(f"[TAB] Auto-play (Robot RL) : {ap_status}", True, ap_color)
        self.__screen.blit(ap_txt, (self.__largeur // 2 - ap_txt.get_width() // 2, 450))

        if auto_play and rl_robot_agent:
            rl_r = self.__font_small.render(
                f"Agent Robot RL : {rl_robot_agent.total_updates} updates, "
                f"kills: {rl_robot_agent.kills}",
                True, (0, 200, 170))
            self.__screen.blit(rl_r, (self.__largeur // 2 - rl_r.get_width() // 2, 478))

        # Instructions
        instr = self.__font.render("[1] [2] [3] pour choisir, [ESPACE] pour lancer",
                                   True, (255, 215, 0))
        self.__screen.blit(instr, (self.__largeur // 2 - instr.get_width() // 2, 510))

        pygame.display.flip()

    def tick(self, fps=60):
        self.__clock.tick(fps)
        return self.__clock.get_fps()

    def fermer(self):
        pygame.quit()
