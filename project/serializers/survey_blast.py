from project.utils import ma

class SurveyBlastSchema(ma.Schema):
  class Meta:
    fields = ("id", "survey_id", "channel", "status",
      "created_at", "created_by", "updated_at", "updated_by")