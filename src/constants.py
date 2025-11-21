TYPES = [
    "Eau", "Feu", "Electricité", "Plante", "Pierre",
    "Espace", "Temps", "Lumière", "Ténèbre", "Psy",
    "Fantome", "Poison", "Metal", "Monstre", "Normal"
]

# Key: Attacker Type, Value: {Defender Type: Multiplier}
# Default is 1.0. Weakness usually 2.0, Resistance 0.5.
TYPE_CHART = {
    "Eau": {"Feu": 2.0, "Pierre": 2.0, "Monstre": 2.0, "Plante": 0.5, "Electricité": 0.5},
    "Feu": {"Plante": 2.0, "Metal": 2.0, "Monstre": 2.0, "Eau": 0.5, "Pierre": 0.5},
    "Plante": {"Eau": 2.0, "Pierre": 2.0, "Psy": 1.5, "Feu": 0.5, "Poison": 0.5},
    "Electricité": {"Eau": 2.0, "Metal": 2.0, "Pierre": 0.5, "Plante": 0.5},
    "Pierre": {"Feu": 2.0, "Electricité": 2.0, "Poison": 2.0, "Metal": 0.5, "Eau": 0.5},
    "Espace": {"Temps": 2.0, "Ténèbre": 1.5, "Espace": 0.5},
    "Temps": {"Lumière": 2.0, "Poison": 2.0, "Temps": 0.5},
    "Lumière": {"Ténèbre": 2.0, "Fantome": 2.0, "Lumière": 0.5, "Temps": 0.5},
    "Ténèbre": {"Psy": 2.0, "Fantome": 2.0, "Lumière": 2.0, "Ténèbre": 0.5},
    "Psy": {"Monstre": 2.0, "Poison": 2.0, "Ténèbre": 0.5, "Metal": 0.5},
    "Fantome": {"Psy": 2.0, "Normal": 0.0, "Ténèbre": 0.5},
    "Poison": {"Plante": 2.0, "Monstre": 2.0, "Metal": 0.5, "Pierre": 0.5},
    "Metal": {"Plante": 2.0, "Pierre": 2.0, "Fantome": 2.0, "Feu": 0.5, "Electricité": 0.5},
    "Monstre": {"Normal": 2.0, "Psy": 0.5, "Poison": 0.5},
    "Normal": {"Fantome": 0.0, "Metal": 0.5}
}

def get_type_multiplier(attacker_type, defender_type_1, defender_type_2=None):
    mult = 1.0
    if attacker_type in TYPE_CHART:
        mult *= TYPE_CHART[attacker_type].get(defender_type_1, 1.0)
        if defender_type_2:
            mult *= TYPE_CHART[attacker_type].get(defender_type_2, 1.0)
    return mult
