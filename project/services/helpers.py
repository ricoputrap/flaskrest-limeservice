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


def extract_angkatan_and_jurusan_in_params(params):
    angkatan = params["angkatan"] if "angkatan" in params else ""
    jurusan = params["jurusan"] if "jurusan" in params else ""

    if not angkatan and not jurusan:
        return {
            "error": {
                "status_code": 400,
                "error": {
                    "title": "No angkatan or jurusan in request body",
                    "detail": "Must specify either `angkatan` or `jurusan` in request body."
                }
            }
        }
    
    return {
        "data": [angkatan, jurusan]
    }


def extract_participants_from_atlas_db(users):
    """
    extract the users data with this format:  { name, email, npm, batch_year, major }
    """
    participants = []
    for user in users:
        computed_user = {
            "name": user["name"],
            "email": user["email"],
            "npm": user["educations"][-1]["uiSsoNpm"],
            "batch_year": user["educations"][-1]["csuiClassYear"],
            "major": user["educations"][-1]["csuiProgram"],
        }
        participants.append(computed_user)

    return participants


def validate_email_template(req_body):
    name = req_body["name"] if "name" in req_body else ""
    subject = req_body["subject"] if "subject" in req_body else ""
    body = req_body["body"] if "body" in req_body else ""

    # populate empty fields
    empty_fields = []
    if not name:
        empty_fields.append({ "field": "name", "value": name })
    if not subject:
        empty_fields.append({ "field": "subject", "value": subject })
    if not body:
        empty_fields.append({ "field": "body", "value": body })
    
    # return error if any field empty
    if len(empty_fields) > 0:
        res = { 
            "status_code": 400,
            "error": {
                "title": "Bad Request"
            }
        }
        if len(empty_fields) == 1:
            error_detail = "Missing the value of " + empty_fields[0]["field"]
        elif len(empty_fields) == 2:
            error_detail = "Missing the values of " + empty_fields[0]["field"] \
                + " and " + empty_fields[1]["field"]
        else:
            error_detail = "Missing the values of " + empty_fields[0]["field"] \
                + ", " + empty_fields[1]["field"] + ", and" + empty_fields[2]["field"]
        res["error"]["detail"] = error_detail
        return res
    
    return req_body