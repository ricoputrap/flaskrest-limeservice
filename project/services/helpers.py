from project.models.survey import SurveyModel

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