import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from openid import LoginPage

import jinja2
import webapp2


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


class MainPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            template_values = {
                'user': user.nickname(),
            }

            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_values))
        else:
            self.response.out.write('Hello world! Sign in at: ')
            for p in openIdProviders:
                p_name = p.split('.')[0]  # take "AOL" from "AOL.com"
                p_url = p.lower()        # "AOL.com" -> "aol.com"
                self.response.out.write('[<a href="%s">%s</a>]' % (
                    users.create_login_url(federated_identity=p_url), p_name))


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/login', LoginPage),
], debug=True)
