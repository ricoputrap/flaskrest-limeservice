from werkzeug.wrappers import Request, Response
import requests
import jwt
import json

class AuthMiddleware:

  auth_token_not_provided = { "message": "Authentication credentials were not provided." }
  auth_token_not_valid = { "message": "Authentication token is not valid." }

  def __init__(self, app):
    self.app = app
  
  def __call__(self, environ, start_response):
    req = Request(environ)
    res = Response(mimetype='application/json', status=401)
  
    try:
      header_auth_token = req.headers['Authorization']
      auth_token = header_auth_token.replace('Bearer ', '')
      decoded_token = jwt.decode(auth_token, options={"verify_signature": False})
      user_id = decoded_token['user_id']

      is_token_valid = self.is_token_valid(user_id, header_auth_token)
      if is_token_valid:
        return self.app(environ, start_response)
      else:
        res.data = self.auth_token_not_valid
        return res(environ, start_response)
    
    except jwt.InvalidTokenError:
      res.data = json.dumps(self.auth_token_not_valid)
      return res(environ, start_response)

    except KeyError:
      res.data = json.dumps(self.auth_token_not_provided)
      return res(environ, start_response)

    except:
      res.data = json.dumps(self.auth_token_not_provided)
      return res(environ, start_response)
          
  def is_token_valid(self, user_id, header_auth_token):
    auth_url = 'https://atlas-iluni12.cs.ui.ac.id/api/v1/users/' + user_id
    headers = {"Authorization": header_auth_token}

    response = requests.get(auth_url, headers=headers)
    if response.status_code == 200:
      return True
    return False

'''
# path = req.path
#   if (path == '/survey/'):
#     # do something when `/survey/` path is accessed 
#     # (before Survey controller is accessed)
#     pass
'''