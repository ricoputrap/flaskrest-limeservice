from flask_restful import Resource

class Survey(Resource):

  def get(self):
    return {
      'data': [
        {
          'id': 0,
          'name': 'Survey XYZ'
        },
        {
          'id': 1,
          'name': 'Survey XYZ'
        },
        {
          'id': 2,
          'name': 'Survey XYZ'
        },
        {
          'id': 3,
          'name': 'Survey XYZ'
        }
      ]
    }