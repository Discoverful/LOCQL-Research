from google.appengine.ext import db

import logging
from datetime import datetime

from text import extract_terms

class Question(db.Model):
    question_id = db.IntegerProperty()  # don't use it as key to facilitate testing
    title = db.StringProperty()
    place_id = db.IntegerProperty()
    create_time = db.DateTimeProperty()
    terms = db.StringListProperty()

class TermStat(db.Model):
    docfreq = db.IntegerProperty()

def generate_local_terms(terms, place_ids):
    return [(term+' '+place_id) for term in terms for place_id in place_ids]

def question_score(question, term_dict):
    score = 0.0
    for term in question.terms:
        if term in term_dict:
            score += (1.0+(1.0/(term_dict[term]+1.0)))**2
    score /= len(question.terms)
    return score

def find_relevant_questions(query, place_ids=[], max_num=10):
    query = query.strip()
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
        termstats = TermStat.get_by_key_name(query_terms)
        term_dict = dict([(termstat.key().name(),termstat.docfreq) for termstat in termstats if termstat])
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
    return questions[:max_num]

def update_termstats(term_dict):
    terms = term_dict.keys()
    termstats = TermStat.get_by_key_name(terms)
    for i in range(len(terms)):
        term = terms[i]
        more_docfreq = term_dict[term]
        if termstats[i]:
            termstats[i].docfreq += more_docfreq
        else:
            termstats[i] = TermStat(key_name=term)
            termstats[i].docfreq = more_docfreq
    db.put(termstats)

def add_question(question_title):
    question_title = question_title.strip()
    if not question_title:
        return
    question = Question()
    question.create_time = datetime.utcnow()
    question.title = question_title
    question.terms = extract_terms(question_title)
    if not question.terms:
        return
    db.put(question)
    term_dict = dict(zip(question.terms, [1]*len(question.terms)))
    update_termstats(term_dict)

def add_questions(question_titles):
    logging.info("Adding new questions.")
    for question_title in question_titles:
        add_question(question_title)

def delete_all(Model, chunk=100):
    query = Model.all(keys_only=True)
    while True:
        keys = query.fetch(chunk)
        if keys:
            db.delete(keys)
        else:
            break

def delete_all_questions():
    logging.info("Deleting all questions.")
    delete_all(Question)
    delete_all(TermStat)
