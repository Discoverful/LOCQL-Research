from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import deferred

import os
import time
import simplejson as json

from placemaker import geoparsing
import locql

found_questions = None
response_time = "*"
current_focus = "..."

class MainPage(webapp.RequestHandler):
    def get(self):
        global found_questions
        global response_time
        global current_focus
        template_values = {
            'found_questions': found_questions,
            'current_focus': current_focus,
            'response_time': response_time
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        found_questions = None
        response_time = "*"
        current_focus = "..."

class Find(webapp.RequestHandler):
    def post(self):
        global found_questions
        global response_time
        global current_focus
        t = time.time()
        query = self.request.get('question_title').strip()
        found_questions = locql.find_relevant_questions(query)
        response_time = (time.time()-t)*1000
        current_focus = geoparsing(query)
        self.redirect('/')

class Ask(webapp.RequestHandler):
    def post(self):
        global response_time
        global current_focus
        t = time.time()
        question_title = self.request.get('question_title')
        locql.add_question(question_title)
        response_time = (time.time()-t)*1000
        current_focus = geoparsing(question_title)
        self.redirect('/')

class Load(webapp.RequestHandler):
    def post(self):
        question_titles = self.request.get('questions_file').split('\n')
        question_titles = [question_title.decode('utf-8') for question_title in question_titles]
        deferred.defer(locql.add_questions, question_titles)
        self.redirect('/')

class Clear(webapp.RequestHandler):
    def post(self):
        deferred.defer(locql.delete_all_questions)
        self.redirect('/')

class SearchAPI(webapp.RequestHandler):
    def get(self):
        query = self.request.get('query')
        place_ids = self.request.get('place_ids')
        if not place_ids:
            place_ids = []
        max_num = self.request.get('max_num')
        if not max_num:
            max_num = 10
        found_questions = locql.find_relevant_questions(query, place_ids, max_num)
        question_ids = [question.question_id for question in found_questions]  # key().id()
        self.response.out.write(json.dumps(question_ids))
        # self.error(404)  # not found

class QuestionAPI(webapp.RequestHandler):
    def delete(self):
        deferred.defer(locql.delete_all_questions)

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/find', Find),
                                      ('/ask', Ask),
                                      ('/load', Load),
                                      ('/clear', Clear),
                                      ('/search', SearchAPI),
                                      ('/question', QuestionAPI)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
