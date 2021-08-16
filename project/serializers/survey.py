from project.utils import ma

class SurveySchema(ma.Schema):
  class Meta:
    fields = ("id", "limesurvey_id", "status",
      "created_at", "created_by", "updated_at", "updated_by")