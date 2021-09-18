from project.models.survey import SurveyModel
from project.clients.limesurvey.api import LimesurveyClient
# from utils import db

class SurveyService:

  client = LimesurveyClient()

  def get_list_surveys(self):

    # get from limesurvey
    available_surveys = self.client.get_available_surveys()

    # surveys = []
    return available_surveys