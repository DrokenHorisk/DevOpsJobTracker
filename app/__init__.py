from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from flask import redirect, url_for

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates'))
    app = Flask(__name__, template_folder=template_dir, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py', silent=True)
    
    db.init_app(app)
    migrate.init_app(app, db)

    from . import models

    # Création auto des tables si pas présentes
    with app.app_context():
        db.create_all()

    # ROUTE EXEMPLE
    from flask import render_template

    from flask import request, flash

    @app.route("/relance/<int:offer_id>", methods=["POST"])
    def relance(offer_id):
        from .models import JobOffer
        job = JobOffer.query.get_or_404(offer_id)
        job.relance_effectuee = True
        db.session.commit()
        return redirect(url_for("index"))


    @app.route("/")
    def index():
        print("Current working directory:", os.getcwd())
        print("Templates in /app/templates/:", os.listdir("/app/templates/"))
        from .models import JobOffer
        offers = JobOffer.query.order_by(JobOffer.date_publication.desc()).all()
        return render_template("index.html", offers=offers, current_date=date.today())

    from datetime import date

    @app.route("/a-relancer")
    def a_relancer():
        from .models import JobOffer
        today = date.today()
        # Toutes les offres dont la date de relance est aujourd'hui ou avant, et qui n'ont PAS été relancées
        offers = JobOffer.query.filter(
            JobOffer.date_relance <= today,
            JobOffer.date_relance != None,
            JobOffer.relance_effectuee == False
        ).order_by(JobOffer.date_relance.asc()).all()
        return render_template("index.html", offers=offers, current_date=date.today())


    @app.route("/reset_db")
    def reset_db():
        if request.args.get("secret") != "votremotdepasse":
            return "Non autorisé", 403
        from .models import JobOffer
        JobOffer.query.delete()
        db.session.commit()
        return redirect(url_for("index"))
    @app.route("/postuler/<int:offer_id>", methods=["POST"])
    def postuler(offer_id):
        from .models import JobOffer
        job = JobOffer.query.get_or_404(offer_id)
        job.postule = True
        job.date_postulation = datetime.today().date()
        # Relance prévue 15 jours plus tard
        job.date_relance = datetime.today().date() + timedelta(days=15)
        db.session.commit()
        return redirect(url_for("index"))

    @app.route("/note/<int:offer_id>", methods=["POST"])
    def ajouter_note(offer_id):
        from .models import JobOffer
        job = JobOffer.query.get_or_404(offer_id)
        note = request.form.get("note")
        job.notes = note
        db.session.commit()
        flash("Note ajoutée !", "success")
        return redirect(url_for("index"))

    @app.route("/modifier/<int:offer_id>", methods=["POST"])
    def modifier_offre(offer_id):
        from .models import JobOffer
        job = JobOffer.query.get_or_404(offer_id)
        date_relance = request.form.get("date_relance")
        notes = request.form.get("notes")
        if date_relance:
            from datetime import datetime
            job.date_relance = datetime.strptime(date_relance, "%Y-%m-%d").date()
        job.notes = notes
        db.session.commit()
        return redirect(url_for("index"))
    @app.route("/details/<int:offer_id>")
    def details(offer_id):
        from .models import JobOffer
        job = JobOffer.query.get_or_404(offer_id)
        return render_template("details.html", offer=job)

    from app.scraper import scrape_swissdevjobs_selenium

    def scheduled_scrape():
        print("Lancement du scraping planifié...")
        scrape_swissdevjobs_selenium()
        print("Scraping planifié terminé.")


    # On utilise un scheduler pour automatiser le scraping
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=scheduled_scrape, trigger="interval", hours=2)  # toutes les 2h
    scheduler.start()

    # Lancer un scraping au démarrage
    with app.app_context():
        scheduled_scrape()

    return app
