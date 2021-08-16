from project.utils import db

class EmailTemplateModel(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), nullable=False)
  subject = db.Column(db.String(255), nullable=False)
  body = db.Column(db.Text, nullable=False)