from project.models.survey_participant import SurveyParticipantModel
from project.models.survey import SurveyModel
import math

class ParticipantService:


  def get_list_participants(self, survey_id, page, pageSize):

    # check if survey exists
    survey = SurveyModel.query.filter_by(limesurvey_id=survey_id).first()
    if not survey:
      return {
        "status_code": 404,
        "error": {
          "title": "Survey doesn't exist",
          "detail": "Survey with id " + str(survey_id) + " doesn't exist."
        }
      }

    # prepare the parameter values
    page = int(page) if page else 1
    pageSize = int(pageSize) if pageSize else 5

    participants = SurveyParticipantModel.query.filter_by(survey_id=survey_id).all()
    real_total_participants = len(participants)
    real_total_pages = math.ceil(real_total_participants / pageSize)

    if real_total_participants == 0:
      return {
        "currentPage": 1,
        "totalItems": 0,
        "items": []
      }

    elif page > real_total_pages:
      return {
        "status_code": 404,
        "error": {
          "title": "Page requested is not available",
          "detail": "Page " + str(page) + " is requested, only " + str(real_total_pages) + " is available."
        }
      }
    else:
      computed_participants = []
      end_idx = page * pageSize
      end_idx = end_idx if end_idx <= real_total_participants else real_total_participants
      start_idx = pageSize * (page - 1)

      for i in range(start_idx, end_idx):
        computed_participants.append({
          "id": participants[i].id,
          "name": participants[i].name,
          "email": participants[i].email,
          "npm": participants[i].npm,
          "angkatan": participants[i].batch_year,
        })
      
      return {
        "currentPage": page,
        "totalItems": real_total_participants,
        "items": computed_participants
      }