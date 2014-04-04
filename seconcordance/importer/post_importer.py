# -*- coding: utf-8 -*-
import requests
import json
from readini import Ini
import MySQLdb as mysql
import logging
from VerseReference import BibleReference
import time
import re

def update_database(ini_file):
	#Read keys in ini, kick off an Importer.get_posts)_

	readini = Ini(ini_file)
	runner = Importer(readini)
	runner.configure_logs()

	for sitename, lastrundate in readini.report_last_runs():
		last_run_date = readini.get_last_run(sitename)
		logging.debug("Importing new posts in {0} since {1}".format(sitename, last_run_date.strftime("%Y-%m-%d")))

		runner.get_posts(sitename, last_run_date)
		readini.set_last_run(sitename)

#To get a known id, use this:
def read_question(ini_file, sitename, id):
	readini = Ini(ini_file)

	runner = Importer(readini)
	runner.configure_logs()

	runner.get_question_by_id(sitename, id)


class Importer:

	#URL of the API to retrieve posts.  See: http://api.stackexchange.com/docs/questions#pagesize=100&order=desc&sort=activity&filter=!!1uzN8oLa40xRL*E_cnH)0co0A4.Pc5YVAIM)tO2EFak5(eJ5AzdowJDaRzU8g1P0uoE&site=christianity
	#for details on what the object looks like.  It returns the body markdown, id, links, etc.. of questions and answers.  Don't be fooled!
	se_getquestions_filter = "!1uzN8oLa40xRL*E_cnH)0co0A4.Pc5YVAIM)tO2EFak5(eJ5AzdowJDaRzU8g1P0uoE&key=rIKmb7)KLgtLPKo5*jubZw(("
	url_se_getquestions = "http://api.stackexchange.com/2.2/questions?fromdate={2}&pagesize=100&page={1}&order=desc&sort=activity&site={0}&filter={3}"

	def __init__(self, readini):
		self.ini = readini
		log_file = readini.get_ini_value('logging', 'filename')
		logging.basicConfig(filename=log_file, filemode='w', level=logging.INFO)

	def configure_logs(self):
		log_file = self.ini.get_ini_value('logging', 'filename')
		logging.basicConfig(filename=log_file, 
							filemode='w', 
							level=logging.WARNING,
							format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
	                    	datefmt='%m-%d %H:%M')

		console = logging.StreamHandler()
		console.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
		console.setFormatter(formatter)
		logging.getLogger('').addHandler(console)

	def connect_to_mysql(self):
		db_server = self.ini.get_ini_value('database', 'server')
		db_user = self.ini.get_ini_value('database', 'user')
		db_password = self.ini.get_ini_value('database', 'password')
		db_name = self.ini.get_ini_value('database', 'database')

		return mysql.connect(db_server, db_user, db_password, db_name)

	def get_question_by_id(self, sitename, id):
		"""For debug purposes, this function gets a question by its id and saves it"""
		con = self.connect_to_mysql()
		se_api_url ="http://api.stackexchange.com/2.2/questions/{0}/?site={1}&filter={2}".format(id, sitename, self.se_getquestions_filter)

		print "calling {0}".format(se_api_url)
		r = requests.get(se_api_url)
		if (r.status_code == 200):
			se_posts = json.loads(r.text)
			print "found se_post"

			for post in se_posts['items']:
				if 'question_id' in post:
					q = self.process_post(post)
					q.display_state()
					for ans in q.answers:
						ans.display_state()

					self.save_posts(con, q)
				else:
					logging.warning("Malformed post - no json['question_id']!\n{0}".format(post))
		else:
			logging.warning("Http status_code {1} reading posts from Stack Exchange at {0}".format(se_api_url, r.status_code))

		if con.open:
			con.close()

	def get_posts(self, sitename, last_run_time):
		self.sitename = sitename
		self.from_date = last_run_time.strftime('%s')
		
		con = self.connect_to_mysql()

		npage = 1
		has_more_pages = True

		while has_more_pages:
			se_api_url = self.url_se_getquestions.format(self.sitename, npage, self.from_date, self.se_getquestions_filter)
			logging.info( "Retrieving SE posts at {0}".format(se_api_url) )

			r = requests.get(se_api_url)

			if (r.status_code == 200):
				se_posts = json.loads(r.text)

				#TODO: Handle the SE_URL_API Backoff message
				has_more_pages = se_posts['has_more']

				for post in se_posts['items']:
					if 'question_id' in post:
						logging.debug("...processing question {0}".format(post['question_id']))

						q = self.process_post(post)

						q.display_state()
						for ans in q.answers:
							ans.display_state()

						self.save_posts(con, q)

					else:
						logging.warning("Malformed post - no json['question_id']!\n{0}".format(post))

			else:
				logging.warning("Http status_code {1} reading posts from Stack Exchange at {0}".format(se_api_url, r.status_code))

			if con.open:
				con.close()

			#Wait in order to stay until rate limiting.  The real problem is the biblia api, which stops me at 5000.
			#Since I'm doing somewhere near 200 requests per 100 se_posts, and I can do no more than 30 batches per hour, I will wait 2 minutes between batches.
			if has_more_pages:
				logging.debug( "===========================================")
				logging.debug( "Waiting so as not to exceed API threshholds")
				logging.debug( "===========================================")
				time.sleep(20)

			npage += 1

	def process_post(self, post):
		"""Reads the passed Json into the Object Model"""
		q = self.parse_question(post)
		self.locate_bible_refs(q)
		self.insert_body_tags(q)

		for a in q.answers:
			self.locate_bible_refs(a)
			self.insert_body_tags(a)

		return q

	def save_posts(self, con, q):
		"""Saves each se_post to the database"""

		try:
			cur = con.cursor()
		except Exception, e:
			logging.warning( "Unable to obtain a valid cursor:".format(q.post_id, q.link))
			logging.exception( e )
			con.rollback()

		is_ok = (q.save_to_db(cur))

		if is_ok:
			for a in q.answers:
				is_ok = a.save_to_db(cur)

				if not is_ok:
					logging.warning("Unsuccessful answer save, rolling bacl: Answer id:{0}, Link={1}".format(a.post_id, a.link))
					break
		else:
			logging.warning("Unsuccessful question save, rolling bacl: Answer id:{0}, Link={1}".format(q.post_id, q.link))

		if is_ok:
			con.commit()
		else:
			logging.info("Rolling back")
			con.rollback()

	def parse_question(self, post_item):
		#When /questions/ is called, each question returns the question and the various answers attached to it.
		#This function reads through that structure and instantiates the objects in a common SQL connection, so
		#that the rollback is atomic.

		# Example post['item'] = {
		#       "question_id": 27027,
		#       "title": "Why do Catholics bow for icons of the Virgin Mary?"
		#       "link": "http://christianity.stackexchange.com/questions/27027/why-do-catholics-bow-for-icons-of-the-virgin-mary",
		#       "body_markdown": "It doesn&#39;t surprise me when orthodox Christians bow for icons of the Virgin Mary, since they believe that she is present in the icon. But why do (some) Catholics also bow for icons of Mary?\r\n\r\nThere are numerous pages on the internet like [this one](http://www.godlovespeople.com/deceptions/maryiolatry.htm) where the author argues against this gesture. The reasoning is that it&#39;s against the commandment from Ex 20:4-5:\r\n\r\n&gt; Thou shalt not make unto thee any graven image, or any likeness of any thing that is in heaven above, or that is in the earth beneath, or that is in the water under the earth: Thou shalt not bow down thyself to them, nor serve them: for I the LORD thy God am a jealous God, visiting the iniquity of the fathers upon the children unto the third and fourth generation of them that hate me.\r\n\r\nHowever, I cannot find arguments against this position. I guess there are, but what are they?",
		#		"owner": {
		#		        "display_name": "Camil Staps"
		#		      },
		#       "score": 5,
		#       "is_answered": false,
	 	#      	"tags": ["catholicism","virgin-mary","iconography"],
		#       "answers": [
		#         {
		#           "answer_id": 27088,
		#           "link": "http://christianity.stackexchange.com/questions/27027/why-do-catholics-bow-for-icons-of-the-virgin-mary/27088#27088"
		#           "body_markdown": "Biblically, there is no reason to bow to an image. God said don&#39;t do it. Man finds an excuse to do it. It is the reason that we have so many Christian denominations. The Bible says one thing, but people are either ignorant of what the Bible says, or choose not to do it. The Bible is the Word of God, and the Word of God has authority.\r\n\r\n&gt; Thou shalt not make unto thee any graven image, or any likeness of any\r\n&gt; thing that is in heaven above, or that is in the earth beneath, or\r\n&gt; that is in the water under the earth: Thou shalt not bow down thyself\r\n&gt; to them, nor serve them: for I the LORD thy God am a jealous God,\r\n&gt; visiting the iniquity of the fathers upon the children unto the third\r\n&gt; and fourth generation of them that hate me.\r\n&gt; \r\n&gt; Ex, 20:4, 5\r\n&gt; \r\n&gt; Being then God&#39;s offspring, we ought not to think that the divine\r\n&gt; being is like gold or silver or stone, an image formed by the art and\r\n&gt; imagination of man.\r\n&gt; \r\n&gt; Acts 17:29\r\n&gt; \r\n&gt; I am the Lord; that is my name; my glory I give to no other, nor my\r\n&gt; praise to carved idols.\r\n&gt; \r\n&gt; Isaiah 42:8\r\n&gt; \r\n&gt; Then it becomes fuel for a man. He takes a part of it and warms\r\n&gt; himself; he kindles a fire and bakes bread. Also he makes a god and\r\n&gt; worships it; he makes it an idol and falls down before it.\r\n&gt; \r\n&gt; Isaiah 44:15\r\n&gt; \r\n&gt; But what is God&#39;s reply to him? “I have kept for myself seven thousand\r\n&gt; men who have not bowed the knee to Baal.”\r\n&gt; \r\n&gt; Romans 11:4\r\n\r\nSimply bowing the knee to an image is a direct offense to God, regardless of what it symbolizes.\r\n\r\nI am not trying to be insensitive to what others believe. Neither am I pointing fingers at any one denomination. I am simply stating what is in the Bible. If you don&#39;t think this is so, I simply ask, tell me where in the Bible it says it is RIGHT to bow to an image?",
		#           "is_accepted": false,
		#           "score": 0,
		#			{
		# 	         "owner": {
		#   	         "display_name": "jlaverde"
		#          	},		
        #         }
		#       ],
		#		"closed_details": {
		#        "by_users": [
		#          {
		#            "display_name": "Matt"
		#          },
		#          {
		#            "display_name": "Caleb"
		#          }
		#        ],
		#        "on_hold": true,
		#        "description": "This question appears to be off-topic. The users who voted to close gave these specific reasons:    <ul class=\"close-as-off-topic-status-list\">\r\n        <li>&quot;Questions seeking <b>pastoral advice</b> are off-topic here; your spiritual problems are too important to be left in the hands of random Internet people. See: <a href=\"http://meta.christianity.stackexchange.com/questions/255/pastoral-advice-questions\">Pastoral Advice Questions</a>&quot; &ndash; Matt, Caleb</li>\r\n        <li>&quot;General <b>philosophical or sociological questions</b> are off-topic unless clearly asking for a doctrinal answer. See: <a href=\"http://meta.christianity.stackexchange.com/questions/779/on-topic-and-constructive-examples\">On-topic and constructive examples</a>.&quot; &ndash; James T, David Stratton</li>\r\n    </ul>",
		#        "reason": "off-topic"
		#      },
		#      "owner": {
		#        "display_name": "Anthony"
		#      },
		#      "is_answered": true,
		#      "closed_date": 1396522187,
		# }

		#Extract the Question
		q = SE_Question()
		q.parse(post_item)
		q.answers = []	

		#Extract the Answers
		if 'answers' in post_item:
			for ans_item in post_item['answers'] :
				a = SE_Answer()
				a.parse(q, ans_item)
				q.answers.append(a)
		else:
			logging.warn("There are no answers on question {0}".format(q.link))

		return q

	def locate_bible_refs(self, sepost_object):
		"""Reads the body to locate found bible references, tags the body, and stores an array of found references"""

		refparser_url = "http://api.biblia.com/v1/bible/scan/?"
		biblia_apikey = self.ini.get_ini_value('keys', 'biblia_apikey')

		sepost_object.biblia_apikey = biblia_apikey
		sepost_object.found_refs = []
		nchunk_start = 0
		nchunk_size=1000

		se_body = sepost_object.body.encode('utf-8', errors='ignore')

		while nchunk_start < len(se_body):
			body_chunk = se_body[nchunk_start:nchunk_size]

			refparser_params = {'text': body_chunk, 'key': biblia_apikey }
			headers = {'content-type': 'text/plain; charset=utf-8', 'Accept-Encoding': 'gzip,deflate,sdch'}

			refparse = requests.get(refparser_url, params = refparser_params, headers=headers)

			if (refparse.status_code == 200):
				foundrefs = json.loads(refparse.text)
				for foundref in foundrefs['results']:
					foundref['textIndex'] += nchunk_start
					sepost_object.found_refs.append( foundref )
			else:
				msg = "Status Code {0}: Failed to retrieve valid parsing info at {1}\n     returned text is: =>{2}<=".format(refparse.status_code, refparse.url, refparse.text)
				print msg
				logging.exception(msg)

			nchunk_start += (nchunk_size-50)
			#Note: I'm purposely backing up, so that I don't accidentally split a reference across chunks

	def insert_body_tags(self, sepost_object):
		"""Using the information from locate_bible_refs, decorates the body_markdown with <SPAN> tags"""

		#TODO: Add <SPAN class='verse_reference' reference='Malachi 1:2-5'>Mal 1:2-5</SPAN> tags to found references in body

		se_body = sepost_object.body
		for found_ref in reversed(sepost_object.found_refs):
			print found_ref['textLength']
			si = found_ref['textIndex']
			l = found_ref['textLength']

			open_tag = "<SPAN reference='"+found_ref['passage']+"' class='verse_reference' >"
			close_tag = "</SPAN>"

			se_body = 	se_body[:si] + \
						open_tag + \
						se_body[si:si+l] + \
						close_tag + \
						se_body[si+l:]

			#TODO: Now, I need to adjust the index starts of each... or, I could just abandon the textIndex & Length, 
			#since they really would be better served by regexing the new consistent <SPAN syntax
			#The highlighter could just add a class='active' when the reference is looked for...
			#TODO: The snippet creator in highlighter.py now only needs to worry about open SPAN tags...


		sepost_object.body = se_body

