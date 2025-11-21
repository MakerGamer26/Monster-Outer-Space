# Monstres Infinis

Un jeu de capture de monstres généré par IA (Gemini), codé en Python avec PyQt6.

## Fonctionnalités

*   **Génération Infinie :** Monstres, stats, images et capacités générés par Gemini.
*   **Combat :** Système au tour par tour avec équipe de 3 monstres.
*   **Évolution :** Les monstres évoluent (Niveau 45, 90) en changeant d'apparence et de nom.
*   **Boutique & Recrutement :** Achetez des objets (Balls, Potions) et recrutez des starters.
*   **Échange :** Système d'échange sécurisé via code unique.

## Installation

1.  Assurez-vous d'avoir Python 3.10+ installé.
2.  Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Ce jeu nécessite une clé API Google Gemini.

1.  Obtenez une clé sur [Google AI Studio](https://aistudio.google.com/).
2.  Définissez la variable d'environnement `GEMINI_API_KEY` :
    *   **Linux/Mac :** `export GEMINI_API_KEY="votre_cle"`
    *   **Windows :** `set GEMINI_API_KEY="votre_cle"`

Ou modifiez directement `src/config.py` (déconseillé pour le partage).

## Lancement

Lancez le jeu depuis la racine du projet :

```bash
python3 main.py
```

## Structure du Projet

*   `src/ai_manager.py` : Gestion des appels à Gemini.
*   `src/game_engine.py` : Logique du jeu (Combat, Stats, Inventaire).
*   `src/gui/` : Interface utilisateur (PyQt6).
*   `data/` : Base de données SQLite locale.
*   `assets/` : Images générées.

## Crédits

Créé avec l'aide de l'IA. Utilisez Gemini 1.5 Flash ou Pro pour de meilleurs résultats.
