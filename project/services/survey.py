import concurrent
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

from citric.exceptions import LimeSurveyStatusError

from project.models.survey import SurveyModel
from project.clients.limesurvey.api import LimesurveyClient, _get_optional_attributes
from project.services.participant import ParticipantService, _get_total_participants
from project.utils import db
import math

# Good number of concurrency to start with
SURVEY_PARTICIPANT_DELETE_CONCURRENCY = 40
SURVEY_PARTICIPANT_INSERT_CONCURRENCY = 5
SURVEY_PARTICIPANT_INSERT_SIZE = 100

LIMESURVEY_ID_MAPPING = _get_optional_attributes("limesurvey_id")
ANGKATAN_MAPPING = _get_optional_attributes("angkatan")
NPM_MAPPING = _get_optional_attributes("npm")

class SurveyService:
    client = LimesurveyClient()

    def get_list_surveys(self):
        # get from limesurvey
        available_surveys = self.client.get_available_surveys()

        # surveys = []
        return available_surveys

    def __retrieve_and_update_surveys(self):
        # get from limesurvey
        available_surveys = self.client.get_available_surveys()

        for survey_from_limesurvey in available_surveys:
            self.__update_survey_in_db(survey_from_limesurvey)

    def __update_survey_in_db(self, survey_from_limesurvey):
        '''
        update the saved survey data in limeservice db 
        to be consistent with the available ones in limesurvey
        '''
        survey_in_db = SurveyModel.query.filter_by(limesurvey_id=survey_from_limesurvey['sid']).first()

        if not survey_in_db:
            new_survey = SurveyModel(
                limesurvey_id=survey_from_limesurvey['sid'],
                title=survey_from_limesurvey['surveyls_title'],
                created_by=self.client.get_survey_properties(survey_from_limesurvey['sid'])['owner_id']
            )
            db.session.add(new_survey)
            db.session.commit()

    def get_list_surveys(self, page, pageSize):

        self.__retrieve_and_update_surveys()

        # prepare the parameter values
        page = int(page) if page else 1
        pageSize = int(pageSize) if pageSize else 5

        # prepare survey data to be returned
        surveys_in_db = SurveyModel.query.all()
        real_total_surveys = len(surveys_in_db)
        real_total_pages = math.ceil(real_total_surveys / pageSize)

        if page > real_total_pages:
            return {
                "status_code": 404,
                "error": {
                    "title": "Page requested is not available",
                    "detail": "Page " + str(page) + " is requested, only " + str(real_total_pages) + " is available."
                }
            }
        else:
            surveys = []
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

    def get_survey_detail(self, limesurvey_id):

        self.__retrieve_and_update_surveys()
        survey = SurveyModel.query.filter_by(limesurvey_id=limesurvey_id).first()

        if not survey:
            return {
                "status_code": 404,
                "error": {
                    "title": "Survey doesn't exist",
                    "detail": "Survey with id " + str(limesurvey_id) + " doesn't exist."
                }
            }
        else:
            return {
                "id": limesurvey_id,
                "name": survey.title,
                "status": survey.status
            }

    def get_list_survey_participants(self, survey_id):
        return self.client.list_participants(survey_id)

    def _delete_survey_participant(self, survey_id, participant):
        participant_id = participant.get("tid")
        res = self.client.delete_survey_participant(survey_id, participant_id)
        return res

    def _insert_survey_participants(self, survey_id, limesurvey_client, participant_service, page,
                                    page_size):
        participant_data = participant_service.get_list_participants(survey_id, page, page_size)["items"]
        for participant in participant_data:
            participant[LIMESURVEY_ID_MAPPING] = participant["id"]
            participant[ANGKATAN_MAPPING] = participant["angkatan"]
            participant[NPM_MAPPING] = participant["npm"]

        limesurvey_participants = limesurvey_client.add_survey_participant(survey_id, participant_data)
        for participant in limesurvey_participants:
            participant_service.add_participant_token(participant[LIMESURVEY_ID_MAPPING], participant["token"])
        return True

    def truncate_survey_participants(self, survey_id):
        try:
            current_participants = self.client.list_participants(survey_id)
        except LimeSurveyStatusError:
            current_participants = []
        if len(current_participants) > 0:
            # parallel execution since we need to hit api one by one for delete
            pool = ThreadPoolExecutor(SURVEY_PARTICIPANT_DELETE_CONCURRENCY)
            pool.map(self._delete_survey_participant, repeat(survey_id), current_participants)

        total_participants = _get_total_participants(survey_id)
        total_batches = math.ceil(total_participants / SURVEY_PARTICIPANT_INSERT_SIZE)
        participant_service = ParticipantService()
        participant_service.clear_survey_participants_token(survey_id)
        for batch in range(1, total_batches + 1):
            self._insert_survey_participants(survey_id,
                                             self.client,
                                             participant_service,
                                             batch,
                                             SURVEY_PARTICIPANT_INSERT_SIZE)
        db.session.commit()
        return True
