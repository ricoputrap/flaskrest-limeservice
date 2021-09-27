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
        response = self.survey_service.get_survey_detail(limesurvey_id)
        if "error" in response:
          return make_response(response, response["status_code"])
      else:
        page = request.args.get("page")
        pageSize = request.args.get("pageSize")
        response = self.survey_service.get_list_surveys(page, pageSize)
        if "error" in response:
          return make_response(response, response["status_code"])

      return response
    except Exception as e:
      return {
        "errors": e
      }