from project.models.survey import SurveyModel
from project.models.survey_participant import SurveyParticipantModel
from project.utils import db

from datetime import datetime

def check_if_survey_exists(survey_id):
    survey = SurveyModel.query.filter_by(limesurvey_id=survey_id).first()
    if not survey:
        return {
            "error": {
                "status_code": 404,
                "error": {
                "title": "Survey doesn't exist",
                "detail": "Survey with id " + str(survey_id) + " doesn't exist."
                }
            }
        }
    return { "data": survey }


def save_participants_to_limeservice_db(survey, creator_id, submitted_participants):
    for participant in submitted_participants:
        new_participant = SurveyParticipantModel(
            survey_id = survey.id,
            name = participant["name"],
            email = participant["email"],
            npm = participant["npm"],
            batch_year = participant["batch_year"],
            major = participant["major"],
            created_at = datetime.now(),
            created_by = creator_id
        )

        db.session.add(new_participant)
        db.session.commit()