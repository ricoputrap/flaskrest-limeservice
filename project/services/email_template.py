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

        # check if email template exists
        id = req_body["id"] if "id" in req_body else ""
        if not id:
            return {
                "status_code": 400,
                "error": {
                    "title": "Bad Request",
                    "detail": "Missing the value of `id` to retrieve the email template object in database"
                }
            }

        email_template = EmailTemplateModel.query.filter_by(id=id).first()
        if not email_template:
            return {
                "status_code": 404,
                "error": {
                    "title": "Email Template Not Found",
                    "detail": "Email template with id " + str(id) + " is not found"
                }
            }
        
        res = { "id": id }

        name = req_body["name"] if "name" in req_body else ""
        if name:
            # check if name already exists
            email_template_by_name = EmailTemplateModel.query.filter_by(name=name).first()
            if email_template_by_name and email_template_by_name.id != id:
                return {
                    "status_code": 400,
                    "error": {
                        "title": "Duplicate Template Name",
                        "detail": "The template name already exists"
                    }
                }
            email_template.name = name
            res["name"] = name
        
        
        subject = req_body["subject"] if "subject" in req_body else ""
        if subject:
            email_template.subject = subject
            res["subject"] = subject
        
        body = req_body["body"] if "body" in req_body else ""
        if body:
            email_template.body = body
            res["body"] = body
        
        db.session.commit()
        return res
