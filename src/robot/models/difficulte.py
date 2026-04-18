"""
Classe Difficulte - Configuration des niveaux de difficulte.
Facile, Difficile, Impossible (avec apprentissage par renforcement).
"""


class Difficulte:
    """Parametres de difficulte du jeu."""

    FACILE = "facile"
    DIFFICILE = "difficile"
    IMPOSSIBLE = "impossible"

    CONFIGS = {
        FACILE: {
            "nom": "Facile",
            "description": "Zombies lents, peu de PV",
            "robot_pv": 150,
            "zombie_vitesse_mult": 0.6,
            "zombie_pv_mult": 0.5,
            "intervalle_vague": 20.0,
            "max_zombies_par_vague": 15,
            "vague_arme_zombie": 99,  # jamais d'arme
            "prob_arme_zombie": 0.0,
            "use_rl": False,
        },
        DIFFICILE: {
            "nom": "Difficile",
            "description": "Zombies rapides et armes",
            "robot_pv": 80,
            "zombie_vitesse_mult": 1.3,
            "zombie_pv_mult": 1.5,
            "intervalle_vague": 12.0,
            "max_zombies_par_vague": 30,
            "vague_arme_zombie": 3,
            "prob_arme_zombie": 0.5,
            "use_rl": False,
        },
        IMPOSSIBLE: {
            "nom": "Impossible (RL)",
            "description": "Zombies avec IA par renforcement",
            "robot_pv": 60,
            "zombie_vitesse_mult": 1.5,
            "zombie_pv_mult": 2.0,
            "intervalle_vague": 10.0,
            "max_zombies_par_vague": 35,
            "vague_arme_zombie": 2,
            "prob_arme_zombie": 0.6,
            "use_rl": True,
        },
    }

    @staticmethod
    def get_config(niveau):
        """Retourne la config pour un niveau donne."""
        return Difficulte.CONFIGS.get(niveau, Difficulte.CONFIGS[Difficulte.FACILE])
