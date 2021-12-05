from flask import request, make_response
from flask_restful import Resource

from project.services.email_template import EmailTemplateService


class EmailTemplate(Resource):

    email_template_service = EmailTemplateService()

    def get(self):
        pass

    def post(self):
        try:
            req_body = request.get_json()
            response = self.email_template_service.create_email_template(req_body)
            if "error" in response:
                return make_response(response, response["status_code"])
            return response
        except Exception as e:
            return {
                "errors": e
            }

    def put(self):
        try:
            req_body = request.get_json()
            response = self.email_template_service.update_email_template(req_body)
            if "error" in response:
                return make_response(response, response["status_code"])
            return response
        except Exception as e:
            return {
                "errors": e
            }