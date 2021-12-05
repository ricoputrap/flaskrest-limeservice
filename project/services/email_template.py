from project.models.email_template import EmailTemplateModel
from project.utils import db

class EmailTemplateService:

    def create_email_template(self, req_body):
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