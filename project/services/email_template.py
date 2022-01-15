from werkzeug.wrappers import response
from project.models.email_template import EmailTemplateModel
from project.services.helpers import validate_email_template
from project.utils import db
import math


class EmailTemplateService:

    def get_email_templates(self, page, pageSize, keyword):
        
        # prepare the parameter values
        page = int(page) if page else 1
        pageSize = int(pageSize) if pageSize else 5

        # filter the email by keyword (if any)
        email_templates_in_db = EmailTemplateModel.query.all()
        if keyword:
            email_templates_in_db = list(filter(
                lambda template: keyword.lower() in template.name.lower(),
                email_templates_in_db
            ))

            if len(email_templates_in_db) == 0:
                return {
                    "status_code": 404,
                    "error": {
                        "title": "Keyword doesn't match",
                        "detail": "Keyword doesn't match with the available template names"
                    }
                }

        # compute the pagination
        real_total_templates = len(email_templates_in_db)
        real_total_pages = math.ceil(real_total_templates / pageSize)

        if page > real_total_pages:
            return {
                "status_code": 404,
                "error": {
                    "title": "Page requested is not available",
                    "detail": "Page " + str(page) + " is requested, only " + str(real_total_pages) + " is available."
                }
            }
        
        email_templates = []
        end_idx = page * pageSize
        end_idx = end_idx if end_idx <= real_total_templates else real_total_templates
        start_idx = pageSize * (page - 1)

        # populate the data based on the pagination
        for i in range(start_idx, end_idx):
            email_templates.append({
                "id": email_templates_in_db[i].id,
                "name": email_templates_in_db[i].name,
                "subject": email_templates_in_db[i].subject,
                "body": email_templates_in_db[i].body,
            })
        
        response = {
            "currentPage": page,
            "totalItems": real_total_templates,
            "items": email_templates
        }
        return response

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
