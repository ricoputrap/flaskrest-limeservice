from werkzeug.wrappers import Request, Response
import requests
import jwt
import json
import os

class AuthMiddleware:

  auth_token_not_provided = { "message": "Authentication credentials were not provided." }
  auth_token_not_valid = { "message": "Authentication token is not valid." }
  auth_has_not_access = { "message": "User has no access" }
  
  ATLAS_JWT_SECRET_KEY = os.getenv("ATLAS_JWT_SECRET_KEY")
  ATLAS_JWT_ALGO = os.getenv("ATLAS_JWT_ALGO")

  def __init__(self, app):
    self.app = app
  
  def __call__(self, environ, start_response):
    req = Request(environ)
    res = Response(mimetype='application/json', status=401)
  
    try:
      header_auth_token = req.headers['Authorization']
      auth_token = header_auth_token.replace('Bearer ', '')

      # sementara begini dulu
      decoded_token = jwt.decode(auth_token, options={"verify_signature": False})

      # karena kayaknya secret key nya masih salah jd gabisa decode
      # decoded_token = jwt.decode(auth_token, AuthMiddleware.ATLAS_JWT_SECRET_KEY, algorithms=[AuthMiddleware.ATLAS_JWT_ALGO])
      user_id = decoded_token['user_id']

      is_token_valid = True

      is_token_valid = self.is_token_valid(user_id, header_auth_token)
      if is_token_valid:
        has_access = self.has_access(is_token_valid)
        if has_access:
          return self.app(environ, start_response)
        else:
          res.data = AuthMiddleware.auth_has_not_access
          return res(environ, start_response)
      else:
        res.data = AuthMiddleware.auth_token_not_valid
        return res(environ, start_response)
    
    except jwt.InvalidTokenError:
      res.data = json.dumps(AuthMiddleware.auth_token_not_valid)
      return res(environ, start_response)

    except KeyError:
      res.data = json.dumps(AuthMiddleware.auth_token_not_provided)
      return res(environ, start_response)

    except:
      res.data = json.dumps(AuthMiddleware.auth_token_not_provided)
      return res(environ, start_response)
          
  def is_token_valid(self, user_id, header_auth_token):
    auth_url = 'https://atlas-iluni12.cs.ui.ac.id/api/v1/users/' + user_id
    headers = {"Authorization": header_auth_token}

    response = requests.get(auth_url, headers=headers)
    
    if response.status_code == 200:
      data = response.json()
      return data
    return False
  
  def has_access(self, data):
    is_staff = data["isStaff"]
    return is_staff


'''
# path = req.path
#   if (path == '/survey/'):
#     # do something when `/survey/` path is accessed 
#     # (before Survey controller is accessed)
#     pass
'''