class SE_PostItem:
	"""SE_PostItem is the parser for SE_Question and SE_Answer.  It handles the save of all items, but Q & A handle the details of each bit"""
	#This class has multiple items, and the save instance will save them all
	
	def __init__(self):
		self.post_id = ""		#Represents SE's internal id to the post
		self.link = ""			#SE's canonical link to the post
		self.title = ""			#The title of the associated question
		self.body = ""			#Encoded, Tagged, AutoEscaped body_markdown

		self.score = 0 			#Current score of the question or answer.  Note: Likely to be out of date at first at least...
		self.owner = ""			#Display Name of the Author
		self.is_closed = False
		self.close_reason = ""	#Reason why the question was closed - if in fact it is closed
		self.is_answered = False

		self.tags = []			#List of the tags associated with the post
		self.found_refs = [];	#An Array of Parsed Bible Refs that appear in the body

	def is_valid(self):
		if(self.post_id == ""):
			return False

		if(self.link == ""):
			return False

		return True

	def save_to_db(self, cur):
		"""Saves this object to the database"""
		is_ok = self.save_postrecord(cur)

		if is_ok:
			is_ok = self.save_biblerefs(cur)

		return is_ok

	def save_postrecord(self, cur):
		#Main Post Record
		try:
			logging.info( "Inserting Post # {0} ({1})".format(self.post_id, self.title))

			#qry_Insert_Post = "INSERT INTO concordance_sepost (sepost_id, owner, type, title, link, score, body) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=%s, body=%s, score=%s"
			#cur.execute(qry_Insert_Post, (self.post_id, self.owner, self.post_type, self.title, self.link, self.score, self.body, self.title, self.body, self.score))
			#Consider:
			#  	INSERT INTO concordance_sepost (sepost_id, title, link) VALUES (%s, %s, %s) ON DUPLICATE sepost_id UPDATE title=%s
			# Then, update details
			#	UPDATE concordance_sepost SET body=%s WHERE sepost_id=%s   
			#	UPDATE concordance_sepost SET score=%s WHERE sepost_id=%s   
			# How much slower is this, vis a vis INSERT VALUES?  The readibility of the code will be enchanced...
			# You know what? Optimize for maintainability first, performance second!!!

			qry = "INSERT INTO concordance_sepost (sepost_id, link, type) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE link = %s"
			cur.execute(qry, (self.post_id, self.link, self.post_type, self.link))

			qry = "UPDATE concordance_sepost SET title=%s WHERE sepost_id=%s"
			cur.execute(qry, (self.title, self.post_id))
			qry = "UPDATE concordance_sepost SET body=%s WHERE sepost_id=%s"
			cur.execute(qry, (self.body, self.post_id))

			qry = "UPDATE concordance_sepost SET score=%s WHERE sepost_id=%s"
			cur.execute(qry, (self.score, self.post_id))
			qry = "UPDATE concordance_sepost SET owner=%s WHERE sepost_id=%s"
			cur.execute(qry, (self.owner, self.post_id))
			qry = "UPDATE concordance_sepost SET is_closed=%s WHERE sepost_id=%s"
			cur.execute(qry, (self.owner, self.is_closed))
			qry = "UPDATE concordance_sepost SET closed_reason=%s WHERE sepost_id=%s"
			cur.execute(qry, (self.owner, self.close_reason))
			qry = "UPDATE concordance_sepost SET is_answered=%s WHERE sepost_id=%s"
			cur.execute(qry, (self.owner, self.is_answered))

			qry = "DELETE FROM concordance_setag WHERE sepost_id = %s"
			cur.execute(qry, (self.post_id,))
			for tag in self.tags:
				qry = "INSERT INTO concordance_setag (sepost_id, tag) VALUES (%s, %s)"
				cur.execute(qry, (self.post_id, tag))

			return True	

		except Exception, e:
			logging.warning( "Unable to commit post {0} to database at {1} using SQL statement:\n   {2}".format(self.post_id, self.link, qry))
			logging.exception( e )
			return False

	def save_biblerefs(self, cur):

		#Note: self.biblia_apikey was set during the Importer.locate_bible_refs() fnuction

		#For Each Found Bible Reference
		try:
			qry_Clear_Refs = "DELETE FROM concordance_reference WHERE sepost_id=%s"
			cur.execute(qry_Clear_Refs, (self.post_id,))
		except Exception, e:
			logging.warning( "Unable to clear existing bible_refs for post {0} to database at {1} using SQL:\n   {2}:".format(self.post_id, self.link, qry_Clear_Refs))
			logging.exception( e )

		try:
			qry_Insert_Ref = ""
			for found in self.found_refs:
				qry_Insert_Ref = "INSERT INTO concordance_reference (sepost_id, reference, ref_book_num, end_book_num, ref_startchapter_num, ref_startverse_num, ref_endchapter_num, ref_endverse_num, se_post_index_start, se_post_reference_length) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

				plain_ref = found['passage'].replace(u"\u2014", "-").replace(u"\u2013", "-").replace(u"\u2019", "'").encode('utf-8')
				refr = BibleReference(plain_ref, self.biblia_apikey)

				cur.execute(qry_Insert_Ref, (self.post_id, refr.plain_ref, refr.book_num, refr.end_book_num, refr.start_chapter, refr.start_verse, refr.end_chapter, refr.end_verse, found['textIndex'], found['textLength']))

		except Exception, e:
			logging.warning( "Unable to save bible_refs for post {0} to database at {1} using SQL:\n   {2}:".format(self.post_id, self.link, qry_Insert_Ref))
			logging.exception( e )
		
		return True

	def display_state(self):
		print "========================================================="
		print "post_id = {0}".format(self.post_id)

		if self.post_type == 'q':
			print "QUESTION: {0}".format(self.title)
		else:
			print "ANSWER"
			print "on {0}".format(self.title)

		print "Link = {0}".format(self.link)
		print "=========="

		#self.body 			

		print "BODY:"
		print self.body.encode('utf-8', errors='ignore')

		print "Score = {0}".format(self.score)
		print "Owner = {0}".format(self.owner)
		print "is_closed = {0}".format(self.is_closed)
		print "close_reason = {0}".format(self.close_reason)
		print "Link = {0}".format(self.is_answered)

		print "TAGS:"
		for tag in self.tags:
			print "		{0}".format(tag)

		print "BIBLE_REFS FOUND:"
		for bibleref in self.found_refs:
			print " 		{0}".format(bibleref)

		print "========================================================="

