from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import deferred

import os
import time
from datetime import datetime
import simplejson as json

from placemaker import annotate_places
import locql

relevant_questions = None
response_time = "*"
current_focus = "..."

class MainPage(webapp.RequestHandler):
    def get(self):
        global relevant_questions
        global response_time
        global current_focus
        template_values = {
            'relevant_questions': relevant_questions,
            'current_focus': current_focus,
            'response_time': response_time
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        relevant_questions = None
        response_time = "*"
        current_focus = "..."

class Find(webapp.RequestHandler):
    def post(self):
        global relevant_questions
        global response_time
        global current_focus
        t = time.time()
        query = self.request.get('query').strip()
        relevant_questions = locql.find_relevant_questions(query)
        response_time = (time.time()-t)*1000
        current_focus = annotate_places(query)
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
        locql.create_question(question)
        response_time = (time.time()-t)*1000
        current_focus = annotate_places(title)
        self.redirect('/')

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

class Load(webapp.RequestHandler):
    def post(self):
        titles = self.request.get('questions_file').split('\n')
        titles = [title.decode('utf-8') for title in titles]
        questions = [create_test_question(title) for title in titles]
        for chunk in chunks(questions, 50):
            deferred.defer(locql.create_questions, chunk)
        self.redirect('/')

class Clear(webapp.RequestHandler):
    def post(self):
        locql.delete_all_questions()
        self.redirect('/')

class SearchAPI(webapp.RequestHandler):
    def get(self):
        query = self.request.get('query')
        place_ids = json.loads(self.request.get('place_ids', default_value='[]'))
        max_num = self.request.get_range('max_num', default=10)
        with_titles = self.request.get_range('with_titles', default=0)
        if ((not query) or (len(query) > 200) or 
            (len(place_ids) > 20) or 
            (max_num < 1) or (max_num > 50)):
            self.error(400) # bad request
        else:
            relevant_questions = locql.find_relevant_questions(query, place_ids, max_num)
            if not with_titles:
                search_results = [question.question_id for question in relevant_questions]
            else:
                search_results = [(question.question_id,question.title) for question in relevant_questions]
            self.response.out.write(json.dumps(search_results))

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
    def post(self):
        jsonobj = json.loads(self.request.get('question', default_value='[]'))
        question = jsonobj2question(jsonobj)
        if not question:
            self.error(400)  # bad request
        operation = self.request.get('operation', default_value='create')
        if operation == 'create':
            if locql.create_question(question):
                self.response.set_status(200)  # success
            else:
                self.error(400)  # failure
        elif operation == 'delete':
            if locql.delete_question(question):
                self.response.set_status(201)  # success
            else:
                self.error(400)  # failure
        else:
            self.error(400)  # bad request
    def delete(self):
        locql.delete_all_questions()
    def get(self):
        question_ids = json.loads(self.request.get('question_ids', default_value='[]'))
        if (not question_ids) or (len(question_ids)>50):
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
