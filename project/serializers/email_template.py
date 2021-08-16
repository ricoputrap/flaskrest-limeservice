from project.utils import ma

class EmailTemplateSchema(ma.Schema):
  class Meta:
    fields = ("id", "name", "subject", "body")