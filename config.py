WTF_CSRF_ENABLED = True
SECRET_KEY = 'something-new'

OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]


#config for Database
import os
basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

#Omniauth Credentials
OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '1701929076760729',
        'secret': 'f6d11f6f85ea650b06715c28e0bbf0a2'
    }
}

#Pusher Credentials
PUSHER_APP_ID = '171174'
PUSHER_KEY = '6728e7a78ff504f3b8b0'
PUSHER_SECRET = '21006147abc41de552b6'