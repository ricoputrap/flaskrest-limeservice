from project.utils import db

class ActivityModel(db.Model):
    '''
    Activity Types:
    - ADD_PRTCP_DB: add participants from DB
    - ADD_PRTCP_CSV: add participants from CSV
    - FIX_DUPL: fix duplicate data
    - DEL_PRTCP: delete participants
    - SAV_PRTCP: save participants
    - BLST_MAIL: blast email
    - CRT_MAIL_TEMP: create email template
    '''
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey_model.id'), nullable=False)
    activity_type = db.Column(db.String(16), nullable=False)
    description = db.Column(db.Text, nullable=False)
    additional_data = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, nullable=False)