from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db

import os
import time

from text import extract_terms
from placemaker import geoparsing

questions = None
response_time = "*"
current_focus = "..."

class Question(db.Model):
    title = db.StringProperty()
    place_id = db.IntegerProperty()
    create_time = db.DateTimeProperty(auto_now_add=True)
    terms = db.StringListProperty()

class TermStats(db.Model):
    docfreq = db.IntegerProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        global questions
        global response_time
        global current_focus
        template_values = {
            'questions': questions,
            'current_focus': current_focus,
            'response_time': response_time
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        questions = None
        response_time = "*"
        current_focus = "..."

# def jaccard_coefficient(a,b):
#     c = [v for v in a if v in b]
#     return float(len(c))/(len(a)+len(b)-len(c))

def question_score(question, term_dict):
    score = 0.0
    for term in question.terms:
        if term in term_dict:
            score += (1.0+(1.0/(term_dict[term]+1.0)))**2
    score /= len(question.terms)
    return score

def find_relevant_questions(query):
    query_terms = extract_terms(query)
    # NOTE: 
    # the following code uses list-properties and merge-join to implement keyword search
    # but it leads to the problem of exploding index if len(query_terms) >= 2
    #
    # select_str = "SELECT * FROM Question WHERE"
    # where_str = " AND ".join([("terms = '%s'" % term) for term in query_terms])
    # order_str = "ORDER BY create_time DESC" # useful as sorted() is guaranteed to be stable
    # limit_str = "LIMIT 200"
    # questions = db.GqlQuery(select_str+" "+where_str+" "+order_str+" "+limit_str)
    #
    questions = []
    if query_terms:
        termstatses = TermStats.get_by_key_name(query_terms)
        term_dict = dict([(termstats.key().name(),termstats.docfreq) for termstats in termstatses if termstats])
        terms = sorted(term_dict.keys(),
                       key=lambda term: term_dict[term])
        best_terms = []
        k = 0
        for term in terms:
            k += 1
            if len(best_terms) < 1:
                best_terms.append(term)
            else:
                if (k <= 5) and (term_dict[term] <= 20):
                    best_terms.append(term)
        if best_terms:
            question_query = Question.all()
            question_query.filter("terms IN", best_terms)
            question_query.order("-create_time")
            questions = question_query.fetch(100) # the number of questions to be ranked
            if questions:
                questions.sort(key=lambda question: question_score(question,term_dict),
                               reverse=True)
            questions = questions[:10]
    return questions

class Find(webapp.RequestHandler):
    def post(self):
        global questions
        global response_time
        global current_focus
        t = time.time()
        query = self.request.get('question_title').strip()
        questions = find_relevant_questions(query)
        response_time = (time.time()-t)*1000
        current_focus = geoparsing(query)
        self.redirect('/')

def update_termstats(term_dict):
    terms = term_dict.keys()
    termstatses = TermStats.get_by_key_name(terms)
    for i in range(len(terms)):
        term = terms[i]
        more_docfreq = term_dict[term]
        if termstatses[i]:
            termstatses[i].docfreq += more_docfreq
        else:
            termstatses[i] = TermStats(key_name=term)
            termstatses[i].docfreq = more_docfreq
    db.put(termstatses)

class Ask(webapp.RequestHandler):
    def post(self):
        global questions
        global response_time
        global current_focus
        question = Question()
        question.title = self.request.get('question_title').strip()
        t = time.time()
        question.terms = extract_terms(question.title)
        if question.terms:
            question.put()
            term_dict = dict(zip(question.terms, [1]*len(question.terms)))
            update_termstats(term_dict)
        questions = None
        response_time = (time.time()-t)*1000
        current_focus = geoparsing(question.title)
        self.redirect('/')

from collections import defaultdict

class Load(webapp.RequestHandler):
    def post(self):
        title_list = self.request.get('questions_file').split('\n')
        questions = []
        term_dict = defaultdict(int)
        for title in title_list:
            title = title.strip()
            if not title:
                continue
            question = Question()
            question.title = title.decode('utf-8')
            question.terms = extract_terms(question.title)
            if not question.terms:
                continue
            questions.append(question)
            for term in question.terms:
                term_dict[term] += 1
        db.put(questions)
        update_termstats(term_dict)
        self.redirect('/')

class Clear(webapp.RequestHandler):
    def post(self):
        db.delete(Question.all(keys_only=True))
        db.delete(TermStats.all(keys_only=True))
        self.redirect('/')

import simplejson as json

class SearchAPI(webapp.RequestHandler):
    def get(self):
        query = self.request.get('query').strip()
        questions = find_relevant_questions(query)
        question_ids = [question.key().id() for question in questions]
        self.response.out.write(json.dumps(question_ids))

class QuestionAPI(webapp.RequestHandler):
    def get(self):
        pass

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
