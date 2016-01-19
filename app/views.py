from __future__ import print_function
from flask import render_template, flash, redirect, url_for, g, request
from app import app, models, db, lm, pusher
from models import User
from .forms import LoginForm
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from oauth import OAuthSignIn
from random import randint
import time, sys, thread

@app.route('/')
@app.route('/index')
def index():
    global app
    players = []
    
    if app.game_state != 'off':
        players = [models.User.query.get(i).nickname for i in app.player_ids]

    return render_template("index.html",
                           title = 'Home',
                           players = players,
                           game_state = app.game_state)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
      return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
      flash('Login requested for OpenID="%s", remember_me=%s' %
            (form.openid.data, str(form.remember_me.data)))
      return redirect('/index')
    return redirect(url_for('index'))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.', 'error')
        return redirect(url_for('index'))
    user = models.User.query.filter_by(social_id=social_id).first()
    if not user:
        user = models.User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    flash('Successfully logged in.', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    flash('Successfully logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User %s not found.' % nickname, 'error')
        return redirect(url_for('index'))

    return render_template('user.html',
                           user=user)

@app.before_request
def before_request():
    g.user = current_user

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

from flask import jsonify

@app.route('/ajax', methods=['POST'])
@login_required
def translate():
    return jsonify({ 
        'score': 55 })


def reset_game():
    global app
    app.secs_remaining = 60
    app.game_state = 'off'
    app.announced_nums = []
    app.player_ids = []

def push_number(num):
    with app.app_context():
        client = pusher.client
        client.trigger('test_channel', 'event', {
            'message': num,
            })

def pusher_test():
    global app
    time.sleep(.1)
    numbers = [num for num in range(1,26)]
    length = 25

    for turn in range(1,26):
        num = numbers.pop(randint(0, length - 1))
        app.announced_nums.append(num)
        push_number(num)
        length -= 1
        time.sleep(3)

    with app.app_context():
        reset_game()
        client = pusher.client
        client.trigger('test_channel', 'game_over', {
            'winner': 'No-one',
            })

@app.route('/game')
@login_required
def play_game():
    if app.game_state != 'started':
        return redirect(url_for('new_game'))
    array = [i for i in range(1,26) ]
    return render_template('game.html',
                            array = array)

def start_timer():
    global app
    while app.secs_remaining > 0:
        time.sleep(1)
        app.secs_remaining -= 1

@app.route('/game/waiting')
@login_required
def new_game():
    global app

    if current_user.id not in app.player_ids:
        user = current_user
        user.played += 1
        app.player_ids.append(user.id)
        db.session.add(user)
        db.session.commit()

    if app.game_state == 'off':
        app.game_state = 'initialized'
        thread.start_new_thread( start_timer, () )
        return render_template('new_game.html',
                                secs_remaining = app.secs_remaining)
    elif app.game_state == 'initialized' and app.secs_remaining > 0:
        return render_template('new_game.html',
                                secs_remaining = app.secs_remaining)
    else:
        if app.game_state != 'started':
            app.game_state = 'started'
            app.secs_remaining = 0
            thread.start_new_thread(pusher_test, ())
        return redirect(url_for('play_game'))

@app.route('/game/over', methods=['POST'])
@login_required
def game_over():
    global app

    answers = request.form['data'].replace('[', ',').replace(']', ',').replace('"', ',').replace(',',' ').split()

    if app.game_state != 'started':
        return redirect(url_for('new_game'))

    for num in answers:
        if int(num) not in app.announced_nums:
            return jsonify({ 
                    'message': 'You tried to cheat!' })

    winner = current_user
    winner.wins += 1
    db.session.add(winner)
    db.session.commit()

    reset_game()
    client = pusher.client
    client.trigger('test_channel', 'game_over', {
        'winner': winner.nickname,
        })
