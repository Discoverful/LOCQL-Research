from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users

#import cgi
import os

STOP_WORDS = frozenset((
"a", "a's", "able", "about", "above", "according", "accordingly", "across", "actually", "after", "afterwards", "again", "against", "ain't", "all", "allow", "allows", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "an", "and", "another", "any", "anybody", "anyhow", "anyone", "anything", "anyway", "anyways", "anywhere", "apart", "appear", "appreciate", "appropriate", "are", "aren't", "around", "as", "aside", "ask", "asking", "associated", "at", "available", "away", "awfully", 
"b", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "both", "brief", "but", "by", 
"c", "c'mon", "c's", "came", "can", "can't", "cannot", "cant", "cause", "causes", "certain", "certainly", "changes", "clearly", "co", "com", "come", "comes", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "could", "couldn't", "course", "currently", 
"d", "definitely", "described", "despite", "did", "didn't", "different", "do", "does", "doesn't", "doing", "don't", "done", "down", "downwards", "during", 
"e", "each", "edu", "eg", "eight", "either", "else", "elsewhere", "enough", "entirely", "especially", "et", "etc", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", 
"f", "far", "few", "fifth", "first", "five", "followed", "following", "follows", "for", "former", "formerly", "forth", "four", "from", "further", "furthermore", 
"g", "get", "gets", "getting", "given", "gives", "go", "goes", "going", "gone", "got", "gotten", "greetings", 
"h", "had", "hadn't", "happens", "hardly", "has", "hasn't", "have", "haven't", "having", "he", "he's", "hello", "help", "hence", "her", "here", "here's", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "hi", "him", "himself", "his", "hither", "hopefully", "how", "howbeit", "however", 
"i", "i'd", "i'll", "i'm", "i've", "ie", "if", "ignored", "immediate", "in", "inasmuch", "inc", "indeed", "indicate", "indicated", "indicates", "inner", "insofar", "instead", "into", "inward", "is", "isn't", "it", "it'd", "it'll", "it's", "its", "itself", 
"j", "just", 
"k", "keep", "keeps", "kept", "know", "knows", "known", 
"l", "last", "lately", "later", "latter", "latterly", "least", "less", "lest", "let", "let's", "like", "liked", "likely", "little", "look", "looking", "looks", "ltd", 
"m", "mainly", "many", "may", "maybe", "me", "mean", "meanwhile", "merely", "might", "more", "moreover", "most", "mostly", "much", "must", "my", "myself", 
"n", "name", "namely", "nd", "near", "nearly", "necessary", "need", "needs", "neither", "never", "nevertheless", "new", "next", "nine", "no", "nobody", "non", "none", "noone", "nor", "normally", "not", "nothing", "novel", "now", "nowhere", 
"o", "obviously", "of", "off", "often", "oh", "ok", "okay", "old", "on", "once", "one", "ones", "only", "onto", "or", "other", "others", "otherwise", "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "own", 
"p", "particular", "particularly", "per", "perhaps", "placed", "please", "plus", "possible", "presumably", "probably", "provides", 
"q", "que", "quite", "qv", 
"r", "rather", "rd", "re", "really", "reasonably", "regarding", "regardless", "regards", "relatively", "respectively", "right", 
"s", "said", "same", "saw", "say", "saying", "says", "second", "secondly", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "shall", "she", "should", "shouldn't", "since", "six", "so", "some", "somebody", "somehow", "someone", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "specified", "specify", "specifying", "still", "sub", "such", "sup", "sure", 
"t", "t's", "take", "taken", "tell", "tends", "th", "than", "thank", "thanks", "thanx", "that", "that's", "thats", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "there's", "thereafter", "thereby", "therefore", "therein", "theres", "thereupon", "these", "they", "they'd", "they'll", "they're", "they've", "think", "third", "this", "thorough", "thoroughly", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "took", "toward", "towards", "tried", "tries", "truly", "try", "trying", "twice", "two", 
"u", "un", "under", "unfortunately", "unless", "unlikely", "until", "unto", "up", "upon", "us", "use", "used", "useful", "uses", "using", "usually", "uucp", 
"v", "value", "various", "very", "via", "viz", "vs", 
"w", "want", "wants", "was", "wasn't", "way", "we", "we'd", "we'll", "we're", "we've", "welcome", "well", "went", "were", "weren't", "what", "what's", "whatever", "when", "whence", "whenever", "where", "where's", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "who's", "whoever", "whole", "whom", "whose", "why", "will", "willing", "wish", "with", "within", "without", "won't", "wonder", "would", "would", "wouldn't", 
"x", 
"y", "yes", "yet", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves", 
"z", "zero"
))
import re
splitter=re.compile(r'\W+')
from porter import stem
def text2terms(text):
    term_list = [stem(term)
                 for term in splitter.split(text.lower()) 
                 if ((len(term)>1) and (term not in STOP_WORDS))]
    return frozenset(term_list)

