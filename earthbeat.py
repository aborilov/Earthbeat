import os
import urllib
import datetime
import logging
logging.getLogger().setLevel(logging.DEBUG)

from google.appengine.api import users
from google.appengine.ext import db

import jinja2
import webapp2

import counter


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

openIdProviders = (
    'Gmail.com',  # shorter alternative: "Gmail.com"
    'Yahoo.com',
    'MySpace.com',
    'AOL.com',
    'MyOpenID.com',

    # add more here
)


class Mood(db.Model):
    mood = db.BooleanProperty(indexed=True)
    name = db.StringProperty(required=True)
    date = db.DateTimeProperty()


class User(db.Model):
    mood = db.BooleanProperty(indexed=True)
    name = db.StringProperty(required=True)
    date = db.DateTimeProperty()


class MainPage(webapp2.RequestHandler):

    def post(self):
        user = users.get_current_user()
        if user:
            user_id = user.user_id()
            mood = self.request.get("mood")
            if mood:
                if mood == "smile":
                    change_mood(user_id, True)
                else:
                    change_mood(user_id, False)
            self.redirect('/')

    def get(self):
        user = users.get_current_user()
        if user:
            template_values = {
                'user': user.nickname(),
            }
            mood = user_mood(user.user_id())
            if mood is None:
                template_values['mood'] = ""
            else:
                if mood:
                    template_values['mood'] = "happy"
                else:
                    template_values['mood'] = "sad"
            template_values['smile_count'] = counter.get_count("smile_count")
            template_values['cry_count'] = counter.get_count("cry_count")

            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_values))
        else:
            self.response.out.write('Hello world! Sign in at: ')
            for p in openIdProviders:
                p_name = p.split('.')[0]  # take "AOL" from "AOL.com"
                p_url = p.lower()        # "AOL.com" -> "aol.com"
                self.response.out.write('[<a href="%s">%s</a>]' % (
                    users.create_login_url(federated_identity=p_url), p_name))


def user_mood(user_id):
    q = db.Query(User).filter(
        "name", user_id).fetch(limit=1)
    if q and q[0].date.date() == datetime.datetime.now().date():
        return q[0].mood
    return None


def increment(mood):
    if mood:
        counter.increment("smile_count")
    else:
        counter.increment("cry_count")


def change_mood(user_id, mood):
    q = db.Query(User).filter(
        "name", user_id).fetch(limit=1)
    now = datetime.datetime.now()
    if q:
        user = q[0]
        if 1:  # user.mood != mood and user.date.date() != now.date():
            user.mood = mood
            user.date = now
            user.put()
            poll(user_id, mood)
            increment(mood)
    else:
        u = User(mood=mood,
                 name=user_id,
                 date=now)
        u.put()
        poll(user_id, mood)
        increment(mood)


def poll(user_id, mood):
    m = Mood(mood=mood,
             name=user_id,
             date=datetime.datetime.now())
    m.put()

application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
