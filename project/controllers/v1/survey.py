from flask import make_response
from flask_restful import Resource
from project.services.survey import SurveyService
from project.serializers.survey import SurveySchema

class Survey(Resource):

  survey_service = SurveyService()
  survey_list_schema = SurveySchema(many=True)

  def get(self):
    try:
      surveys = self.survey_service.get_list_surveys()
      print("========== SURVEYS =========")
      print(surveys)

      response = {
        "data": {
          "surveys": self.survey_list_schema.dump(surveys)
        }
      }

      return response
    except Exception as e:
      return {
        "errors": e
      }