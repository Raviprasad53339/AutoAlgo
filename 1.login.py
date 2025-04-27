import credentials as crs
from fyers_apiv3 import fyersModel
import webbrowser

# Replace these values with your actual API credentials
client_id = crs.client_id
secret_key = crs.secret_key
redirect_uri = crs.redirect_uri
response_type = "code"  
state = "sample_state"

# Create a session model with the provided credentials
session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type=response_type
)

# Generate the auth code using the session model
response = session.generate_authcode()

# Print the auth code received in the response
print(response)

webbrowser.open(response,new=1)

#response_link='https://www.google.com/?s=ok&code=200&auth_code=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkubG9naW4uZnllcnMuaW4iLCJpYXQiOjE3MzE4MjI3MDYsImV4cCI6MTczMTg1MjcwNiwibmJmIjoxNzMxODIyMTA2LCJhdWQiOiJbXCJ4OjBcIiwgXCJ4OjFcIiwgXCJ4OjJcIiwgXCJkOjFcIiwgXCJkOjJcIiwgXCJ4OjFcIiwgXCJ4OjBcIl0iLCJzdWIiOiJhdXRoX2NvZGUiLCJkaXNwbGF5X25hbWUiOiJYUjI5MTMxIiwib21zIjoiSzEiLCJoc21fa2V5IjoiNDljN2Y4ZDk3MTkxZmNkNWRiOTNmYjFmODEzOTZkMjVhNDU2YmQ5ZTM1YTMzODQwYzMwNGZiNDQiLCJub25jZSI6IiIsImFwcF9pZCI6IlE3VFQxR0xMVUgiLCJ1dWlkIjoiMGZiZTIyMDQ5MGE5NDhkZDlmZjBmNWQyMmNjZjVkNjIiLCJpcEFkZHIiOiIwLjAuMC4wIiwic2NvcGUiOiIifQ.Tr8jrwd-TVnzLC678bXel3biyUiByebV2xnM46OhVHM&state=None'

newurl = input("Enter the url: ")
auth_code = newurl[newurl.index('auth_code=')+10:newurl.index('&state')]
print(auth_code)

grant_type = "authorization_code" 
session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key, 
    redirect_uri=redirect_uri, 
    response_type=response_type, 
    grant_type=grant_type
)

# Set the authorization code in the session object
session.set_token(auth_code)

# Generate the access token using the authorization code
response = session.generate_token()

# Print the response, which should contain the access token and other details
print(response)

# There can be two cases over here you can successfully get the acccessToken over the request or you might get some error over here. so to avoid that have this in try except block
try: 
    access_token = response["access_token"]
    with open('access.txt','w') as k:
        k.write(access_token)
except Exception as e:
    print(e,response)  ## This will help you in debugging then and there itself like what was the error and also you would be able to see the value you got in response variable. instead of getting key_error for unsuccessfull response.
 