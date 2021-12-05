from project.models.email_template import EmailTemplateModel
from project.services.helpers import validate_email_template
from project.utils import db

class EmailTemplateService:

    def create_email_template(self, req_body):

        res = validate_email_template(req_body)
        if "error" in res:
            return res
        
        # extract the values
        name = res["name"]
        subject = res["subject"]
        body = res["body"]
        
        # if name already exists
        email_template = EmailTemplateModel.query.filter_by(name=name).first()
        if email_template:
            return {
                "status_code": 400,
                "error": {
                    "title": "Duplicate Template Name",
                    "detail": "The template name already exists"
                }
            }
        
        # save the new template
        new_email_template = EmailTemplateModel(
            name = name,
            subject = subject,
            body = body
        )
        db.session.add(new_email_template)
        db.session.commit()

        # return success response
        return {
            "id": new_email_template.id,
            "name": name,
            "subject": subject,
            "body": body,
        }

    def update_email_template(self, req_body):
        id = req_body["id"] if "id" in req_body else ""
        email_template = EmailTemplateModel.query.filter_by(id=id).first()
        if not email_template:
            return {
                "status_code": 404,
                "error": {
                    "title": "Email Template Not Found",
                    "detail": "Email template with id " + str(id) + " is not found"
                }
            }

        name = req_body["name"] if "name" in req_body else ""
        subject = req_body["subject"] if "subject" in req_body else ""
        body = req_body["body"] if "body" in req_body else ""

