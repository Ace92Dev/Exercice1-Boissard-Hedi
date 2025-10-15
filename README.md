ToDo API (Flask minimal)

Projet simplifié en MVC avec une API JSON Flask (pas de templates HTML).

Structure
- models — définitions des modèles (Task, DeadlineTask, enums)
- controller — logique en mémoire (CRUD + filtres + stats)
- view — helpers d'affichage (non utilisés par l'API)

Démarrage
- Installer les dépendances: `pip install -r requirements.txt`
- Lancer le serveur: `python -m todo_cli.app` ou `flask --app todo_cli.app run`
- Santé: `GET /health` → `{ "status": "ok" }`

Endpoints (principaux)
- `GET /tasks` — liste des tâches (params: `status`, `priority`, `tag`, `overdue`, `search`, `sort`)
- `POST /tasks` — crée une tâche `{title, description?, priority?, due?, tags?}`
- `GET /tasks/<id>` — détail d’une tâche
- `PATCH /tasks/<id>` — met à jour des champs (title, description, priority, due, status, tags)
- `DELETE /tasks/<id>` — supprime une tâche
- `POST /tasks/<id>/complete` — marque DONE
- `POST /tasks/<id>/status` — fixe un statut `{status}`
- `DELETE /tasks?confirm=yes` — supprime toutes les tâches
- `GET /stats` — statistiques agrégées

Remarques
- Stockage en mémoire (pas de persistance).
- Réponses JSON uniquement.
