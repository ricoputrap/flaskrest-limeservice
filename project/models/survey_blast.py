from project.utils import db

class SurveyBlastModel(db.Model):
    '''
    Survay Blast Channel:
    - EML: email
    - SMS: sms

    Survey Blast Status:
    - PROG: in progress
    - DONE: done
    - FAIL: failed
    '''
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey_model.id'), nullable=False)
    channel = db.Column(db.String(3), default="EML", nullable=False)
    status = db.Column(db.String(4), default="PROG", nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)