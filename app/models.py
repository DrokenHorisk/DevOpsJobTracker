from . import db
from datetime import datetime

class JobOffer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(256), nullable=False)
    entreprise = db.Column(db.String(256))
    lien = db.Column(db.String(512), unique=True, nullable=False)
    date_publication = db.Column(db.Date, nullable=False)
    postule = db.Column(db.Boolean, default=False)
    date_postulation = db.Column(db.Date)
    date_relance = db.Column(db.Date)
    relance_effectuee = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    salaire = db.Column(db.String(128))        
    localisation = db.Column(db.String(255))   
    keywords = db.Column(db.String(512))

    def __repr__(self):
        return f"<JobOffer {self.titre} at {self.entreprise}>"
