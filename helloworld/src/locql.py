from google.appengine.ext import db
from mapreduce import operation as op
from mapreduce import control as ctrl

import logging
import math

from text import extract_terms

class Question(db.Model):
    question_id = db.IntegerProperty()  # don't use it as key to facilitate testing
    title = db.StringProperty()
    create_time = db.DateTimeProperty()
    place_ids = db.ListProperty(int)
    terms = db.StringListProperty()

class TermStat(db.Model):
    docfreq = db.IntegerProperty()

def generate_local_terms(terms, place_ids):
    return [(term+' '+str(place_id)) for term in terms for place_id in place_ids]

def question_score(question, term_dict):
    score = 0.0
    for term in question.terms:
        if term in term_dict:
            term_df = term_dict[term]
            if term_df > 0:
                score += math.sqrt(1.0/term_df)
    question_len = len([term for term in question.terms if term.find(' ') < 0])
    score /= math.sqrt(question_len)
    return score

def find_relevant_questions(query, place_ids=[], max_num=10):
    query = query.strip()
    query_terms = extract_terms(query)
    query_terms += generate_local_terms(query_terms, place_ids)
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
            questions = question_query.fetch(max_num*10) # the number of questions to be ranked
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

def create_question(question):
    if not question:
        return False
    question_query = Question.all(keys_only=True)
    question_query.filter("question_id =", question.question_id)
    if question_query.get():
        return False
    logging.info("Create a new question")
    question.terms = extract_terms(question.title)
    question.terms += generate_local_terms(question.terms, question.place_ids)
    if question.terms:
        term_dict = dict(zip(question.terms, [1]*len(question.terms)))
        update_termstats(term_dict)
    db.put(question)
    return True

def create_questions(questions):
    for question in questions:
        create_question(question)

def delete_question(question):
    if not question:
        return False
    question_query = Question.all(keys_only=True)
    question_query.filter("question_id =", question.question_id)
    quertion_key = question_query.get()
    if not quertion_key:
        return False
    logging.info("Create a new question")
    question.terms = extract_terms(question.title)
    question.terms += generate_local_terms(question.terms, question.place_ids)
    if question.terms:
        term_dict = dict(zip(question.terms, [-1]*len(question.terms)))
        update_termstats(term_dict)
    db.delete(quertion_key)
    return True

def delete_entity(e):
    "The MapReduce handler for batch deletion"
    yield op.db.Delete(e)

def delete_all_questions():
    logging.info("Delete all existing questions")
    ctrl.start_map("Delete all Question entities", 
                   'locql.delete_entity', 
                   'mapreduce.input_readers.DatastoreKeyInputReader', 
                   {'entity_kind': 'locql.Question'})
    ctrl.start_map("Delete all TermStat entities", 
                   'locql.delete_entity', 
                   'mapreduce.input_readers.DatastoreKeyInputReader',
                   {'entity_kind': 'locql.TermStat'})

def get_questions(question_ids):
    questions = []
    for question_id in question_ids:
        question_query = Question.all()
        question_query.filter("question_id =", question_id)
        questions.append(question_query.get())
    return questions
