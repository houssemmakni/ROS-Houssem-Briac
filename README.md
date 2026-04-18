# Robot Zombie Survival

Simulation robotique mobile en Python avec Pygame -- Jeu de survie zombie.

Projet réalisé par : Houssem Makni et Briac Leclercq

Projet realise dans le cadre du cours **Programmation Orientee Objet a destination de la robotique** (M2, annee 2025-2026).
Enseignant : Adam GOUGUET

REPOSITORY GITHUB : https://github.com/houssemmakni/ROS-Houssem-Briac

---

## Sommaire

1. [Description du projet](#description-du-projet)
2. [Gameplay](#gameplay)
3. [Installation](#installation)
4. [Lancement](#lancement)
5. [Controles](#controles)
6. [Architecture du projet](#architecture-du-projet)
7. [Diagramme de classes](#diagramme-de-classes)
8. [Detail des classes](#detail-des-classes)
   - [Models (Modele)](#models-modele)
   - [Views (Vue)](#views-vue)
   - [Controllers (Controleur)](#controllers-controleur)
9. [Design Patterns utilises](#design-patterns-utilises)
10. [Formules mathematiques](#formules-mathematiques)
11. [Fonctionnalites implementees](#fonctionnalites-implementees)
12. [Dependances](#dependances)
13. [Membres du groupe](#membres-du-groupe)

---

## Description du projet

Un robot mobile evolue dans une arene 2D et doit survivre a des vagues de zombies de plus en plus difficiles. Le projet met en pratique les concepts fondamentaux de la POO (classes abstraites, heritage, polymorphisme, encapsulation, composition) ainsi que les principes de la robotique mobile (cinematique, capteurs, navigation autonome, cartographie).

Le jeu est construit sur une architecture **MVC** (Modele-Vue-Controleur) stricte, ou chaque fichier contient une seule classe.

---

## Gameplay

**Objectif** : Survivez le plus de vagues possible en eliminant tous les zombies.

### Regles generales

- Le robot joueur possede une **barre de PV** (points de vie)
- Le contact avec un zombie inflige **5 degats**
- Les projectiles ennemis infligent des degats variables
- Les munitions se regenerent automatiquement (1 munition toutes les 0.8s)
- Une nouvelle vague de zombies apparait a intervalle regulier
- Chaque vague apporte plus de zombies avec plus de PV et de vitesse
- **4 armes** disponibles : Fusil, Fusil a pompe, Laser, Lance-flamme
- **Minimap** en temps reel (grille d'occupation construite par le Lidar)

### Mode Facile

Le mode ideal pour decouvrir le jeu et s'entrainer.

- **150 PV** pour le robot (marge d'erreur confortable)
- Zombies **lents** (vitesse x0.6) et **fragiles** (PV x0.5)
- Vagues toutes les **20 secondes** (temps de souffler entre les vagues)
- Maximum **15 zombies** par vague
- Les zombies ne sont **jamais armes** (pas de tirs ennemis)
- IA des zombies : **A* + GoalStrategy** (navigation planifiee avec evitement d'obstacles)

### Mode Difficile

Pour les joueurs qui maitrisent les bases et veulent un vrai defi.

- **80 PV** pour le robot (peu de marge d'erreur)
- Zombies **rapides** (vitesse x1.3) et **resistants** (PV x1.5)
- Vagues toutes les **12 secondes** (enchainement rapide)
- Maximum **30 zombies** par vague (ecran vite submerge)
- Les zombies sont **armes des la vague 3** (50% de chance d'avoir un lance-flamme)
- IA des zombies : **A* + GoalStrategy** (meme intelligence, mais beaucoup plus rapides et dangereux)

### Mode Impossible (Apprentissage par Renforcement)

Le mode ultime : les zombies apprennent a vous traquer grace au **Q-Learning**.

- **60 PV** pour le robot (la moindre erreur est fatale)
- Zombies **tres rapides** (vitesse x1.5) et **tres resistants** (PV x2.0)
- Vagues toutes les **10 secondes** (aucun repit)
- Maximum **35 zombies** par vague
- Les zombies sont **armes des la vague 2** (60% de chance d'avoir un lance-flamme)
- IA des zombies : **A* + Q-Learning** (algorithme de reinforcement learning)
  - Les zombies partagent un **agent RL commun** (Q-table 64 etats x 8 actions)
  - Ils apprennent **en temps reel** pendant la partie : quelles directions mener au joueur, comment eviter les murs
  - L'apprentissage **persiste entre les parties** : quand vous relancez en mode Impossible, les zombies reprennent la ou ils en etaient
  - Un **pre-entrainement** de 3000 episodes est effectue au premier lancement (~5 secondes)

### Mode Auto-Play (Robot RL)

Active avec la touche **[TAB]** sur l'ecran de selection de difficulte. Le robot joue tout seul.

- Le robot est controle par un **agent Q-Learning** (1152 etats x 36 actions)
- Il apprend **tout par lui-meme** : deplacement (8 directions), choix d'arme (4 armes), evitement des murs (via Lidar)
- La visee est automatique (toujours vers le zombie le plus proche)
- Le tir est automatique
- L'agent est **pre-entraine** au premier lancement et **sauvegarde sur disque** apres chaque partie
- Combinable avec n'importe quel niveau de difficulte
- Plus il joue, plus il devient performant

### Strategie

- Utilisez les murs et bunkers comme couverture
- Le fusil a pompe est ideal contre les groupes rapproches
- Le laser permet des tirs de precision a longue distance
- Le lance-flamme est parfait pour les combats rapproches
- Anticipez les vagues : les zombies contournent les obstacles avec A*
- En mode Impossible, les zombies deviennent plus malins au fil du temps

---

## Installation

**Prerequis** : [uv](https://docs.astral.sh/uv/) (gestionnaire de paquets Python)

```bash
https://github.com/houssemmakni/ROS-Houssem-Briac# Installer uv (si pas deja fait)
curl -LsSf https://astral.sh/uv/install.sh | sh   # Linux/Mac
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Cloner le depot
git clone https://github.com/<VOTRE_USERNAME>/Robotique-ROS-V2.git
cd "Robotique ROS V2"

# Installer le projet (cree le venv + installe les dependances automatiquement)
uv sync
```

`uv sync` fait tout en une commande : cree le `.venv`, installe Python 3.11, installe pygame et numpy aux versions exactes du `uv.lock`. Zero configuration manuelle.

---

## Lancement

```bash
# Lancement standard
uv run python main.py

# Ou via le script installe
uv run robot-zombie

# Ou via le module Python
uv run python -m robot

# Avec le moteur differentiel (au lieu d'omnidirectionnel)
uv run python main.py --moteur differentiel

# Avec les logs de debug
uv run python main.py --debug
```

### Arguments en ligne de commande (argparse)

| Argument     | Type  | Defaut   | Choix                      | Description                   |
| ------------ | ----- | -------- | -------------------------- | ----------------------------- |
| `--moteur` | str   | `omni` | `differentiel`, `omni` | Type de moteur du robot       |
| `--debug`  | flag  | False    |                            | Active les logs niveau DEBUG  |
| `--dt`     | float | auto     |                            | Pas de temps de la simulation |

Les logs sont ecrits dans le terminal et dans le fichier `robot.log`.

---

## Controles

| Touche            | Action                   |
| ----------------- | ------------------------ |
| Z / Fleche Haut   | Avancer                  |
| S / Fleche Bas    | Reculer                  |
| Q / Fleche Gauche | Aller a gauche           |
| D / Fleche Droite | Aller a droite           |
| Souris            | Viser                    |
| Clic gauche       | Tirer (maintenir = auto) |
| 1                 | Fusil                    |
| 2                 | Fusil a pompe            |
| 3                 | Laser                    |
| 4                 | Lance-flamme             |
| Espace            | Demarrer (ecran titre)   |
| R                 | Recommencer (game over)  |
| Echap             | Quitter                  |

---

## Architecture du projet

Le projet suit l'architecture **MVC** avec un fichier par classe :

```
Robotique ROS V2/
|-- .venv/                          # Environnement virtuel
|-- .gitignore
|-- pyproject.toml                  # Packaging Python (pip install .)
|-- main.py                         # Point d'entree
|-- robot.log                       # Fichier de logs
|-- DOCS/                           # PDFs du cours
|-- src/
    |-- robot/
        |-- __init__.py
        |-- __main__.py             # Entree module (argparse + logging)
        |-- game.py                 # Boucle principale MVC
        |-- logging_config.py       # Configuration des logs
        |
        |-- models/                 # === MODELE ===
        |   |-- __init__.py
        |   |-- robot_mobile.py         -> RobotMobile
        |   |-- moteur.py               -> Moteur (ABC)
        |   |-- moteur_differentiel.py  -> MoteurDifferentiel
        |   |-- moteur_omnidirectionnel.py -> MoteurOmnidirectionnel
        |   |-- moteur_differentiel_realiste.py -> MoteurDifferentielRealiste
        |   |-- environnement.py        -> Environnement
        |   |-- obstacle.py             -> Obstacle (ABC)
        |   |-- obstacle_rectangle.py   -> ObstacleRectangle
        |   |-- obstacle_circulaire.py  -> ObstacleCirculaire
        |   |-- capteur.py              -> Capteur (ABC)
        |   |-- lidar.py                -> Lidar
        |   |-- arme.py                 -> Arme (ABC)
        |   |-- fusil.py                -> Fusil
        |   |-- fusil_a_pompe.py        -> FusilAPompe
        |   |-- laser.py                -> Laser
        |   |-- lance_flamme.py         -> LanceFlamme
        |   |-- projectile.py           -> Projectile
        |   |-- zombie.py               -> Zombie
        |   |-- wave_manager.py         -> WaveManager
        |   |-- grille_occupation.py    -> GrilleOccupation
        |   |-- cartographe.py          -> Cartographe
        |   |-- planificateur_astar.py  -> PlanificateurAStar
        |
        |-- views/                  # === VUE ===
        |   |-- __init__.py
        |   |-- vue_pygame.py           -> VuePygame
        |   |-- vue_terminal.py         -> VueTerminal
        |
        |-- controllers/            # === CONTROLEUR ===
            |-- __init__.py
            |-- controleur.py           -> Controleur (ABC)
            |-- controleur_terminal.py  -> ControleurTerminal
            |-- controleur_clavier_pygame.py -> ControleurClavierPygame
            |-- controleur_pid.py       -> ControleurPID
            |-- strategy.py             -> Strategy (ABC)
            |-- avoid_strategy.py       -> AvoidStrategy
            |-- free_direction_strategy.py -> FreeDirectionStrategy
            |-- goal_strategy.py        -> GoalStrategy
            |-- navigator.py            -> Navigator
```

**37 fichiers Python**, chacun contenant **une seule classe**.

---

## Diagramme de classes

```
                            +-------------+
                            |   Game      |
                            | (MVC loop)  |
                            +------+------+
                                   |
              +--------------------+--------------------+
              |                    |                     |
      CONTROLEUR              MODELE                   VUE
              |                    |                     |
    +---------+--------+    +------+------+     +-------+-------+
    |                  |    |             |     |               |
 Controleur(ABC)   Navigator  RobotMobile   VuePygame     VueTerminal
    |                  |        |
    +------+------+    |     Moteur(ABC)
    |      |      |  Strategy(ABC)  |
  Terminal Clavier PID  |      +--------+--------+
                        |      |        |        |
                   +----+----+ Diff   Omni   DiffRealiste
                   |    |    |
                 Avoid Free Goal

  Environnement ----+---- Obstacle(ABC)
       |            |         |
     Robot       Zombies   +--+--+
     Lidar       Projectiles Rect Circ
     Armes
                 GrilleOccupation <--- Cartographe
                        |
                 PlanificateurAStar

  Arme(ABC)          Capteur(ABC)
    |                    |
  +-+--+--+--+        Lidar
  |    |  |  |
 Fusil Pompe Laser LanceFlamme
```

---

## Detail des classes

### Models (Modele)

#### RobotMobile (`models/robot_mobile.py`)

Le robot joueur. Stocke l'etat (position, orientation, PV) et delegue le mouvement a son moteur par **composition**.

| Attribut (prive)       | Type   | Description                      |
| ---------------------- | ------ | -------------------------------- |
| `__x`, `__y`       | float  | Position en metres               |
| `__orientation`      | float  | Angle en radians                 |
| `__rayon`            | float  | Rayon de collision (0.3m)        |
| `__pv`, `__pv_max` | int    | Points de vie (100)              |
| `__moteur`           | Moteur | Moteur du robot (composition)    |
| `__capteurs`         | list   | Liste des capteurs               |
| `__invincible_timer` | float  | Cooldown anti-spam degats (0.3s) |

Methodes principales : `commander(**kwargs)`, `mettre_a_jour(dt)`, `subir_degat(degats)`, `sauvegarder_etat()`, `restaurer_etat(etat)`

Attribut statique : `_nb_robots` -- compte toutes les instances creees.

#### Moteur (`models/moteur.py`) -- ABC

Classe abstraite pour tous les moteurs. Definit l'interface `commander()` et `mettre_a_jour(robot, dt)`.

#### MoteurDifferentiel (`models/moteur_differentiel.py`)

Commande par vitesse lineaire `v` et angulaire `omega`. Cinematique :

- `theta += omega * dt`
- `x += v * cos(theta) * dt`
- `y += v * sin(theta) * dt`

#### MoteurOmnidirectionnel (`models/moteur_omnidirectionnel.py`)

Commande par `vx`, `vy` (repere robot) et `omega`. Cinematique :

- `x += (vx*cos(theta) - vy*sin(theta)) * dt`
- `y += (vx*sin(theta) + vy*cos(theta)) * dt`

#### MoteurDifferentielRealiste (`models/moteur_differentiel_realiste.py`)

Moteur physiquement realiste avec 4 etapes :

1. **Limitation d'acceleration** : `dv = clip(v_cmd - v_reel, -a_max*dt, a_max*dt)`
2. **Frottements** : `v *= (1 - lambda * dt)`
3. **Saturation** : `|v| <= v_max`
4. **Bruit** : `v += uniform(-sigma, sigma)`

#### Environnement (`models/environnement.py`)

Gestionnaire central de la simulation. Contient le robot, les obstacles, les zombies et les projectiles. Gere les collisions et la validation des mouvements. Principe : le robot calcule son mouvement, l'environnement decide si c'est valide.

#### Obstacle (`models/obstacle.py`) -- ABC

Interface commune : `collision(x, y, rayon)`, `intersection_rayon(ox, oy, dx, dy, max_range)`, `get_rect()`.

#### ObstacleRectangle (`models/obstacle_rectangle.py`)

Intersection rayon : algorithme par intervalles (slabs). Collision : point le plus proche du cercle sur le rectangle.

#### ObstacleCirculaire (`models/obstacle_circulaire.py`)

Intersection rayon : resolution de l'equation quadratique `at^2 + bt + c = 0`. Collision : `distance(centres) <= r1 + r2`.

#### Capteur (`models/capteur.py`) -- ABC

Interface commune pour tous les capteurs : `lire(env)`, `dessiner(screen, convertir)`.

#### Lidar (`models/lidar.py`)

Capteur de distance simule. Envoie `nb_rayons` rayons (36 par defaut) sur 360 degres et mesure la distance au premier obstacle. Utilise `intersection_rayon()` de chaque obstacle (polymorphisme).

#### Arme (`models/arme.py`) -- ABC

Classe abstraite pour les armes. Gere les munitions, la cadence de tir, et la regeneration automatique.

| Arme          | Fichier              | Degats | Cadence    | Munitions | Portee | Particularite              |
| ------------- | -------------------- | ------ | ---------- | --------- | ------ | -------------------------- |
| Fusil         | `fusil.py`         | 25     | 4 tirs/s   | 30        | 12m    | Tir unique precis          |
| Fusil a Pompe | `fusil_a_pompe.py` | 15     | 1.2 tirs/s | 16        | 5m     | 5 projectiles en eventail  |
| Laser         | `laser.py`         | 35     | 2.5 tirs/s | 20        | 15m    | Tres rapide, longue portee |
| Lance-Flamme  | `lance_flamme.py`  | 8      | 10 tirs/s  | 100       | 3m     | 3 particules par tir       |

#### Projectile (`models/projectile.py`)

Un projectile se deplacant en ligne droite. Attributs : position, angle, vitesse, degats, portee max, proprietaire (joueur ou ennemi), couleur, taille.

#### Zombie (`models/zombie.py`)

Ennemi intelligent utilisant :

- **A*** pour trouver un chemin autour des obstacles (recalcul toutes les 1s)
- **GoalStrategy** (Strategy Pattern) pour la navigation reactive
- Un **mini-lidar** (8 rayons, portee 2m) pour l'evitement local
- **Look-ahead** : vise quelques waypoints plus loin pour des mouvements fluides
- Peut tirer avec un lance-flamme a partir de la vague 5

#### WaveManager (`models/wave_manager.py`)

Gere la progression des vagues. Nombre de zombies par vague : `min(3 + vague*2, 25)`. Les zombies gagnent en vitesse et en PV a chaque vague. Spawn sur les bords de la map, a distance du joueur.

#### GrilleOccupation (`models/grille_occupation.py`)

Grille 2D pour la cartographie. Chaque cellule a un etat :

- `-1` : Inconnu
- `0` : Libre
- `1` : Occupe

Methodes : `coord2index(x, y)`, `index2coord(ix, iy)`, `get_cellule(ix, iy)`, `set_cellule(ix, iy, etat)`.

#### Cartographe (`models/cartographe.py`)

Met a jour la GrilleOccupation a partir des rayons du Lidar via l'**algorithme de Bresenham** : trace une ligne cellule par cellule, marque les cellules traversees comme LIBRE et le point d'impact comme OCCUPE.

#### PlanificateurAStar (`models/planificateur_astar.py`)

Algorithme **A*** sur la grille d'occupation. Utilise `heapq` (file de priorite). Heuristique euclidienne. Explore 8 directions (cardinales + diagonales). Retourne un chemin en coordonnees metriques.

---

### Views (Vue)

#### VuePygame (`views/vue_pygame.py`)

Rendu graphique temps reel avec Pygame (1000x750 pixels, echelle 50px/m). Affiche :

- La map avec grille, obstacles, bordures
- Le robot avec indicateur de direction (souris)
- Les zombies avec barres de PV et yeux rouges
- Les projectiles (balles, flammes avec particules)
- Le HUD : barre de PV, vague, score, arme, munitions
- Le selecteur d'armes en bas
- La **minimap** (grille d'occupation) en bas a droite avec positions du robot (bleu) et des zombies (rouge)
- Les ecrans titre et game over

#### VueTerminal (`views/vue_terminal.py`)

Affichage texte simple pour le debug : position et orientation du robot.

---

### Controllers (Controleur)

#### Controleur (`controllers/controleur.py`) -- ABC

Interface commune : `lire_commande()` retourne un dictionnaire de commandes.

#### ControleurClavierPygame (`controllers/controleur_clavier_pygame.py`)

Gere les entrees clavier (ZQSD + fleches) et souris (visee + tir). Normalise les diagonales. Expose des proprietes pour les actions (tir, changement d'arme, quitter, restart).

#### ControleurTerminal (`controllers/controleur_terminal.py`)

Entree texte : l'utilisateur tape `v omega` dans le terminal.

#### ControleurPID (`controllers/controleur_pid.py`)

Controleur proportionnel pour le suivi de chemin A*. Formules :

- `v = Kp_lin * distance`
- `omega = Kp_ang * e_theta`
- `e_theta = atan2(dy, dx) - theta`, normalise dans `[-pi, pi]`

#### Strategy (`controllers/strategy.py`) -- ABC

Interface du Design Pattern Strategy : `compute_command(observation)`.

#### AvoidStrategy (`controllers/avoid_strategy.py`)

Evitement simple : si obstacle proche devant, tourner. Sinon, avancer.

#### FreeDirectionStrategy (`controllers/free_direction_strategy.py`)

Evitement directionnel : compare la moyenne des distances gauche/droite du lidar et tourne vers le cote le plus libre.

#### GoalStrategy (`controllers/goal_strategy.py`)

Navigation vers un objectif avec evitement. Combine :

- **Attraction** vers la cible (proportionnelle a la distance)
- **Repulsion** des obstacles (inversement proportionnelle a la distance lidar)

#### Navigator (`controllers/navigator.py`)

Context du Design Pattern Strategy. Delegue la decision a la strategie courante. Permet de changer de strategie dynamiquement avec `set_strategy()`.

---

## Design Patterns utilises

| Pattern                    | Localisation                                           | Utilisation                                  |
| -------------------------- | ------------------------------------------------------ | -------------------------------------------- |
| **MVC**              | `models/`, `views/`, `controllers/`, `game.py` | Separation Modele-Vue-Controleur             |
| **Strategy**         | `Strategy`, `Navigator`, `AvoidStrategy`, etc.   | Comportements de navigation interchangeables |
| **Abstract Factory** | `Moteur(ABC)`, `Obstacle(ABC)`, `Arme(ABC)`      | Interfaces communes, polymorphisme           |
| **Composition**      | Robot+Moteur, Cartographe+Grille, Navigator+Strategy   | Delegation de responsabilite                 |
| **Polymorphisme**    | `Moteur.mettre_a_jour()`, `Obstacle.collision()`   | Meme interface, comportements differents     |

---

## Formules mathematiques

### Cinematique differentielle

```
theta(k+1) = theta(k) + omega * dt
x(k+1)     = x(k) + v * cos(theta) * dt
y(k+1)     = y(k) + v * sin(theta) * dt
```

### Cinematique omnidirectionnelle

```
x(k+1) = x(k) + (vx*cos(theta) - vy*sin(theta)) * dt
y(k+1) = y(k) + (vx*sin(theta) + vy*cos(theta)) * dt
```

### Moteur realiste

```
v(k+1)     = v(k) + clip(v_cmd - v(k), -a_max*dt, a_max*dt)   # acceleration
v(k+1)     = v(k+1) * (1 - lambda * dt)                        # frottements
v(k+1)     = clip(v(k+1), -v_max, v_max)                       # saturation
v(k+1)     = v(k+1) + uniform(-sigma, sigma)                   # bruit
```

### Intersection rayon-cercle

```
a = dx^2 + dy^2
b = 2*(fx*dx + fy*dy)
c = fx^2 + fy^2 - r^2
discriminant = b^2 - 4ac
t = (-b - sqrt(discriminant)) / (2a)
```

### Collision cercle-cercle

```
collision = distance(centre1, centre2) <= rayon1 + rayon2
```

### Controleur PID

```
distance     = sqrt(dx^2 + dy^2)
theta_desire = atan2(dy, dx)
e_theta      = normaliser(theta_desire - theta, [-pi, pi])
v            = Kp_lin * distance
omega        = Kp_ang * e_theta
```

### Algorithme de Bresenham

Trace une ligne de (x0,y0) a (x1,y1) cellule par cellule dans la grille en utilisant uniquement des operations entieres.

### Algorithme A*

Recherche du plus court chemin sur la grille avec file de priorite (`heapq`), cout reel `g` + heuristique euclidienne `h`, exploration 8 directions.

---

## Fonctionnalites implementees

| Fonctionnalite                      | TP source              | Status |
| ----------------------------------- | ---------------------- | ------ |
| Classe RobotMobile (POO)            | TP Prise en main       | OK     |
| Encapsulation (attributs prives)    | TP Prise en main       | OK     |
| Heritage et polymorphisme (Moteurs) | TP Prise en main       | OK     |
| Attributs/methodes statiques        | TP Prise en main       | OK     |
| Architecture MVC                    | TP MVC + Pygame        | OK     |
| Simulation Pygame (VuePygame)       | TP MVC + Pygame        | OK     |
| Controleur clavier Pygame           | TP MVC + Pygame        | OK     |
| Environnement + Obstacles           | TP MVC + Pygame        | OK     |
| Gestion des collisions              | TP MVC + Pygame        | OK     |
| Moteur differentiel realiste        | TP Simulation realiste | OK     |
| Capteur Lidar (lancer de rayons)    | TP Capteurs            | OK     |
| Packaging (pyproject.toml, pip)     | TP Packaging           | OK     |
| Arguments CLI (argparse)            | TP Arguments et Logs   | OK     |
| Logs (module logging)               | TP Arguments et Logs   | OK     |
| Navigation reactive (Strategy)      | TP Navigation reactive | OK     |
| Grille d'occupation                 | TP Cartographie        | OK     |
| Cartographe (Bresenham)             | TP Cartographie        | OK     |
| Planificateur A*                    | TP Navigation autonome | OK     |
| Controleur PID                      | TP Navigation autonome | OK     |
| Scenario zombie survival            | Projet fil rouge       | OK     |

---

## Dependances

| Bibliotheque | Version | Utilisation                                        |
| ------------ | ------- | -------------------------------------------------- |
| pygame       | >= 2.0  | Rendu graphique, gestion evenements, boucle de jeu |
| numpy        | >= 1.20 | Matrice de la grille d'occupation (cartographie)   |

---

## Membres du groupe

- Houssem MAKNI
- Briac Leclercq
