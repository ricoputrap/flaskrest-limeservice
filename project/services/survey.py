from project.models.survey import SurveyModel
from project.clients.limesurvey.api import LimesurveyClient
from project.utils import db
import math

class SurveyService:

  client = LimesurveyClient()

  def get_list_surveys(self, page, pageSize):

    # get from limesurvey
    available_surveys = self.client.get_available_surveys()
    surveys = []

    # update the saved survey data in limeservice db 
    # to be consistent with the ones in limesurvey
    for survey_from_limesurvey in available_surveys:
      survey_in_db = SurveyModel.query.filter_by(limesurvey_id=survey_from_limesurvey['sid']).first()
      
      if not survey_in_db:
        new_survey = SurveyModel(
          limesurvey_id = survey_from_limesurvey['sid'],
          title = survey_from_limesurvey['surveyls_title'],
          created_by = 1 # soon updated to use the correct data
        )
        db.session.add(new_survey)
        db.session.commit()

    # prepare the parameter values
    page = int(page) if page else 1
    pageSize = int(pageSize) if pageSize else 5
    
    # prepare survey data to be returned
    surveys_in_db = SurveyModel.query.all()
    real_total_surveys = len(surveys_in_db)
    real_total_pages = math.ceil(real_total_surveys / pageSize)

    if page > real_total_pages:
      return {
        "error": {
          "title": "Page requested is not available",
          "detail": "Page " + str(page) + " is requested, only " + str(real_total_pages) + " is available."
        }
      }
    else:
      end_idx = page * pageSize
      end_idx = end_idx if end_idx <= real_total_surveys else real_total_surveys
      start_idx = pageSize * (page - 1)

      for i in range(start_idx, end_idx):
        surveys.append({
          "id": surveys_in_db[i].limesurvey_id,
          "name": surveys_in_db[i].title
        })
    
    response = {
      "currentPage": page,
      "totalItems": real_total_surveys,
      "items": surveys
    }
    return response

  