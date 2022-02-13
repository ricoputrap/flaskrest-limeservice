import logging

from citric import Client, exceptions

from dotenv import load_dotenv

load_dotenv()
import os

from project.clients.abstract import AbstractClient

# Load tested with this scale of response in local
PARTICIPANT_FETCH_LIMIT = 3000
OPTIONAL_ATTRIBUTES = {"limesurvey_id": 0,
                       "angkatan": 1,
                        "npm": 2
                       }

def _get_optional_attributes(key):
    value = OPTIONAL_ATTRIBUTES[key]
    return f"attribute_{value}"

def client_factory():
    HOST = os.getenv('LIMESURVEY_HOST')
    USERNAME = os.environ.get('LIMESURVEY_USERNAME')
    PASSWORD = os.environ.get('LIMESURVEY_PASSWORD')

    print("HOST")
    print(HOST)
    return Client(HOST, USERNAME, PASSWORD)


class LimesurveyClient(AbstractClient):
    client = client_factory()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls_name = self.__class__.__name__
        self.logger = logging.getLogger(cls_name)

    def get_available_surveys(self, fail_silently=False, username=None):
        username = username if username else None
        try:
            res = self.get_client().list_surveys(username)
            return res
        except exceptions.LimeSurveyStatusError:
            return []
        except Exception as e:
            self.logger.error(str(e))
            if not fail_silently:
                raise e

    def list_participants(self, survey_id, fail_silently=False):
        try:
            # TODO: Pagination logic to scale participants number
            participant_list = self.get_client().list_participants(survey_id, limit=PARTICIPANT_FETCH_LIMIT)
            return participant_list
        except Exception as e:
            self.logger.error(str(e))
            if not fail_silently:
                raise e

    def get_participant_properties(self, survey_id, participant_token, fail_silently=False):
        try:
            res = self.get_client().get_participant_properties(survey_id, participant_token)
            return res
        except Exception as e:
            self.logger.error(str(e))
            if not fail_silently:
                raise e

    def get_survey_properties(self, survey_id, fail_silently=False):
        try:
            res = self.get_client().get_survey_properties(survey_id)
            return res
        except Exception as e:
            self.logger.error(str(e))
            if not fail_silently:
                raise e

    def add_survey_participant(self, survey_id, participant_list, fail_silently=False, try_activate=True):
        if try_activate:
            try:
                # Optional attributes can only be in form of integers, thus mapping of values is provided
                # Ref: https://github.com/LimeSurvey/LimeSurvey/blob/master/application/helpers/remotecontrol/remotecontrol_handle.php#L2563
                attributes = list(OPTIONAL_ATTRIBUTES.values())
                self.get_client().activate_tokens(survey_id, attributes)
            except:
                self.logger.warning(f'Survey {survey_id}: survey has already been activated')
        try:
            res = self.get_client().add_participants(survey_id, participant_list)
            return res
        except Exception as e:
            self.logger.error(str(e))
            if not fail_silently:
                raise e

    def delete_survey_participant(self, survey_id, id, fail_silently=False):
        try:
            res = self.get_client().delete_participants(survey_id, {"id": id})
            return res
        except Exception as e:
            self.logger.error(str(e))
            if not fail_silently:
                raise e
