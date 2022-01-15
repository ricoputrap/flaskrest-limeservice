from project.controllers.v1.email_template import EmailTemplate
from project.controllers.v1.participant import Participant
from project.controllers.v1.survey import Survey
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_restful import Api
import os

'''
@TODO delete soon, for testing only 
(on a real case, these imports should be called on the controllers/services)
'''
from project.models.survey import SurveyModel
from project.models.survey_participant import SurveyParticipantModel
from project.models.survey_blast import SurveyBlastModel
from project.models.activity import ActivityModel
from project.models.email_template import EmailTemplateModel

def init_app():
    '''Flask Application Factory'''
    from project.middleware import AuthMiddleware

    app = Flask(__name__)
    api = Api(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

    from project.utils import db, ma, migrate
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    api.add_resource(Survey, "/api/v1/surveys/", "/api/v1/surveys/<limesurvey_id>")
    api.add_resource(Participant, "/api/v1/surveys/<survey_id>/participants/", "/api/v1/surveys/<survey_id>/participants/duplicates")
    app.add_url_rule("/api/v1/surveys/<survey_id>/participants/csv", endpoint="participant", methods=["POST"])
    app.add_url_rule("/api/v1/surveys/<survey_id>/participants/db", endpoint="participant", methods=["POST"])
    api.add_resource(EmailTemplate, "/api/v1/email-templates/")

    # app.add_url_rule("/api/v1/surveys/participants/db", endpoint="participant", methods=["POST"])
    app.wsgi_app = AuthMiddleware(app.wsgi_app)
    return app