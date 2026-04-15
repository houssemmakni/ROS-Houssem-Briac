"""
Classe VueTerminal - Affichage du robot dans le terminal.
"""


class VueTerminal:
    """Vue Terminal : affiche les informations du robot en mode texte."""

    def dessiner_robot(self, robot):
        print(f"Robot -> x={robot.x:.2f}, y={robot.y:.2f}, orientation={robot.orientation:.2f}")

    def dessiner_environnement(self, env):
        robot = env.robot
        if robot:
            self.dessiner_robot(robot)
        print(f"Obstacles: {len(env.obstacles)}, Zombies: {len(env.zombies)}")
