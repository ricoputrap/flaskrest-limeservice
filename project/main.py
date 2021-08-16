from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_restful import Api
import os

'''
@TODO delete soon for testing only 
(on a real case, these imports should be called on controllers/services)
'''
from project.models.survey import SurveyModel
from project.models.survey_participant import SurveyParticipantModel
from project.models.survey_blast import SurveyBlastModel
from project.models.activity import ActivityModel
from project.models.email_template import EmailTemplateModel

def init_app():
  '''Flask Application Factory'''
  app = Flask(__name__)
  api = Api(app)

  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

  from project.utils import db, ma, migrate
  db.init_app(app)
  ma.init_app(app)
  migrate.init_app(app, db)

  return app