import time
response_time = 0

questions = None

class Question(db.Model):
    author = db.UserProperty()
    content = db.StringProperty()
    terms = db.StringListProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class TermStats(db.Model):
    term = db.StringProperty()
    docfreq = db.IntegerProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        global questions
        global response_time
        if questions == None:
            question_query = Question.all()
            question_query.order("-date")
            questions = question_query.fetch(10)
        template_values = {
            'url': url,
            'url_linktext': url_linktext,
            'questions': questions,
            'response_time': response_time
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        questions = None
        response_time = 0

# def jaccard_coefficient(a,b):
#     c = [v for v in a if v in b]
#     return float(len(c))/(len(a)+len(b)-len(c))

def question_score(question, term_dict):
    score = 0
    for term in question.terms:
        if term in term_dict:
            score += 1+(1/(term_dict[term]+1))
    return score

class Search(webapp.RequestHandler):
    def post(self):
        question_content = self.request.get('content').strip()
        global response_time
        t = time.time()
        query_terms = text2terms(question_content)
        global questions
        questions = []
        # NOTE: 
        # the following code uses list-properties and merge-join to implement keyword search
        # but it leads to the problem of exploding index if len(query_terms) >= 2
        #
        # select_str = "SELECT * FROM Question WHERE"
        # where_str = " AND ".join([("terms = '%s'" % term) for term in query_terms])
        # order_str = "ORDER BY date DESC" # useful as sorted() is guaranteed to be stable
        # limit_str = "LIMIT 200"
        # questions = db.GqlQuery(select_str+" "+where_str+" "+order_str+" "+limit_str)
        #
        if query_terms:
            termstats_query = TermStats.all()
            termstats_query.filter("term IN", list(query_terms))
            termstats_query.order("docfreq")
            termstatses = termstats_query.fetch(200)
            best_terms = []
            term_dict = {}
            for termstats in termstatses:
                if not best_terms:
                    best_terms.append(termstats.term)
                else:
                    if termstats.docfreq <= 10:
                        best_terms.append(termstats.term)
                term_dict[termstats.term] = termstats.docfreq
            if best_terms:
                question_query = Question.all()
                question_query.filter("terms IN", best_terms)
                question_query.order("-date")
                questions = question_query.fetch(50)
                questions = sorted(questions,
                                   key=lambda question: question_score(question,term_dict),
                                   reverse=True)
                questions = questions[:10]
        response_time = (time.time()-t)*1000
        self.redirect('/')

def update_termstats(term, docfreq):
    termstats_query = TermStats.all()
    termstats_query.filter("term =", term)
    termstats = termstats_query.get()
    if termstats:
        termstats.docfreq += docfreq
    else:
        termstats = TermStats()
        termstats.term = term
        termstats.docfreq = docfreq
    termstats.put()
    
class Ask(webapp.RequestHandler):
    def post(self):
        question = Question()
        if users.get_current_user():
            question.author = users.get_current_user()
        question.content = self.request.get('content').strip()
        global response_time
        t = time.time()
        question.terms = list(text2terms(question.content))
        if question.terms:
            question.put()
            for term in question.terms:
                update_termstats(term, 1)
        response_time = (time.time()-t)*1000
        self.redirect('/')

from collections import defaultdict

class Load(webapp.RequestHandler):
    def post(self):
        content_list = self.request.get('questions_file').split('\n')
        questions = []
        term_dict = defaultdict(int)
        for content in content_list:
            content = content.strip()
            if not content:
                continue
            question = Question()
            if users.get_current_user():
                question.author = users.get_current_user()
            question.content = content.decode('utf-8')
            question.terms = list(text2terms(question.content))
            if not question.terms:
                continue
            questions.append(question)
            for term in question.terms:
                term_dict[term] += 1
        db.put(questions)
        for term in term_dict:
            update_termstats(term, term_dict[term])
        self.redirect('/')

class Clear(webapp.RequestHandler):
    def post(self):
        db.delete(Question.all(keys_only=True))
        db.delete(TermStats.all(keys_only=True))
        self.redirect('/')

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/search', Search),
                                      ('/ask', Ask),
                                      ('/load', Load),
                                      ('/clear', Clear)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()