class SE_Question(SE_PostItem):

	def __init__(self):
		SE_PostItem.__init__(self)
		self.post_type = "q"
		self.answers = []
		self.is_answered = False

	def parse(self, post_item):
		if('question_id' in post_item):
			self.post_id = post_item['question_id']
		else:
			logging.INFO('Malformed Question: No item[question_id] in json:\n{0}'.format(post_item))
			return

		if('title' in post_item):
			self.title = post_item['title']

		if('link' in post_item):
			self.link = post_item['link']

		if('score' in post_item):
			self.score = post_item['score']

		if('body_markdown' in post_item):
			self.body = post_item['body_markdown']

		if('owner' in post_item):
			dsp = post_item['owner']
			if('display_name' in dsp):
				self.owner = dsp['display_name']

		if('tags' in post_item):
			self.tags = post_item['tags']

		if('is_answered' in post_item):
			self.is_answered = post_item['is_answered']

		self.is_closed = ('is_closed' in post_item)
		if(self.is_closed):
			if('closed_details' in post_item):
				cl = post_item['closed_details']
				if('reason' in cl):
					self.close_reason = cl['reason']

class SE_Answer(SE_PostItem):

	def __init__(self):
		SE_PostItem.__init__(self)
		self.post_type = "a"
		self.is_accepted = False

	def parse(self, q, ans_item):
		self.question_id = q.post_id

		if('answer_id' in ans_item):
			self.post_id = ans_item['answer_id']
		else:
			logging.INFO('Malformed Answer: No item[answer_id] in json:\n{0}'.format(ans_item))
			return

		if('link' in ans_item):
			self.link = ans_item['link']

		if('score' in ans_item):
			self.score = ans_item['score']

		if('body_markdown' in ans_item):
			self.body = ans_item['body_markdown']

		if('owner' in ans_item):
			dsp = ans_item['owner']
			if('display_name' in dsp):
				self.owner = dsp['display_name']

		if('is_accepted' in ans_item):
			self.is_accepted = ans_item['is_accepted']

		self.title = q.title
		self.tags = q.tags
		self.is_closed = q.is_closed
		self.close_reason = q.close_reason
