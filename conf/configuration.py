"""
Ce module contient le code pour charger la configuration à partir d'un fichier JSON.
Variables:
    - conf (dict): Dictionnaire contenant la configuration chargée à partir du fichier JSON.
"""
import json
import os

conf = {}
with open(os.path.dirname(os.path.realpath(__file__)) + "/configuration.json", encoding="utf-8") as json_file:
    conf = json.load(json_file)