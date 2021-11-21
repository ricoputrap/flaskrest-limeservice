from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

from citric.exceptions import LimeSurveyStatusError

from project.models.survey import SurveyModel
from project.clients.limesurvey.api import LimesurveyClient

# from utils import db

# Good number of concurrency to start with
SURVEY_PARTICIPANT_DELETE_CONCURRENCY = 40


class SurveyService:
    client = LimesurveyClient()

    def get_list_surveys(self):
        # get from limesurvey
        available_surveys = self.client.get_available_surveys()

        # surveys = []
        return available_surveys

    def get_list_survey_participants(self, survey_id):
        return self.client.list_participants(survey_id)

    def _delete_survey_participant(self, survey_id, participant):
        participant_id = participant.get("tid")
        res = self.client.delete_survey_participant(survey_id, participant_id)
        print(res)
        return res

    def truncate_survey_participants(self, survey_id, participant_data):
        try:
            current_participants = self.client.list_participants(survey_id)
        except LimeSurveyStatusError:
            current_participants = []
        if len(current_participants) > 0:
            # parallel execution since we need to hit api one by one for delete
            pool = ThreadPoolExecutor(SURVEY_PARTICIPANT_DELETE_CONCURRENCY)
            pool.map(self._delete_survey_participant, repeat(survey_id), current_participants)
        self.client.add_survey_participant(survey_id, participant_data)
