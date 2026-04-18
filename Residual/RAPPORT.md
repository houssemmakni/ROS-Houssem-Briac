# Rapport de Projet -- Robot Zombie Survival

## Simulation robotique mobile avec architecture MVC et Pygame

**Cours :** Programmation Orientee Objet a destination de la robotique  
**Enseignant :** Adam GOUGUET -- IMT Nord-Europe  
**Annee :** 2025-2026  
**Auteur :** Houssem MAKNI

---

## Table des matieres

1. [Introduction](#1-introduction)
2. [Cahier des charges](#2-cahier-des-charges)
3. [Architecture logicielle](#3-architecture-logicielle)
4. [Couche Modele](#4-couche-modele)
5. [Couche Vue](#5-couche-vue)
6. [Couche Controleur](#6-couche-controleur)
7. [Systeme de jeu](#7-systeme-de-jeu)
8. [Intelligence Artificielle des zombies](#8-intelligence-artificielle-des-zombies)
9. [Apprentissage par renforcement](#9-apprentissage-par-renforcement)
10. [Cartographie et navigation autonome](#10-cartographie-et-navigation-autonome)
11. [Formules mathematiques](#11-formules-mathematiques)
12. [Design Patterns utilises](#12-design-patterns-utilises)
13. [Packaging et configuration](#13-packaging-et-configuration)
14. [Bilan et perspectives](#14-bilan-et-perspectives)

---

## 1. Introduction

### 1.1 Contexte

Ce projet s'inscrit dans le cadre du cours de Programmation Orientee Objet appliquee a la robotique mobile. L'objectif est de concevoir une simulation robotique complete en Python, en mettant en oeuvre les principes fondamentaux de la POO : classes abstraites, heritage, polymorphisme, encapsulation et composition.

### 1.2 Scenario choisi

Le scenario retenu est un **jeu de survie zombie** : un robot mobile evolue dans une arene 2D et doit survivre a des vagues de zombies de plus en plus difficiles. Ce scenario permet d'integrer naturellement toutes les fonctionnalites demandees dans les TPs du cours (capteurs, navigation, cartographie, moteurs, obstacles, etc.) dans un contexte ludique et motivant.

### 1.3 Technologies

| Technologie | Version | Utilisation |
|---|---|---|
| Python | >= 3.9 | Langage principal |
| Pygame | >= 2.0 | Rendu graphique 2D, evenements |
| NumPy | >= 1.20 | Calcul matriciel (grille d'occupation) |

### 1.4 Metriques du projet

| Metrique | Valeur |
|---|---|
| Nombre de fichiers Python | 40 |
| Nombre de classes | 30 |
| Nombre total de lignes | ~3200 |
| Classes abstraites (ABC) | 6 |
| Design patterns | 5 |
| Niveaux de difficulte | 3 |

---

## 2. Cahier des charges

### 2.1 Fonctionnalites issues des TPs

Chaque TP du cours a ete integre dans le projet :

| TP | Fonctionnalite | Fichiers concernes |
|---|---|---|
| TP Prise en main POO | RobotMobile, Moteurs, heritage, encapsulation | `robot_mobile.py`, `moteur*.py` |
| TP MVC + Pygame | Architecture MVC, VuePygame, Controleurs | `game.py`, `vue_pygame.py`, `controleur*.py` |
| TP Simulation realiste | MoteurDifferentielRealiste (inertie, frottements, bruit) | `moteur_differentiel_realiste.py` |
| TP Capteurs | Capteur (ABC), Lidar (lancer de rayons) | `capteur.py`, `lidar.py` |
| TP Packaging | pyproject.toml, pip install, __main__.py | `pyproject.toml`, `__main__.py` |
| TP Arguments et Logs | argparse, module logging | `__main__.py`, `logging_config.py` |
| TP Navigation reactive | Strategy Pattern, Navigator, 3 strategies | `strategy.py`, `navigator.py`, `*_strategy.py` |
| TP Cartographie | GrilleOccupation, Cartographe (Bresenham) | `grille_occupation.py`, `cartographe.py` |
| TP Navigation autonome | A*, PID | `planificateur_astar.py`, `controleur_pid.py` |
| Cours (RL) | Apprentissage par renforcement (Q-learning) | `rl_agent.py`, `rl_strategy.py` |

### 2.2 Fonctionnalites specifiques au jeu

- Systeme d'armes (4 armes avec comportements differents)
- Systeme de vagues progressives (difficulte croissante)
- Barre de PV avec degats variables
- 3 niveaux de difficulte (Facile, Difficile, Impossible)
- Minimap en temps reel (grille d'occupation)
- IA des zombies (A* + Strategy Pattern + Q-learning)
- HUD complet (PV, score, vague, arme, munitions)

---

## 3. Architecture logicielle

### 3.1 Pattern MVC

Le projet respecte strictement le pattern Modele-Vue-Controleur :

```
Controleur (entrees utilisateur)
    |
    v
Modele (logique metier, physique, IA)
    |
    v
Vue (affichage Pygame)
```

- **Modele** : Ne connait ni l'affichage ni les entrees utilisateur. Contient toute la logique : robot, moteur, environnement, zombies, armes, cartographie, pathfinding.
- **Vue** : Ne modifie jamais l'etat du jeu. Se contente de lire les donnees et de les afficher.
- **Controleur** : Ne calcule pas le mouvement du robot. Genere uniquement des commandes a partir des entrees.

### 3.2 Principe "un fichier = une classe"

Chaque fichier Python contient exactement une classe, ce qui garantit :
- Une responsabilite unique par fichier
- Une navigation simple dans le code
- Une maintenance facilitee

### 3.3 Arborescence complete

```
src/robot/
|-- __init__.py
|-- __main__.py                          # Point d'entree (argparse)
|-- game.py                              # Boucle MVC principale
|-- logging_config.py                    # Configuration des logs
|
|-- models/                              # ========== MODELE ==========
|   |-- robot_mobile.py                      -> RobotMobile
|   |-- moteur.py                            -> Moteur (ABC)
|   |-- moteur_differentiel.py               -> MoteurDifferentiel
|   |-- moteur_omnidirectionnel.py           -> MoteurOmnidirectionnel
|   |-- moteur_differentiel_realiste.py      -> MoteurDifferentielRealiste
|   |-- environnement.py                     -> Environnement
|   |-- obstacle.py                          -> Obstacle (ABC)
|   |-- obstacle_rectangle.py                -> ObstacleRectangle
|   |-- obstacle_circulaire.py               -> ObstacleCirculaire
|   |-- capteur.py                           -> Capteur (ABC)
|   |-- lidar.py                             -> Lidar
|   |-- arme.py                              -> Arme (ABC)
|   |-- fusil.py                             -> Fusil
|   |-- fusil_a_pompe.py                     -> FusilAPompe
|   |-- laser.py                             -> Laser
|   |-- lance_flamme.py                      -> LanceFlamme
|   |-- projectile.py                        -> Projectile
|   |-- zombie.py                            -> Zombie
|   |-- wave_manager.py                      -> WaveManager
|   |-- grille_occupation.py                 -> GrilleOccupation
|   |-- cartographe.py                       -> Cartographe
|   |-- planificateur_astar.py               -> PlanificateurAStar
|   |-- difficulte.py                        -> Difficulte
|   |-- rl_agent.py                          -> RLAgent
|
|-- views/                               # ========== VUE ==========
|   |-- vue_pygame.py                        -> VuePygame
|   |-- vue_terminal.py                      -> VueTerminal
|
|-- controllers/                         # ========== CONTROLEUR ==========
    |-- controleur.py                        -> Controleur (ABC)
    |-- controleur_terminal.py               -> ControleurTerminal
    |-- controleur_clavier_pygame.py         -> ControleurClavierPygame
    |-- controleur_pid.py                    -> ControleurPID
    |-- strategy.py                          -> Strategy (ABC)
    |-- avoid_strategy.py                    -> AvoidStrategy
    |-- free_direction_strategy.py           -> FreeDirectionStrategy
    |-- goal_strategy.py                     -> GoalStrategy
    |-- navigator.py                         -> Navigator
    |-- rl_strategy.py                       -> RLStrategy
```

---

## 4. Couche Modele

### 4.1 RobotMobile

Le robot est l'entite centrale du jeu. Il stocke son etat et delegue le mouvement a son moteur par **composition** (le robot possede un moteur, mais ne depend pas de son type concret).

**Encapsulation :** Tous les attributs sont prives (`__x`, `__y`, `__pv`, etc.) et accessibles via des `@property` et `@setter`. Cela empeche toute modification directe depuis l'exterieur et centralise la logique de validation.

**Attribut statique :** `_nb_robots` compte toutes les instances creees (attribut de classe, pas d'instance).

```python
class RobotMobile:
    _nb_robots = 0  # attribut statique

    def __init__(self, x=0.0, y=0.0, orientation=0.0, rayon=0.3, moteur=None, pv_max=100):
        RobotMobile._nb_robots += 1
        self.__x = x           # prive
        self.__pv = pv_max     # prive
        self.__moteur = moteur # composition
```

### 4.2 Systeme de moteurs (heritage + polymorphisme)

La classe abstraite `Moteur` definit l'interface commune. Trois implementations concretes heritent de cette classe :

| Moteur | Commande | Cinematique |
|---|---|---|
| MoteurDifferentiel | v, omega | theta += omega*dt ; x += v*cos(theta)*dt |
| MoteurOmnidirectionnel | vx, vy, omega | x += (vx*cos - vy*sin)*dt |
| MoteurDifferentielRealiste | v, omega | + acceleration limitee, frottements, saturation, bruit |

Le robot appelle `self.__moteur.mettre_a_jour(self, dt)` sans connaitre le type concret du moteur. C'est le **polymorphisme** : le meme appel produit des comportements differents selon la sous-classe.

### 4.3 Environnement

L'environnement est le gestionnaire central de la simulation. Il contient le robot, les obstacles, les zombies et les projectiles. Il gere toutes les collisions.

**Principe fondamental :** Le robot calcule son mouvement, l'environnement decide si c'est valide. Si collision, le mouvement est annule (rollback via `sauvegarder_etat()` / `restaurer_etat()`).

```
Robot calcule -> Environnement valide -> Position acceptee ou refusee
```

### 4.4 Obstacles

La classe abstraite `Obstacle` definit trois methodes :
- `collision(x, y, rayon)` : test de collision avec un cercle
- `intersection_rayon(ox, oy, dx, dy, max_range)` : intersection avec un rayon (pour le Lidar)
- `get_rect()` : bounding box

Deux implementations :
- `ObstacleRectangle` : collision par point le plus proche, intersection par intervalles (slab method)
- `ObstacleCirculaire` : collision par distance entre centres, intersection par equation quadratique

L'environnement manipule des obstacles sans connaitre leur type concret (**polymorphisme**).

### 4.5 Capteur Lidar

Le Lidar simule un telemitre laser qui envoie 36 rayons sur 360 degres. Pour chaque rayon :
1. Calculer la direction du rayon a partir de l'orientation du robot
2. Tester l'intersection avec tous les obstacles (polymorphisme)
3. Conserver la plus petite distance trouvee

### 4.6 Systeme d'armes

La classe abstraite `Arme` gere les munitions, la cadence, et la regeneration automatique. Quatre implementations :

| Arme | Degats | Cadence | Munitions | Portee | Particularite |
|---|---|---|---|---|---|
| Fusil | 25 | 4/s | 30 | 12m | Tir unique precis |
| Fusil a Pompe | 15 | 1.2/s | 16 | 5m | 5 projectiles en eventail |
| Laser | 35 | 2.5/s | 20 | 15m | Tres rapide, longue portee |
| Lance-Flamme | 8 | 10/s | 100 | 3m | 3 particules de feu par tir |

### 4.7 Systeme de vagues (WaveManager)

Le `WaveManager` gere la progression des vagues :
- Nombre de zombies : `min(3 + vague * 2, max_config)`
- Vitesse : `(0.8 + vague * 0.1) * multiplicateur_difficulte`
- PV : `(30 + vague * 10) * multiplicateur_difficulte`
- Spawn sur les 4 bords de la map, a distance minimale de 3m du robot
- Score : `vague * 100 + zombies_tues * 10`

---

## 5. Couche Vue

### 5.1 VuePygame

La vue Pygame rend l'ensemble du jeu a 60 FPS dans une fenetre de 1000x750 pixels (echelle 50 px/m pour une map de 20m x 15m).

**Elements affiches :**
- Sol avec grille de reference
- Obstacles (rectangles et cercles avec contours)
- Robot joueur avec indicateur de direction (ligne vers la souris)
- Zombies avec yeux rouges orientes, barre de PV, couleur differente si arme
- Projectiles (balles colorees, particules de flamme)
- HUD : barre de PV (verte/jaune/rouge), vague, timer, score, arme, munitions
- Selecteur d'armes en bas (4 cartes avec touche, nom, munitions)
- Minimap (grille d'occupation) en bas a droite
- Indicateur de difficulte en haut a droite
- Stats RL en temps reel (mode Impossible)
- Ecrans : titre, selection de difficulte, game over

**Conversion de coordonnees :**
```
px = offset_x + x * scale      (metres -> pixels)
py = hauteur - offset_y - y * scale   (axe Y inverse)
```

### 5.2 VueTerminal

Vue texte simple pour le debug, affichant la position et l'orientation du robot dans le terminal.

---

## 6. Couche Controleur

### 6.1 Controleurs utilisateur

- **ControleurClavierPygame** : ZQSD/fleches pour le mouvement, souris pour viser et tirer, touches 1-4 pour les armes. Normalise les diagonales pour eviter une vitesse superieure en diagonal.
- **ControleurTerminal** : Entree texte pour le debug.

### 6.2 ControleurPID

Controleur proportionnel pour le suivi de chemin A*. A chaque iteration :
1. Selectionner le waypoint courant
2. Calculer l'erreur de position (distance) et d'orientation (angle)
3. `v = Kp_lin * distance`
4. `omega = Kp_ang * e_theta` (normalise dans [-pi, pi])
5. Si waypoint atteint (distance < tolerance), passer au suivant

### 6.3 Design Pattern Strategy

Le pattern Strategy encapsule des comportements de navigation interchangeables :

| Strategie | Comportement |
|---|---|
| AvoidStrategy | Obstacle devant ? Tourner. Sinon avancer. |
| FreeDirectionStrategy | Tourner vers le cote le plus libre (gauche vs droite) |
| GoalStrategy | Attraction vers cible + repulsion des obstacles |
| RLStrategy | Action choisie par Q-learning |

Le **Navigator** est le Context du pattern. Il delegue la decision a la strategie courante sans connaitre son type. On peut changer de strategie dynamiquement avec `set_strategy()`.

---

## 7. Systeme de jeu

### 7.1 Flux du jeu

```
Ecran titre -> [ESPACE] -> Selection difficulte -> [1/2/3] + [ESPACE] -> Jeu -> Game Over -> [R] -> Selection
```

### 7.2 Niveaux de difficulte

| Parametre | Facile | Difficile | Impossible (RL) |
|---|---|---|---|
| PV Robot | 150 | 80 | 60 |
| Vitesse zombies | x0.6 | x1.3 | x1.5 |
| PV zombies | x0.5 | x1.5 | x2.0 |
| Intervalle vagues | 20s | 12s | 10s |
| Max zombies/vague | 15 | 30 | 35 |
| Zombies armes | Jamais | Vague 3 | Vague 2 |
| IA Zombies | A* + GoalStrategy | A* + GoalStrategy | Q-Learning |

### 7.3 Barre de PV

Le robot a une barre de PV au lieu de vies discretes :
- Contact zombie : 5 degats
- Projectile ennemi : degats variables
- Cooldown d'invincibilite : 0.3s (anti-spam, mais permet de prendre des coups reguliers)
- Affichage : vert (>50%), jaune (25-50%), rouge (<25%)

### 7.4 Carte de la map

L'arene contient :
- 4 murs de couverture centraux (2.0 x 0.3m)
- 2 bunkers (3.0 x 1.0m)
- 5 piliers circulaires (rayon 0.5-0.6m)
- 8 murs de coins en L
- Dimensions : 20m x 15m

---

## 8. Intelligence Artificielle des zombies

### 8.1 Pipeline IA complet

Chaque zombie execute ce pipeline a chaque frame :

```
1. Calcul distance/angle vers le robot
2. Recalcul chemin A* (toutes les 1s)
3. Selection du waypoint look-ahead
4. Mini-lidar (8 rayons, 2m) pour detection locale
5. Strategie de navigation (GoalStrategy ou RLStrategy)
6. Deplacement avec evitement de collisions
7. Tir si arme (distance < 8m, cadence 1/s)
```

### 8.2 Pathfinding A*

L'algorithme A* planifie un chemin global sur la grille d'occupation :
- Heuristique euclidienne
- 8 directions (cardinales + diagonales)
- File de priorite (`heapq`)
- Recalcul toutes les 1 seconde
- Le zombie vise un waypoint en avance (look-ahead de 3 points) pour des mouvements fluides

### 8.3 Navigation reactive

En plus du chemin A*, chaque zombie a un mini-lidar (8 rayons, 2m de portee) qui alimente la GoalStrategy :
- **Attraction** : le zombie est attire vers la cible (robot ou waypoint A*)
- **Repulsion** : les obstacles proches repoussent le zombie
- Si le deplacement principal est bloque, le zombie essaie 6 angles alternatifs

---

## 9. Apprentissage par renforcement

### 9.1 Principe

En mode Impossible, les zombies utilisent un agent de **Q-learning** partage. Au lieu de suivre des regles codees, ils apprennent a traquer le robot par essai-erreur, comme decrit dans le cours (slide 11) :

```
Boucle d'apprentissage :
1. Observer l'etat
2. Choisir une action (politique epsilon-greedy)
3. Recevoir une recompense
4. Mettre a jour le modele (equation de Bellman)
Cycle repete a chaque frame -> comportement de plus en plus optimal
```

### 9.2 Espace d'etats

L'etat continu est discretise en 64 etats :

| Composante | Bins | Valeurs |
|---|---|---|
| Angle relatif vers le robot | 8 | N, NE, E, SE, S, SW, W, NW |
| Distance au robot | 4 | Contact (<1m), Proche (1-3m), Moyen (3-7m), Loin (>7m) |
| Obstacle devant | 2 | Libre, Bloque |
| **Total** | **64** | 8 x 4 x 2 |

### 9.3 Espace d'actions

8 directions de deplacement :

```
0: Est (0 rad)        4: Ouest (pi rad)
1: Nord-Est (pi/4)    5: Sud-Ouest (5pi/4)
2: Nord (pi/2)        6: Sud (3pi/2)
3: Nord-Ouest (3pi/4) 7: Sud-Est (7pi/4)
```

### 9.4 Q-Table

Matrice 64 x 8 initialisee a zero. Chaque cellule `Q(s, a)` represente la valeur estimee de prendre l'action `a` dans l'etat `s`.

### 9.5 Fonction de recompense

| Evenement | Recompense |
|---|---|
| Toucher le robot | +10 |
| Se rapprocher du robot | +1 |
| S'eloigner du robot | -1 |
| Collision avec un obstacle | -5 |
| Penalite par pas de temps | -0.1 |

### 9.6 Equation de Bellman

```
Q(s, a) = Q(s, a) + alpha * [R + gamma * max(Q(s', a')) - Q(s, a)]
```

Ou :
- `alpha = 0.15` : taux d'apprentissage
- `gamma = 0.9` : facteur de discount (importance du futur)
- `R` : recompense recue
- `s'` : etat suivant
- `max(Q(s', a'))` : meilleure valeur future estimee

### 9.7 Exploration vs Exploitation (epsilon-greedy)

- Debut : `epsilon = 0.5` (50% d'exploration aleatoire)
- Decroissance : `epsilon *= 0.9995` a chaque update
- Minimum : `epsilon = 0.05` (5% d'exploration toujours)

L'exploration permet de decouvrir de nouvelles strategies. L'exploitation utilise les connaissances acquises. L'epsilon decroit au fil du temps pour converger vers un comportement optimal.

### 9.8 Agent partage et persistance

L'agent RL est **partage entre tous les zombies** : quand un zombie apprend, tous les autres en beneficient (meme Q-table). De plus, l'agent **persiste entre les parties** : si le joueur meurt et relance en mode Impossible, les zombies reprennent la ou ils en etaient. Ils deviennent plus intelligents a chaque partie.

### 9.9 Affichage en temps reel

Le HUD affiche en haut a droite :
- Nombre de mises a jour de la Q-table
- Taux d'exploration actuel (epsilon)

---

## 10. Cartographie et navigation autonome

### 10.1 Grille d'occupation

La `GrilleOccupation` est une matrice 2D ou chaque cellule a un etat :
- `-1` : Inconnu (pas encore explore)
- `0` : Libre (le rayon lidar est passe sans toucher d'obstacle)
- `1` : Occupe (le rayon lidar a touche un obstacle)

Resolution : 0.4m par cellule, soit une grille de 50 x 37 cellules pour la map de 20m x 15m.

### 10.2 Algorithme de Bresenham

Le `Cartographe` utilise l'algorithme de Bresenham pour tracer les rayons du Lidar dans la grille :
1. Pour chaque rayon du Lidar, convertir les points de depart et d'arrivee en indices de grille
2. Tracer la ligne cellule par cellule (operations entieres uniquement)
3. Marquer chaque cellule traversee comme LIBRE
4. Si le rayon a touche un obstacle, marquer la cellule finale comme OCCUPE

### 10.3 Minimap

La grille d'occupation est affichee en temps reel sous forme de minimap en bas a droite de l'ecran :
- Vert fonce : cellule libre
- Gris clair : cellule occupee (mur/obstacle)
- Point bleu : position du robot
- Points rouges : positions des zombies
- Fond noir : cellules inconnues

---

## 11. Formules mathematiques

### 11.1 Cinematique differentielle

```
theta(k+1) = theta(k) + omega * dt
x(k+1)     = x(k) + v * cos(theta(k)) * dt
y(k+1)     = y(k) + v * sin(theta(k)) * dt
```

### 11.2 Cinematique omnidirectionnelle

```
theta(k+1) = theta(k) + omega * dt
x(k+1)     = x(k) + (vx * cos(theta) - vy * sin(theta)) * dt
y(k+1)     = y(k) + (vx * sin(theta) + vy * cos(theta)) * dt
```

### 11.3 Moteur realiste

```
Acceleration : v += clip(v_cmd - v, -a_max*dt, a_max*dt)
Frottements  : v *= (1 - lambda * dt)
Saturation   : v  = clip(v, -v_max, v_max)
Bruit        : v += uniform(-sigma, sigma)
```

### 11.4 Intersection rayon-cercle

```
f = (ox - cx, oy - cy)
a = dx^2 + dy^2
b = 2 * (fx*dx + fy*dy)
c = fx^2 + fy^2 - r^2
discriminant = b^2 - 4ac
t = (-b - sqrt(discriminant)) / (2a)
```

### 11.5 Collision cercle-cercle

```
collision = sqrt((x1-x2)^2 + (y1-y2)^2) <= r1 + r2
```

### 11.6 Controleur PID

```
distance   = sqrt(dx^2 + dy^2)
theta_des  = atan2(dy, dx)
e_theta    = normaliser(theta_des - theta, [-pi, pi])
v          = Kp_lin * distance
omega      = Kp_ang * e_theta
```

### 11.7 Q-learning (Bellman)

```
Q(s,a) <- Q(s,a) + alpha * [R + gamma * max_a'(Q(s',a')) - Q(s,a)]
```

---

## 12. Design Patterns utilises

### 12.1 MVC (Modele-Vue-Controleur)

Separation stricte entre les donnees (models/), l'affichage (views/) et les entrees (controllers/). La classe `Game` orchestre les trois couches.

### 12.2 Strategy

Le pattern Strategy permet d'encapsuler des comportements de navigation interchangeables (AvoidStrategy, GoalStrategy, RLStrategy) dans des classes separees. Le Navigator utilise une strategie sans connaitre son type concret. On peut changer de strategie en une ligne.

### 12.3 Classe abstraite (ABC)

6 classes abstraites definissent les interfaces communes : Moteur, Obstacle, Capteur, Arme, Controleur, Strategy. Elles empechent l'instanciation directe et forcent les sous-classes a implementer les methodes requises.

### 12.4 Composition

Le robot possede un moteur et des capteurs, mais ne depend pas de leur type concret. Le Cartographe possede une GrilleOccupation. Le Navigator possede une Strategy. Cette approche permet de changer les composants sans modifier les classes qui les utilisent.

### 12.5 Polymorphisme

Le meme appel `obstacle.collision(x, y, r)` produit un calcul different selon qu'il s'agit d'un rectangle ou d'un cercle. Le meme appel `moteur.mettre_a_jour(robot, dt)` produit un mouvement differentiel ou omnidirectionnel.

---

## 13. Packaging et configuration

### 13.1 pyproject.toml

Le projet est installable via `pip install -e .` :
```toml
[project]
name = "robot-zombie-survival"
version = "1.0.0"
dependencies = ["pygame>=2.0", "numpy>=1.20"]

[project.scripts]
robot-zombie = "robot.__main__:main"
```

### 13.2 Arguments CLI (argparse)

```bash
python -m robot                          # mode par defaut
python -m robot --moteur differentiel    # moteur differentiel
python -m robot --debug                  # logs de debug
```

### 13.3 Logging

Le module `logging` remplace tous les `print()`. Les logs sont ecrits dans le terminal et dans `robot.log`. Format : `[date] NIVEAU module : message`.

---

## 14. Bilan et perspectives

### 14.1 Bilan

Le projet integre toutes les fonctionnalites demandees dans les TPs du cours, organisees dans une architecture MVC propre avec 40 fichiers Python et 30 classes. Le scenario de jeu zombie permet de mettre en valeur les concepts de la POO (heritage, polymorphisme, encapsulation, composition) et de la robotique mobile (cinematique, capteurs, navigation, cartographie).

Le mode Impossible avec apprentissage par renforcement constitue la fonctionnalite avancee du projet : les zombies apprennent en temps reel a traquer le robot, devenant plus efficaces au fil des parties.

### 14.2 Perspectives d'amelioration

- **Deep Q-Network (DQN)** : Remplacer la Q-table par un reseau de neurones (PyTorch) pour un espace d'etats continu
- **Multi-agent RL** : Chaque zombie apprend independamment au lieu de partager une Q-table
- **Carte dynamique** : Obstacles destructibles ou mobiles
- **Mode multijoueur** : Cooperation entre plusieurs robots
- **Sonorisation** : Effets sonores Pygame pour les tirs, explosions, vagues
