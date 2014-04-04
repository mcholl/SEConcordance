# -*- coding: utf-8 -*-
import requests
import json
import readini
import MySQLdb as mysql
import sys
import pprint
import time
from VerseReference import BibleReference
import logging

se_filter = "!LHMdLCIm1-m(LAqHS*VafI"

#This filter corresponds to the filter that api.stackexchange.com uses.  By putting it here, I can debug better
# !-My9VsefIqes2OA9EyxQhzUNuqNvraT4i - requires authentication
# !2.5sIHWRk9kld4Sb1Qn6N - no title
# !BJyHsUt9WLl9dRFPUz(Uyr874YYvNH
# !LHMdLCIm1-m(LAqHS*VafI - retrieves body_markdown instead of body
#http://api.stackexchange.com/docs/posts#order=desc&sort=activity&site=christianity&filter=!LHMdLCIm1-m(LAqHS*VafI

#http://api.stackexchange.com/docs/questions#order=desc&sort=activity&filter=!*1Kh0phYsS.(Pmmttx2HcUKluE2jiGhs09)jl)GVK&site=christianity&run=true will get the tags and whether the question is opened or closed

def connect_to_mysql():
	db_server = readini.get_ini_value('database', 'server')
	db_user = readini.get_ini_value('database', 'user')
	db_password = readini.get_ini_value('database', 'password')
	db_name = readini.get_ini_value('database', 'database')

	return mysql.connect(db_server, db_user, db_password, db_name)

def process_newPosts(site_name, from_date, sepost_process_function, se_post_save_function):
	npage = 1
	has_more_pages = True

	while has_more_pages:
		se_api_url = 'http://api.stackexchange.com/posts?fromdate={0}&order=asc&sort=creation&filter={3}&site={1}&page={2}&pagesize=100'.format(from_date, site_name, npage, se_filter)
		msg = "Retrieving SE posts at {0}".format(se_api_url)
		logging.info( msg )
		print msg

		r = requests.get(se_api_url)

		if (r.status_code == 200):
			se_posts = json.loads(r.text)
			has_more_pages = se_posts['has_more']

			for post in se_posts['items']:
				msg = "...processing post {0}".format(post['post_id'])
				print msg
				logging.info(msg)
				found_refs = sepost_process_function(post)
				se_post_save_function(post, found_refs)
		else:
			msg = "Http status_code {1} reading posts from Stack Exchange at {0}".format(se_api_url, r.status_code)
			print msg
			logging.warning(msg)

		#Wait in order to stay until rate limiting.  The real problem is the biblia api, which stops me at 5000.
		#Since I'm doing somewhere near 200 requests per 100 se_posts, and I can do no more than 30 batches per hour, I will wait 2 minutes between batches.
		if has_more_pages:
			logging.info( "===========================================")
			logging.info( "Waiting so as not to exceed API threshholds")
			logging.info( "===========================================")
			time.sleep(20)

		npage += 1

def strip_encodings(raw_body):
	"""The body of the SE Post needs to have some changes. First off, we want to tag the found biblical references found references. Second, we want to strip some characters"""

	body = raw_body.replace(u"\u2014", "-").replace(u"\u2013", "-").replace(u"\u2019", "'").encode('utf-8')

	#Note: Yes, I could do a whole up HTML entity replace, but this meets my needs...
	body = body.replace("&quot;", "\"").replace("&#39;", "\'")

	return body

def locate_references(se_post):
	refparser_url = "http://api.biblia.com/v1/bible/scan/?"
	msg = "...{0}".format(se_post['title'])
	print msg
	logging.info(msg)
	
	se_body = se_post['body_markdown'].encode('utf-8', errors='ignore')
	found_refs = []
	nchunk_start = 0
	nchunk_size=1000

	while nchunk_start < len(se_body):
		body_chunk = se_body[nchunk_start:nchunk_size]

		refparser_params = {'text': body_chunk.encode('ascii', errors='ignore'), 'key': biblia_apikey }
		headers = {'content-type': 'text/plain; charset=utf-8', 'Accept-Encoding': 'gzip,deflate,sdch'}

		refparse = requests.get(refparser_url, params = refparser_params, headers=headers)

		if (refparse.status_code == 200):
			foundrefs = json.loads(refparse.text)
			for foundref in foundrefs['results']:
				foundref['textIndex'] += nchunk_start
				found_refs.append( foundref )
		else:
			msg = "Status Code {0}: Failed to retrieve valid parsing info at {1}\n     returned text is: =>{2}<=".format(refparse.status_code, refparse.url, refparse.text)
			print msg
			logging.exception(msg)

		nchunk_start += (nchunk_size-50)
		#Note: I'm purposely backing up, so that I don't accidentally split a reference across chunks

	return found_refs

