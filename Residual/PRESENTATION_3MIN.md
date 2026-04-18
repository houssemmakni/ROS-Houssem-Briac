# Robot Zombie Survival -- Presentation 3 minutes

> Format pour Gamma (gamma.app). Chaque `## Slide` = 1 diapo. ~20s par slide.

---

## Slide 1 -- Titre

# Robot Zombie Survival

### POO + Robotique Mobile + IA

Houssem MAKNI -- M2 IMT Nord-Europe -- 2025-2026

**51 fichiers Python | 30+ classes | 3 niveaux | Q-Learning**

---

## Slide 2 -- Le Jeu

Un robot survit a des vagues de zombies dans une arene 2D.

**4 armes** : Fusil, Pompe, Laser, Lance-Flamme
**3 difficultes** : Facile, Difficile, Impossible (IA par renforcement)
**1 mode auto-play** : le robot joue tout seul grace au Q-Learning

Barre de PV, vagues toutes les 15s, minimap en temps reel, zombies intelligents.

---

## Slide 3 -- Architecture MVC

```
src/robot/
|-- models/
|   |-- armes/       Fusil, Pompe, Laser, LanceFlamme
|   |-- moteurs/     Differentiel, Omni, Realiste
|   |-- obstacles/   Rectangle, Circulaire
|   |-- capteurs/    Lidar (36 rayons)
|   |-- navigation/  GrilleOccupation, A*, Bresenham
|   |-- rl/          Q-Learning robot + zombies
|
|-- views/           VuePygame (HUD, minimap)
|-- controllers/     Clavier, PID, Strategy, RL auto-play
```

**1 fichier = 1 classe.** MVC strict, sous-dossiers par domaine.

---

## Slide 4 -- POO Appliquee

**6 classes abstraites (ABC)** : Moteur, Obstacle, Capteur, Arme, Controleur, Strategy

**Polymorphisme** : `obstacle.collision()` fonctionne sur Rectangle ET Cercle sans if/else

**Composition** : Le robot possede un Moteur et des Capteurs, sans connaitre leur type

**Encapsulation** : Attributs `__prives`, acces via `@property`

**Strategy Pattern** : Changer le comportement d'un zombie en 1 ligne : `navigator.set_strategy(GoalStrategy())`

---

## Slide 5 -- Capteur Lidar

Le Lidar envoie **36 rayons** sur 360 degres et mesure les distances aux obstacles.

**Utilise par :**
- Le **Cartographe** : remplit la grille d'occupation (algorithme de Bresenham) → minimap
- Le **robot RL** : 2 features extraites du Lidar integrees dans l'etat Q-Learning (obstacle devant + espace confine)
- Les **zombies** : mini-lidar 8 rayons pour l'evitement reactif

Le Lidar utilise le **polymorphisme** : `obstacle.intersection_rayon()` -- meme methode, calcul different (quadratique pour cercle, intervalles pour rectangle).

---

## Slide 6 -- IA des Zombies

**Pipeline complet a chaque frame :**

1. **A*** sur la grille d'occupation → chemin autour des murs
2. **Strategy Pattern** (GoalStrategy) → attraction cible + repulsion obstacles
3. **Mini-lidar** → evitement local
4. Tir automatique si arme (vague 5+)

**Mode Impossible** : les zombies utilisent le **Q-Learning** au lieu de GoalStrategy.
Ils apprennent en temps reel a traquer le joueur.

---

## Slide 7 -- Apprentissage par Renforcement

### Q-Learning : tout est appris, rien n'est code en dur

**Robot auto-play (1152 etats x 36 actions) :**

| Ce que le RL decide | Comment |
|---|---|
| Direction de deplacement | 8 directions + rester |
| Choix de l'arme | Fusil / Pompe / Laser / Flamme |
| Evitement des murs | Via les donnees Lidar |

**Equation de Bellman :**
`Q(s,a) = Q(s,a) + alpha * [R + gamma * max(Q(s',a')) - Q(s,a)]`

**Recompenses :** +50 kill, +1 survie, -10 degats, -100 mort, -3 collision mur

L'agent apprend seul que le lance-flamme est mieux de pres et le laser de loin.

---

## Slide 8 -- Pre-entrainement + Persistance

**Premier lancement** : 3000 episodes en simulation acceleree (~5 secondes)
→ Le robot arrive deja entraine (~1500 kills)

**Parties suivantes** : charge la Q-table depuis le disque (instantane)
→ Continue d'apprendre pendant le jeu
→ Sauvegarde automatique au game over et a la fermeture

**Plus on joue, plus l'IA s'ameliore.**

---

## Slide 9 -- Demo + Conclusion

### Toutes les fonctionnalites des TPs integrees :

POO, MVC, Pygame, Moteurs, Capteurs, Obstacles, Collisions,
Packaging, Argparse, Logging, Navigation reactive, Cartographie,
A*, PID, Strategy Pattern, **Apprentissage par Renforcement**

### Demo en direct

```
python main.py
```

**Merci !**
