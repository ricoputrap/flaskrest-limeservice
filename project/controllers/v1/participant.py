from flask import request, make_response
from flask_restful import Resource
from project.services.participant import ParticipantService

class Participant(Resource):

  participant_service = ParticipantService()

  def get(self, survey_id):
    try:
      page = request.args.get("page")
      pageSize = request.args.get("pageSize")
      response = self.participant_service.get_list_participants(survey_id, page, pageSize)
      
      if "error" in response:
        return make_response(response, response["status_code"])
      return response
    except Exception as e:
      return {
        "errors": e
      }