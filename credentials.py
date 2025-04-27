client_id = 'Q7TT1GLXGL-500'
secret_key = 'IE7IMBGOP2I'
redirect_uri = 'https://www.google.com/'

user_name='BJ456793'
totp_key='QHZESTDG7S57GFCVI74JNGDP'
pin1 = "1"
pin2 = "6"
pin3 = "6"
pin4 = "7"

import pyotp as tp
t = tp.TOTP(totp_key).now()
print(t)
