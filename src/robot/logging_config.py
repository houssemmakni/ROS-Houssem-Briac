"""
Configuration du système de logging.
"""

import logging


def configurer_logs(debug=False):
    """Configure le logging pour le projet."""
    niveau = logging.DEBUG if debug else logging.INFO
    fmt = "[%(asctime)s] %(levelname)-8s %(name)s : %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=niveau,
        format=fmt,
        datefmt=datefmt,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("robot.log", mode="w"),
        ],
    )
