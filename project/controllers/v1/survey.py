from flask import make_response, request
from flask_restful import Resource
from project.services.survey import SurveyService
from project.serializers.survey import SurveySchema

class Survey(Resource):

  survey_service = SurveyService()
  survey_list_schema = SurveySchema(many=True)

  def get(self, limesurvey_id = None):
    try:
      if limesurvey_id:
        survey = self.survey_service.get_survey_detail(limesurvey_id)
        print("======= SURVEY:")
        print(survey)
        response = {
          "id": limesurvey_id,
          "name": "Career Survey",
          "status": "DRFT",
          "data": survey
        }
      else:
        page = request.args.get("page")
        pageSize = request.args.get("pageSize")
        response = self.survey_service.get_list_surveys(page, pageSize)
        if "error" in response:
          return make_response(response, 404)

      return response
    except Exception as e:
      return {
        "errors": e
      }