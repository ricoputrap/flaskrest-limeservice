from project.utils import db
from datetime import datetime

class SurveyModel(db.Model):
    '''
    Survey Status:
    - DRFT: draft
    - DUPL: duplicate
    - SAVE: saving
    - FINL: final

    `backref` is a simple way to declare a new property on 
    (for example) the `SurveyParticipantModel` class. 
    So, we can then also use `participant.survey` to 
    get to the survey instance that is referenced by `participant` 
    (an object instance of SurveyParticipantModel).

    `lazy=True` means that SQLAlchemy will load the data 
    as necessary in one go using a standard select statement.
    '''
    id =  db.Column(db.Integer, primary_key=True)
    limesurvey_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(4), nullable=False, default="DRFT")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    created_by = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.now())
    updated_by = db.Column(db.Integer, nullable=True)
    participants = db.relationship('SurveyParticipantModel', backref='survey', lazy=True)
    activities = db.relationship('ActivityModel', backref='survey', lazy=True)
    survey_blasts = db.relationship('SurveyBlastModel', backref='survey', lazy=True)