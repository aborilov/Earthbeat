import os
import urllib
import datetime

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
    mood = db.StringProperty(indexed=True)
    name = db.StringProperty(required=True)
    date = db.DateProperty()

class MainPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            template_values = {
                'user': user.nickname(),
            }
            mood = self.request.get('mood')
            if mood:
                template_values['mood'] = mood
                if mood == "cry":
                    counter.increment("cry_count")
                else:
                    counter.increment("smile_count")
                # m = Mood(mood=mood,
                #          name=user.user_id(),
                #          date=datetime.datetime.now().date())
                # m.put()
            else:
                template_values['mood'] = ""

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

    def post(self):
        return self.get()


class SmileCounter(webapp2.RequestHandler):

    def get(self):
        self.response.write(counter.get_count("smile_count"))


class CryCounter(webapp2.RequestHandler):

    def get(self):
        self.response.write(counter.get_count("cry_count"))


class SmileCounterInc(webapp2.RequestHandler):

    def get(self):
        counter.increment("smile_count")
        self.response.write(counter.get_count("smile_count"))


class CryCounterInc(webapp2.RequestHandler):

    def get(self):
        counter.increment("cry_count")
        self.response.write(counter.get_count("cry_count"))


class SmileCounterDec(webapp2.RequestHandler):

    def get(self):
        counter.increment("smile_count")
        self.response.write(counter.get_count("smile_count"))


class CryCounterDec(webapp2.RequestHandler):

    def get(self):
        counter.increment("cry_count")
        self.response.write(counter.get_count("cry_count"))

application = webapp2.WSGIApplication([
    ('/smile', SmileCounter),
    ('/cry', CryCounter),
    ('/smile_inc', SmileCounterInc),
    ('/cry_inc', CryCounterInc),
    ('/smile_dec', SmileCounterDec),
    ('/cry_dec', CryCounterDec),
    ('/', MainPage),
], debug=True)
