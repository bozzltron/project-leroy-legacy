
from twython import Twython

# generate your own auth.py file with credentials
from auth import (
    app_key,
    app_key_secret,
    oauth_token,
    oauth_token_secret
)

image = open('storage/img-0185591144.png', 'rb')
twitter = Twython(app_key, app_key_secret,
                  oauth_token, oauth_token_secret)
response = twitter.upload_media(media=image)
media_id = [response['media_id']]
#logging.info('media id : %s', response['media_id'])
twitter.update_status(status='One of the best shots today.', media_ids=media_id)