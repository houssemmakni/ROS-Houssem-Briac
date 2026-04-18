# Robot Zombie Survival -- Presentation

> Ce document est formate pour etre importe dans **Gamma** (gamma.app) afin de generer une presentation.
> Chaque section `## Slide` correspond a un slide.

---

## Slide 1 -- Titre

# Robot Zombie Survival

### Simulation robotique mobile avec POO et Pygame

**Houssem MAKNI**

Cours : Programmation Orientee Objet a destination de la robotique
Enseignant : Adam GOUGUET -- IMT Nord-Europe
Annee 2025-2026

---

## Slide 2 -- Le Projet

### Scenario : Survie Zombie

Un robot mobile dans une arene 2D doit survivre a des vagues de zombies de plus en plus difficiles.

**Pourquoi ce scenario ?**
- Integre naturellement TOUS les TPs du cours
- Capteurs, navigation, cartographie, moteurs, obstacles
- Fun a developper et a presenter

**Chiffres cles :**
- 40 fichiers Python
- 30 classes
- ~3200 lignes de code
- 3 niveaux de difficulte

---

## Slide 3 -- Architecture MVC

### Modele - Vue - Controleur

Le coeur du projet : une separation stricte des responsabilites.

**Controleur** (entrees)
- Clavier ZQSD + fleches
- Souris (visee, tir)
- Touches 1-4 (armes)

**Modele** (logique)
- Robot, Zombies, Physique
- Collisions, Armes, Capteurs
- IA, Pathfinding, Cartographie

**Vue** (affichage)
- Pygame 1000x750
- HUD, Minimap
- Ecrans de menu

> Un fichier = Une classe. 40 fichiers, 0 ambiguite.

---

## Slide 4 -- Structure du projet

### Organisation en dossiers MVC

```
src/robot/
|-- models/        (24 fichiers)
|   Robot, Moteurs, Obstacles,
|   Capteurs, Armes, Zombies,
|   Cartographie, Pathfinding, RL
|
|-- views/         (2 fichiers)
|   VuePygame, VueTerminal
|
|-- controllers/   (10 fichiers)
|   Clavier, Terminal, PID,
|   Strategy, Navigator, RL
|
|-- game.py        (boucle MVC)
|-- __main__.py    (argparse + logs)
```

---

## Slide 5 -- Concepts POO

### 6 principes fondamentaux appliques

**1. Classes abstraites (ABC)**
Moteur, Obstacle, Capteur, Arme, Controleur, Strategy
-> Impossible a instancier, force l'implementation

**2. Heritage**
MoteurDifferentiel herite de Moteur
ObstacleRectangle herite de Obstacle

**3. Polymorphisme**
`obstacle.collision()` -> calcul different selon Rectangle ou Cercle
`moteur.mettre_a_jour()` -> cinematique differente selon le type

**4. Encapsulation**
Attributs `__prives` + `@property` getters/setters

**5. Composition**
Robot possede un Moteur (pas heritage, mais "a un")

**6. Attributs statiques**
`RobotMobile._nb_robots` compte toutes les instances

---

## Slide 6 -- Les Moteurs

### 3 types de moteurs (polymorphisme)

**Differentiel** (2 roues)
```
theta += omega * dt
x += v * cos(theta) * dt
y += v * sin(theta) * dt
```

**Omnidirectionnel** (mecanum)
```
x += (vx*cos(theta) - vy*sin(theta)) * dt
y += (vx*sin(theta) + vy*cos(theta)) * dt
```

**Differentiel Realiste**
- Acceleration limitee (clip)
- Frottements (v *= 1 - lambda*dt)
- Saturation (|v| <= v_max)
- Bruit aleatoire (uniform)

> Le robot ne connait pas son type de moteur. C'est le polymorphisme.

---

## Slide 7 -- Capteur Lidar

### Lancer de rayons

Le Lidar envoie 36 rayons sur 360 degres et mesure la distance au premier obstacle.

**Algorithme :**
1. Pour chaque rayon : calculer la direction
2. Pour chaque obstacle : calculer l'intersection
3. Garder la plus petite distance

**Intersections :**
- Cercle : equation quadratique (discriminant)
- Rectangle : methode des intervalles (slabs)

> Le Lidar ne connait pas le type des obstacles. Polymorphisme !

---

## Slide 8 -- Systeme d'armes

### 4 armes, 4 comportements differents

| Arme | Degats | Cadence | Portee | Specialite |
|---|---|---|---|---|
| Fusil | 25 | 4/s | 12m | Tir precis |
| Fusil a Pompe | 15 | 1.2/s | 5m | 5 projectiles en eventail |
| Laser | 35 | 2.5/s | 15m | Ultra rapide |
| Lance-Flamme | 8 | 10/s | 3m | Particules de feu |

**Classe abstraite Arme :**
- `peut_tirer()` : verifie cooldown + munitions
- `regenerer(dt)` : +1 munition toutes les 0.8s
- `tirer(x, y, angle)` : cree des Projectiles (abstraite)

---

## Slide 9 -- Cartographie

### Grille d'occupation + Bresenham

**GrilleOccupation :** Matrice 50x37 cellules
- -1 = Inconnu
- 0 = Libre
- 1 = Occupe

**Cartographe :** A chaque frame :
1. Lire les rayons du Lidar
2. Tracer chaque rayon dans la grille (Bresenham)
3. Cellules traversees = LIBRE
4. Point d'impact = OCCUPE

