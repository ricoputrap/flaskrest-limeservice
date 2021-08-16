from project.utils import ma

class ActivitySchema(ma.Schema):
  class Meta:
    fields = ("id", "survey_id", "activity_type", "description",
      "additional_data", "created_at", "created_by")