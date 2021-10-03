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

    def truncate_survey_participants(self, survey_id, participant_data):
        current_participants = self.client.list_participants(survey_id)
        if len(current_participants) > 0:
            self.client.delete_survey_participant(survey_id, current_participants)
        self.client.add_survey_participant(survey_id, participant_data)
