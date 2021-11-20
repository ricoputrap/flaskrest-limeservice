from project.models.survey_participant import SurveyParticipantModel
from project.models.survey import SurveyModel
from project.clients.limesurvey.api import LimesurveyClient
from project.utils import db
import math
import pandas as pd
import json
from datetime import datetime 


class ParticipantService:

  client = LimesurveyClient()

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

    participants = SurveyParticipantModel.query.filter_by(survey_id=survey.id).all()
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

  def add_participants_from_csv(self, survey_id, csv_file):

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
        "status_code": 500,
        "error": {
          "title": "Empty Participant Data",
          "detail": "The file has no data. Please provide at least 1 row participant data."
        }
      }
    
    # save participants to limeservice db
    for participant in submitted_participants:
      
      new_participant = SurveyParticipantModel(
        survey_id = survey.id,
        name = participant["name"],
        email = participant["email"],
        npm = participant["npm"],
        batch_year = participant["batch_year"],
        major = participant["major"],
        created_at = datetime.now(),
        created_by = self.client.get_survey_properties(survey_id)['owner_id']
      )

      db.session.add(new_participant)
      db.session.commit()

    # populate participants data by email: dict
    participants_dict_by_email = {}
    saved_participants = SurveyParticipantModel.query.filter_by(survey_id=survey.id).all()

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

    # remove non duplicate & save the duplicate data as list
    email_to_remove = []
    duplicate_data = []
    for email, data in participants_dict_by_email.items():
      if len(data) < 2:
        email_to_remove.append(email)
      else:
        duplicate_data += data

    for email in email_to_remove:
      del participants_dict_by_email[email]

    # if has duplicate, set survey status to DUPL, return with dupl data
    if len(participants_dict_by_email) > 0:

      # update survey status to DUPL
      survey.status = "DUPL"
      db.session.commit()

      return {
        "status": "duplicate",
        "duplicateParticipant": duplicate_data
      }

    return {
      "status": "draft",
    }