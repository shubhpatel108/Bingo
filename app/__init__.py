from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.pusher import Pusher

class MyServer(Flask):

    def __init__(self, *args, **kwargs):
            super(MyServer, self).__init__(*args, **kwargs)

            #instanciate your variables here
            self.game_state = "off"
            self.secs_remaining = 60
            self.announced_nums = []
            self.winner_id = None
            self.player_ids = []

app = MyServer(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)
lm = LoginManager(app)
lm.init_app(app)
lm.login_view = 'login'
pusher = Pusher(app)

from app import views, models
