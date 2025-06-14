📄 README.md (début)
markdown
Copier
Modifier
# DevOpsJobTracker

Centralise, collecte et suit toutes les offres DevOps en Suisse.  
Statut de chaque offre (vue, postulée, relance), suivi des candidatures et relances, notifications optionnelles.

## Structure

- Scraping automatique (multi-sites)
- Suivi des candidatures
- Relances programmées
- Interface web simple

## Installation

```bash
git clone <ce_repo>
cd DevOpsJobTracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Configurer .env avec les clés nécessaires.

Lancer l'appli
bash
Copier
Modifier
flask run
yaml
Copier
Modifier

---

## 🔑 .env (exemple, ne pas commit !)

DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxxx/...
SECRET_KEY=ton_secret_flask

yaml
Copier
Modifier

---

## 🏗️ Début de structure des fichiers Python

- **`app/models.py`** : ORM SQLAlchemy avec ta table “offres” (structure plus haut)
- **`app/scraper.py`** : Un scraper pour Indeed/JobUp, extensible
- **`app/notifications.py`** : Gestion Discord/email
- **`run.py`** : Démarre l’appli Flask

---
