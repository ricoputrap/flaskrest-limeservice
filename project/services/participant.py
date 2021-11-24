from flask import request
from project.models.survey_participant import SurveyParticipantModel
from project.models.survey import SurveyModel
from project.clients.limesurvey.api import LimesurveyClient
from project.utils import db
from project.services.helpers import check_if_survey_exists, \
	save_participants_to_limeservice_db, extract_participants_from_csv, \
	get_participants_from_limeservice_db_by_email, \
	remove_duplicate_participants_inplace, \
	extract_angkatan_and_jurusan_in_params, \
	extract_participants_from_atlas_db

import math
import requests

class ParticipantService:

	client = LimesurveyClient()

	def get_list_participants(self, limesurvey_id, page, pageSize):

		# check if survey exists
		res = check_if_survey_exists(limesurvey_id)
		if "error" in res:
			return res["error"]

		survey = res["data"]

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
					"detail": "Page " + str(page) + " is requested, only " + 
							str(real_total_pages) + " is available."
				}
			}

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

	def add_participants_from_csv(self, limesurvey_id, csv_file):

		# check if survey exists
		res = check_if_survey_exists(limesurvey_id)
		if "error" in res:
			return res["error"]

		survey = res["data"]
		survey_creator_id = self.client.get_survey_properties(limesurvey_id)['owner_id']

		# extract participants data 
		res = extract_participants_from_csv(csv_file)
		if "error" in res:
			return res["error"]
		submitted_participants = res["data"]
		
		# save, populate the saved participants by email, and remove duplicates
		save_participants_to_limeservice_db(survey, survey_creator_id, submitted_participants)
		participants_dict_by_email = get_participants_from_limeservice_db_by_email(survey.id)
		remove_duplicate_participants_inplace(participants_dict_by_email)

		# if has duplicate, set survey status to DUPL, return with dupl data
		if len(participants_dict_by_email) > 0:
			
			# update survey status to DUPL
			survey.status = "DUPL"
			db.session.commit()

			return {
				"status": "duplicate",
				"duplicateParticipant": participants_dict_by_email
			}

		return { "status": "draft" }


	def get_participants_from_atlas_db(self, params):
		"""
		Retrieve participants data from atlas database
		"""
		res = extract_angkatan_and_jurusan_in_params(params)
		if "error" in res:
			return res["error"]
		
		angkatan = res["data"][0]
		jurusan = res["data"][1]

		headers = {
			"Authorization": request.headers['Authorization'],
			"Accept": "application/json"
		}
		
		atlas_users_url = 'https://atlas-iluni12.cs.ui.ac.id/api/v2/users?'
		if angkatan:
			atlas_users_url += "year=" + angkatan + "&"
		if jurusan:
			atlas_users_url += "program=" + jurusan

		try:
			response = requests.get(atlas_users_url, headers=headers)
			if response.status_code == 200:
				data = response.json()
				users = data["results"]
				return users
			return {
				"status_code": response.status_code,
				"error": {
					"title": "Internal server error",
					"detail": "Internal server error"
				}
			}  
		except Exception as e:
			return {
				"status_code": 500,
				"error": {
					"title": "Internal server error",
					"detail": e
				}
			} 

		
	def add_participants_from_atlas_db(self, limesurvey_id, params):
		"""
		Retrieve participants data from atlas database and save it to limeservice db
		"""

		# check if survey exists
		res = check_if_survey_exists(limesurvey_id)
		if "error" in res:
			return res["error"]

		survey = res["data"]
		survey_creator_id = self.client.get_survey_properties(limesurvey_id)['owner_id']

		# result: retrieve users data from atlas db
		result = self.get_participants_from_atlas_db(params)

		if "error" in result:
			return result
		
		# computed_users: compute the result to be a list of users data: { name, email, npm, angkatan }
		submitted_participants = extract_participants_from_atlas_db(result)

		# save participants to limeservice db
		save_participants_to_limeservice_db(survey, survey_creator_id, submitted_participants)

		# populate participants data by email (as a dictionary)
		participants_dict_by_email = get_participants_from_limeservice_db_by_email(survey.id)
		remove_duplicate_participants_inplace(participants_dict_by_email)

		# if has duplicate, set survey status to DUPL, return with dupl data: `duplicateParticipant`
		if len(participants_dict_by_email) > 0:
			
			# update survey status to DUPL
			survey.status = "DUPL"
			db.session.commit()

			return {
				"status": "duplicate",
				"duplicateParticipant": participants_dict_by_email
			}

		return { "status": "draft" }