def save_post_to_mysql(se_post, found_refs):
	if not found_refs:
		logging.info( "No References located in post id #{0} at {1}".format(se_post['post_id'],se_post['link']))
		return

	con = connect_to_mysql()
	try:
		cur = con.cursor()
	except Exception, e:
		logging.warning( "Unable to commit post {0} to database at {1}:".format(post_id, link))
		logging.exception( e )
		con.rollback()
		if con.open:
			con.close()
		return

	try:
		post_id = se_post['post_id']
		post_type = se_post['post_type'].encode('utf-8')[0]
		title = strip_encodings(se_post['title'])
		link = se_post['link'].encode('utf-8')
		score = se_post['score']

		body = strip_encodings(se_post['body_markdown'])

	except Exception, e:
		logging.warning( "se_post not as expected.  received {0}:".format(se_post))
		logging.exception( e )
		con.rollback()
		if con.open:
			con.close()
		return

	try:
		owner = se_post['owner']['display_name'].encode('utf-8')
	except:
		owner = "removed user account"


	try:
		logging.info( "Inserting Post # {0} ({1})".format(post_id, title))
		qry_Insert_Post = "INSERT INTO concordance_sepost (sepost_id, owner, type, title, link, score, body) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=%s, body=%s"
		cur.execute(qry_Insert_Post, (post_id, owner, post_type, title, link, score, body, title, body))
	except Exception, e:
		logging.warning( "Unable to commit post {0} to database at {1} using {2}:".format(post_id, link, qry_Insert_Post))
		logging.exception( e )
		con.rollback()
		if con.open:
			con.close()
		return

	try:
		qry_Clear_Refs = "DELETE FROM concordance_reference WHERE sepost_id=%s"
		cur.execute(qry_Clear_Refs, (post_id,))
	except Exception, e:
		logging.warning( "Unable to commit post {0} to database at {1} using {2}:".format(post_id, link, qry_Clear_Refs))
		logging.exception( e )
		con.rollback()
		if con.open:
			con.close()
		return

	try:
		for found in found_refs:
			plain_ref = found['passage'].replace(u"\u2014", "-").replace(u"\u2013", "-").replace(u"\u2019", "'").encode('utf-8')
			refr = BibleReference(plain_ref)
			logging.info( "  Reference Found: {0}".format(refr.plain_ref))
			qry_Insert_Ref = "INSERT INTO concordance_reference (sepost_id, reference, ref_book_num, end_book_num, ref_startchapter_num, ref_startverse_num, ref_endchapter_num, ref_endverse_num, se_post_index_start, se_post_reference_length) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

			cur.execute(qry_Insert_Ref, (post_id, refr.plain_ref, refr.book_num, refr.end_book_num, refr.start_chapter, refr.start_verse, refr.end_chapter, refr.end_verse, found['textIndex'], found['textLength']))

		con.commit()
	except Exception, e:
		logging.warning( "Unable to commit post {0} to database at {1}:".format(post_id, link))
		logging.exception( e )
		con.rollback()

	finally:
		if con.open:
			con.close()

def process_sepost_by_id(sitename, postid, sepost_process_function):
	#For debugging purposes, this retrieves a particular sepost by site (e.g. 'hermeneutics') and id (e.g. ('8727'))
	se_api_url = 'http://api.stackexchange.com/posts/{0}?filter={1}&site={2}'.format(postid, se_filter, sitename)
	#logging.info( "Retrieving SE posts at {0}".format(se_api_url) )
	print "Retrieving SE posts at {0}".format(se_api_url) 
	r = requests.get(se_api_url)

	if (r.status_code == 200):
		ret = json.loads(r.text)
		se_post = ret['items'][0]
		found_refs = sepost_process_function(se_post)
		
		return se_post, found_refs

	return {'error':r.status_code, 'encoding':r.encoding, 'url':se_api_url, 'r':r}, []

def show_post_details(se_post, found_refs):
	#This is a debugging function to show what is being collected - but not to do anything with it other than log it...

	try:
		post_id = se_post['post_id']
		post_type = se_post['post_type'].encode('utf-8')[0]
		title = strip_encodings(se_post['title'])
		link = se_post['link'].encode('utf-8')
		score = se_post['score']

		body = se_post['body_markdown']

		print "post_id = {0}".format(post_id)
		print "title = {0}".format(title)
		print "link = {0}".format(link)

	except Exception, e:
		print "Exception parsing post:\n"
		pprint.pprint(e)
		print se_post 

	for found in found_refs:
		plain_ref = strip_encodings(found['passage'])

		refr = BibleReference(plain_ref)
		print "  Reference Found: {0}".format(refr.plain_ref)

		snippet = body[found['textIndex']:found['textIndex']+found['textLength']]
		snippet = strip_encodings(snippet)

		print "        at index {0}, length {1} = '{2}'".format(found['textIndex'], found['textLength'], snippet)

	print "Body:\n{0}".format(body)

def main():
	for site_name in ['christianity', 'hermeneutics', 'judiasm']:
		last_run_date = readini.get_last_run(site_name).strftime("%Y-%m-%d")

		logging.info("{0}.stackexchange.com last checked on {1}".format(site_name, last_run_date))
		process_newPosts(site_name, last_run_date, locate_references, save_post_to_mysql)

		readini.set_last_run(site_name)

biblia_apikey = readini.get_ini_value('keys', 'biblia_apikey')
log_file = readini.get_ini_value('logging', 'filename')
logging.basicConfig(filename=log_file, filemode='w', level=logging.INFO)
main()


# se_post, found_refs = process_sepost_by_id('hermeneutics', '8727', locate_references)
# print found_refs
# show_post_details(se_post, found_refs)

