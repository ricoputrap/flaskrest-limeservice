from flask import request, make_response
from flask_restful import Resource

from project.services.participant import ParticipantService

class Participant(Resource):

    participant_service = ParticipantService()

    def get(self, survey_id):
        try:
            path_splitted = request.path.split("/")
            last_endpoint = path_splitted[-1]

            if last_endpoint == "duplicates":
                response = self.participant_service.get_duplicates_in_limeservice_db(survey_id)
            else:
                page = request.args.get("page")
                pageSize = request.args.get("pageSize")
                response = self.participant_service.get_list_participants(survey_id, page, pageSize)
                
            if "error" in response:
                return make_response(response, response["status_code"])
            return response

        except Exception as e:
            return {
                "errors": e
            }
    
    def post(self, survey_id):
        try:
            path_splitted = request.path.split("/")
            post_type = path_splitted[-1]
            
            if post_type == "csv":
                csv_file = request.files['csvFile']
                file_type = csv_file.__dict__['filename'][-3:]
                
                if file_type == "csv":
                    response = self.participant_service.add_participants_from_csv(survey_id, csv_file)
                    if "error" in response:
                        return make_response(response, response["status_code"])
                    return response
                else:
                    res = {
                        "status_code": 400,
                        "error": {
                            "title": "Incorrect Format",
                            "detail": "Please upload the correct `.csv` file"
                        }
                    }
                    return make_response(res, res["status_code"])
            elif post_type == "db":
                params = request.get_json()
                response = self.participant_service.add_participants_from_atlas_db(survey_id, params)
                if "error" in response:
                    return make_response(response, response["status_code"])
                return response
            else:
                res = {
                    "status_code": 500,
                    "error": {
                        "title": "Upload Method Now Known",
                        "detail": "Use `csv` or `db` only for uploading participants data."
                    }
                }
                return make_response(res, res["status_code"])
        except Exception as e:
            return {
                "errors": e
            }
    
    def delete(self, survey_id):
        try:
            request_body = request.get_json()
            ids = request_body["ids"] if "ids" in request_body else ""
            if not ids:
                res = {
                    "status_code": 400,
                    "error": {
                        "title": "Bad Request",
                        "detail": "Please provide a list of participant ids you want to be deleted"
                    }
                }
                return make_response(res, res["status_code"])
            
            response = self.participant_service.delete_participants(survey_id, ids)
            if "error" in response:
                return make_response(response, response["status_code"])
            return response
        except Exception as e:
            return {
                "errors": e
            }