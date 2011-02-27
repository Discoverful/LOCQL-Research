from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import deferred

import os
import time
from datetime import datetime
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
        query = self.request.get('query').strip()
        found_questions = locql.find_relevant_questions(query)
        response_time = (time.time()-t)*1000
        current_focus = geoparsing(query)
        self.redirect('/')

def create_test_question(title):
    jsonobj = [-1, title, time.time(), []]
    return jsonobj2question(jsonobj)

class Ask(webapp.RequestHandler):
    def post(self):
        global response_time
        global current_focus
        t = time.time()
        title = self.request.get('title')
        question = create_test_question(title)
        locql.add_question(question)
        response_time = (time.time()-t)*1000
        current_focus = geoparsing(title)
        self.redirect('/')

class Load(webapp.RequestHandler):
    def post(self):
        titles = self.request.get('questions_file').split('\n')
        titles = [title.decode('utf-8') for title in titles]
        questions = [create_test_question(title) for title in titles]
        deferred.defer(locql.add_questions, questions)
        self.redirect('/')

class Clear(webapp.RequestHandler):
    def post(self):
        deferred.defer(locql.delete_all_questions)
        self.redirect('/')

class SearchAPI(webapp.RequestHandler):
    def get(self):
        query = self.request.get('query')
        place_ids = json.loads(self.request.get('place_ids', default_value='[]'))
        max_num = self.request.get_range('max_num', default=10)
        if ((not query) or (len(query) > 200) or 
            (len(place_ids) > 20) 
            or (max_num < 1) or (max_num > 100)):
            self.error(400) # bad request
        else:
            found_questions = locql.find_relevant_questions(query, place_ids, max_num)
            question_ids = [question.question_id for question in found_questions]
            self.response.out.write(json.dumps(question_ids))

def jsonobj2question(jsonobj):
    if ((not jsonobj) or (len(jsonobj) < 4)):
        return
    question = locql.Question()
    question.question_id = jsonobj[0]
    question.title = jsonobj[1].strip()
    question.create_time = datetime.utcfromtimestamp(jsonobj[2])
    question.place_ids = jsonobj[3]
    if ((not question.question_id) or
        (not question.title) or
        (not question.create_time) or
        (len(question.place_ids) > 20)):
        return
    return question

def question2jsonobj(question):
    if not question:
        return []
    return [question.question_id, 
            question.title, 
            time.mktime(question.create_time.timetuple()), 
            question.place_ids]
    
class QuestionAPI(webapp.RequestHandler):
    def put(self):
        jsonobjs = json.loads(self.request.get('questions', default_value='[]'))
        questions = [jsonobj2question(jsonobj) for jsonobj in jsonobjs]
        if not questions:
            self.error(400)  # bad request
        elif len(questions) == 1:
            locql.add_question(questions[0])
        else:
            deferred.defer(locql.add_questions, questions)
    def delete(self):
        question_ids = json.loads(self.request.get('question_ids', default_value='[]'))
        if not question_ids:
            locql.delete_all_questions()
        elif len(question_ids) > 100:
            self.error(400)  # bad request
        elif len(question_ids) == 1:
            locql.delete_question(question_ids[0])
        else:
            deferred.defer(locql.delete_questions, question_ids)
    def get(self):
        question_ids = json.loads(self.request.get('question_ids', default_value='[]'))
        if (not question_ids) or (len(question_ids)>100):
            self.error(400)  # bad request
        else:
            questions = locql.get_questions(question_ids)
            jsonobjs = [question2jsonobj(question) for question in questions]
            self.response.out.write(json.dumps(jsonobjs))

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
