import os
import urllib
import datetime
import logging
logging.getLogger().setLevel(logging.DEBUG)

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache

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

memcache.add(key="smile_count", value="0")
memcache.add(key="cry_count", value="0")


class Mood(db.Model):
    mood = db.BooleanProperty(indexed=True)
    name = db.StringProperty(required=True)
    date = db.DateTimeProperty()


class User(db.Model):
    mood = db.BooleanProperty(indexed=True)
    name = db.StringProperty(required=True)
    date = db.DateTimeProperty()


class MainPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            template_values = {
                'user': user.nickname(),
            }
            user_id = user.user_id()
            mood = None
            mood = self.request.get("mood")
            if mood:
                template_values["redirect"] = "/"
                if mood == "smile":
                    if change_mood(user_id, True):
                        mood = True
                        counter.increment("smile_count")
                        poll(user_id, True)
                    else:
                        mood = user_mood(user.user_id())
                else:
                    if change_mood(user_id, False):
                        mood = False
                        counter.increment("cry_count")
                        poll(user_id, False)
                    else:
                        mood = user_mood(user.user_id())
            else:
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
    if q:
        return q[0].mood
    else:
        return None


def change_mood(user_id, mood):
    q = db.Query(User).filter(
        "name", user_id).fetch(limit=1)
    now = datetime.datetime.now()
    if q:
        user = q[0]
        if user.mood != mood and user.date.date() != now.date():
            user.mood = mood
            user.date = now
            user.put()
            return True
    else:
        u = User(mood=mood,
                 name=user_id,
                 date=now)
        u.put()
        return True
    return False


def poll(user_id, mood):
    m = Mood(mood=mood,
             name=user_id,
             date=datetime.datetime.now())
    m.put()

application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
