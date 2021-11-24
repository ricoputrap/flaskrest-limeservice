from project.models.survey import SurveyModel
from project.models.survey_participant import SurveyParticipantModel
from project.utils import db

from datetime import datetime
import pandas as pd


def check_if_survey_exists(survey_id):
    survey = SurveyModel.query.filter_by(limesurvey_id=survey_id).first()
    if not survey:
        return {
            "error": {
                "status_code": 404,
                "error": {
                "title": "Survey doesn't exist",
                "detail": "Survey with id " + str(survey_id) + " doesn't exist."
                }
            }
        }
    return { "data": survey }


def save_participants_to_limeservice_db(survey, creator_id, submitted_participants):
    for participant in submitted_participants:
        new_participant = SurveyParticipantModel(
            survey_id = survey.id,
            name = participant["name"],
            email = participant["email"],
            npm = participant["npm"],
            batch_year = participant["batch_year"],
            major = participant["major"],
            created_at = datetime.now(),
            created_by = creator_id
        )

        db.session.add(new_participant)
        db.session.commit()


def extract_participants_from_csv(csv_file):

    # prepare dataframe from the csv file
    df = pd.read_csv(csv_file)
    df = df.rename(columns={
        "nama": "name",
        "angkatan": "batch_year",
        "jurusan": "major"
    })
    submitted_participants = df.to_dict('records')

    # check if the data size is enough
    if len(submitted_participants) < 1:
        return {
            "error": {
                "status_code": 500,
                "error": {
                    "title": "Empty Participant Data",
                    "detail": "The file has no data. Please provide at least 1 row participant data."
                }
            }
        }

    return { "data": submitted_participants }


def get_participants_from_limeservice_db_by_email(survey_id):
    participants_dict_by_email={}
    saved_participants = SurveyParticipantModel.query.filter_by(survey_id=survey_id).all()

    for participant in saved_participants:
        participant_email = participant.email
        participant_data = {
            "id": participant.id,
            "name": participant.name,
            "email": participant.email,
            "npm": participant.npm,
            "angkatan": participant.batch_year,
        }
        if participant_email not in participants_dict_by_email:
            participants_dict_by_email[participant_email] = [participant_data]
        else:
            participants_dict_by_email[participant_email].append(participant_data)
    
    return participants_dict_by_email


def remove_duplicate_participants_inplace(participants_dict_by_email):
    email_to_remove = []
		
    for email, data in participants_dict_by_email.items():
        if len(data) < 2:
            email_to_remove.append(email)

    for email in email_to_remove:
        del participants_dict_by_email[email]