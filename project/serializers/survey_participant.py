from project.utils import ma

class SurveyParticipantSchema(ma.Schema):
  class Meta:
    fields = ("id", "survey_id", "name", "email",
      "npm", "batch_year", "major",
      "created_at", "created_by", 
      "updated_at", "updated_by")