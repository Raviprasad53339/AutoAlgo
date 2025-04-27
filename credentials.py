client_id = 'Q7TT1GLLUH-100'
secret_key = 'IE7ISPCG2I'
redirect_uri = 'https://www.google.com/'

user_name='XR29131'
totp_key='QHZESTDG7SLU543UDIPALCR3MKF7H7YQ'
pin1 = "9"
pin2 = "6"
pin3 = "5"
pin4 = "3"

import pyotp as tp
t = tp.TOTP(totp_key).now()
print(t)