> Affiche en temps reel sur la minimap (bas droite de l'ecran)

---

## Slide 10 -- Navigation A*

### Pathfinding global

L'algorithme A* trouve le chemin le plus court sur la grille :

1. File de priorite (heapq)
2. Cout reel g + heuristique euclidienne h
3. 8 directions (cardinales + diagonales)
4. Retourne une liste de waypoints en metres

**Utilisation :** Les zombies recalculent leur chemin A* toutes les secondes pour contourner les obstacles intelligemment.

**Controleur PID :** Suit le chemin point par point
```
v     = Kp_lin * distance
omega = Kp_ang * (theta_desire - theta)
```

---

## Slide 11 -- Design Pattern Strategy

### Navigation reactive interchangeable

**Le probleme :** On veut tester plusieurs comportements (eviter, contourner, foncer) sans if/elif/else.

**La solution :** Pattern Strategy

```
Strategy (abstraite)
  |-- AvoidStrategy    : obstacle ? tourner
  |-- FreeDirection    : tourner vers le plus libre
  |-- GoalStrategy     : attraction + repulsion
  |-- RLStrategy       : Q-learning

Navigator.step(observation)
  -> delegue a la Strategy courante
  -> changeable dynamiquement
```

> Le zombie ne sait pas quelle strategie il utilise. C'est le polymorphisme.

---

## Slide 12 -- Niveaux de difficulte

### 3 modes de jeu

| | Facile | Difficile | Impossible |
|---|---|---|---|
| PV Robot | 150 | 80 | 60 |
| Vitesse zombies | x0.6 | x1.3 | x1.5 |
| PV zombies | x0.5 | x1.5 | x2.0 |
| Vagues | 20s | 12s | 10s |
| Armes zombie | Jamais | Vague 3 | Vague 2 |
| IA | A* classique | A* classique | **Q-Learning** |

> En mode Impossible, les zombies APPRENNENT a vous traquer.

---

## Slide 13 -- Apprentissage par Renforcement

### Q-Learning : les zombies apprennent

**Boucle d'apprentissage (a chaque frame) :**
1. Observer l'etat (angle, distance, obstacle)
2. Choisir une action (8 directions)
3. Recevoir une recompense
4. Mettre a jour la Q-table (Bellman)

**Espace d'etats :** 64 etats (8 angles x 4 distances x 2 obstacles)

**Recompenses :**
- +10 : touche le robot
- +1 : se rapproche
- -1 : s'eloigne
- -5 : collision obstacle

---

## Slide 14 -- Q-Learning en detail

### Equation de Bellman

```
Q(s,a) = Q(s,a) + alpha * [R + gamma * max(Q(s',a')) - Q(s,a)]
```

**Parametres :**
- alpha = 0.15 (vitesse d'apprentissage)
- gamma = 0.9 (importance du futur)
- epsilon = 0.5 -> 0.05 (exploration decroissante)

**Agent partage :**
- Tous les zombies partagent la meme Q-table
- Un zombie apprend = tous en beneficient
- Persiste entre les parties !

> Plus vous jouez, plus ils deviennent intelligents.

---

## Slide 15 -- Pipeline IA Zombie complet

### 7 etapes par frame

```
1. Calcul distance/angle vers le robot
2. Recalcul A* (toutes les 1s)
3. Selection waypoint look-ahead
4. Mini-lidar (8 rayons, 2m)
5. Strategy (GoalStrategy ou RLStrategy)
6. Deplacement + evitement collision
7. Tir si arme (distance < 8m)
```

**Mode normal :** A* + GoalStrategy (attraction/repulsion)
**Mode Impossible :** A* + RLStrategy (Q-learning temps reel)

---

## Slide 16 -- Interface du jeu

### HUD complet

**En haut :** Barre de PV (vert/jaune/rouge) | Vague + Timer | Score + Zombies restants | Arme + Munitions | Difficulte

**En bas :** Selecteur d'armes [1] [2] [3] [4]

**Bas droite :** Minimap (grille d'occupation)
- Vert = libre
- Gris = mur
- Bleu = robot
- Rouge = zombies

**Mode Impossible :** Stats RL en temps reel (updates, exploration)

---

## Slide 17 -- Bilan technique

### Recapitulatif des fonctionnalites

| Fonctionnalite | TP Source | Implemente |
|---|---|---|
| Heritage, polymorphisme, encapsulation | TP POO | Oui |
| Architecture MVC | TP MVC | Oui |
| Pygame + Controleur clavier | TP Pygame | Oui |
| Obstacles + Collisions | TP Environnement | Oui |
| Moteur realiste | TP Simulation | Oui |
| Capteur Lidar | TP Capteurs | Oui |
| Packaging (pip install) | TP Packaging | Oui |
| Argparse + Logging | TP Args/Logs | Oui |
| Strategy Pattern | TP Reactive | Oui |
| Cartographie (Bresenham) | TP Cartographie | Oui |
| A* + PID | TP Navigation | Oui |
| Reinforcement Learning | Cours (avance) | Oui |

---

## Slide 18 -- Demo

### Lancement du jeu

```bash
source .venv/bin/activate
python main.py
```

**Controles :**
- ZQSD / Fleches : deplacer
- Souris : viser
- Clic gauche : tirer
- 1-2-3-4 : changer d'arme
- Espace : demarrer

> Demonstration en direct des 3 niveaux de difficulte.

---

## Slide 19 -- Merci

# Merci !

### Questions ?

**Depot GitHub :** (lien du depot)

**Technologies :** Python, Pygame, NumPy

**Auteur :** Houssem MAKNI
