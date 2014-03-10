import requests
import json
import readini
import MySQLdb as mysql
import sys
import pprint
import time
from VerseReference import BibleReference
import logging

def connect_to_mysql():
	db_server = readini.get_ini_value('database', 'server')
	db_user = readini.get_ini_value('database', 'user')
	db_password = readini.get_ini_value('database', 'password')
	db_name = readini.get_ini_value('database', 'database')

	return mysql.connect(db_server, db_user, db_password, db_name)

def process_newPosts(site_name, from_date, sepost_process_function, se_post_save_function):

	# !-My9VsefIqes2OA9EyxQhzUNuqNvraT4i - requires authentication
	# !2.5sIHWRk9kld4Sb1Qn6N - no title
	# !BJyHsUt9WLl9dRFPUz(Uyr874YYvNH

	npage = 1
	has_more_pages = True

	while has_more_pages:
		se_api_url = 'http://api.stackexchange.com/posts?fromdate={0}&order=asc&sort=creation&filter=!BJyHsUt9WLl9dRFPUz(Uyr874YYvNH&site={1}&page={2}&pagesize=100'.format(from_date, site_name, npage)
		logging.info( "Retrieving SE posts at {0}".format(se_api_url) )
		r = requests.get(se_api_url)

		if (r.status_code == 200):
			se_posts = json.loads(r.text)
			has_more_pages = se_posts['has_more']

			for post in se_posts['items']:
				found_refs = sepost_process_function(post)
				se_post_save_function(post, found_refs)

		#Wait in order to stay until rate limiting.  The real problem is the biblia api, which stops me at 5000.
		#Since I'm doing somewhere near 200 requests per 100 se_posts, and I can do no more than 30 batches per hour, I will wait 2 minutes between batches.
		if has_more_pages:
			logging.info( "===========================================")
			logging.info( "Waiting so as not to exceed API threshholds")
			logging.info( "===========================================")
			time.sleep(20)

		npage += 1

def locate_references(se_post):

	refparser_url = "http://api.biblia.com/v1/bible/scan/?"
	se_body = se_post['body'].replace(u"\u2014", "-").replace(u"\u2013", "-").replace(u"\u2019", "'").encode('ascii', 'ignore')
	se_body = se_body.replace('"','')

	nchunk_start=0
	nchunk_size=1500
	found_refs = []

	while nchunk_start < len(se_body):
		body_chunk = se_body[nchunk_start:nchunk_size]
		if (len(body_chunk.strip())<4):
			break;

		refparser_params = {'text': body_chunk, 'key': biblia_apikey }
		refparse = requests.get(refparser_url, params = refparser_params)

		if (refparse.status_code == 200):
			foundrefs = json.loads(refparse.text)
			for foundref in foundrefs['results']:
				foundref['textIndex'] += nchunk_start
				found_refs.append( foundref )  #['passage'].encode('utf-8')
		else:
			logging.warning( "Status Code {0}: Failed to retrieve valid parsing info at {1}".format(refparse.status_code, refparse.url))
			logging.warning( "  returned text is: =>{0}<=".format(reparse.text))

		nchunk_start += 1450
		#Note: I'm purposely backing up, so that I don't accidentally split a reference across chunks

		return found_refs

def save_post_to_mysql(se_post, found_refs):
	if not found_refs:
		logging.info( "No References located in post id #{0} at {1}".format(se_post['post_id'],se_post['link']))
		return

	con = connect_to_mysql()
	try:
		cur = con.cursor()
	except:
		logging.warning( "Unable to commit post {0} to database at {1}:".format(post_id, link))
		logging.warning( sys.exc_info())
		con.rollback()
		con.close()		
		return

	try:
		post_id = se_post['post_id']
		owner = se_post['owner']['display_name'].encode('utf-8')
		post_type = se_post['post_type'].encode('utf-8')[0]
		title = se_post['title'].replace(u"\u2014", "-").replace(u"\u2013", "-").replace(u"\u2019", "'").encode('utf-8')
		link = se_post['link'].encode('utf-8')
		score = se_post['score']
		body = se_post['body'].replace(u"\u2014", "-").replace(u"\u2013", "-").replace(u"\u2019", "'").encode('utf-8') 
		#TODO: Get the tagged version rather than the placed, then inject it, along with some CSS styles to highlight the found references...

		logging.info( "Inserting Post # {0} ({1})".format(post_id, title))
		qry_Insert_Post = "INSERT INTO concordance_sepost (sepost_id, owner, type, title, link, score, body) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=%s, body=%s"
		cur.execute(qry_Insert_Post, (post_id, owner, post_type, title, link, score, body, title, body))
	except:
		logging.warning( "Unable to commit post {0} to database at {1} using {2}:".format(post_id, link, qry_Insert_Post))
		logging.warning( sys.exc_info())
		con.rollback()
		con.close()		
		return

	try:
		qry_Clear_Refs = "DELETE FROM concordance_reference WHERE sepost_id=%s"
		cur.execute(qry_Clear_Refs, (post_id))
	except:
		logging.warning( "Unable to commit post {0} to database at {1} using {2}:".format(post_id, link, qry_Clear_Refs))
		logging.warning( sys.exc_info())
		con.rollback()
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
	except:
		logging.warning( "Unable to commit post {0} to database at {1}:".format(post_id, link))
		logging.warning( sys.exc_info())
		con.rollback()
		con.close()		
		return

	finally:
		con.close()

def main():
	for site_name in ['christianity', 'hermeneutics']:
		last_run_date = readini.get_last_run(site_name).strftime("%Y-%m-%d")

		logging.info("{0}.stackexchange.com last checked on {1}".format(site_name, last_run_date))
		process_newPosts(site_name, last_run_date, locate_references, save_post_to_mysql)

		readini.set_last_run(site_name)

biblia_apikey = readini.get_ini_value('keys', 'biblia_apikey')
log_file = readini.get_ini_value('logging', 'filename')
logging.basicConfig(filename=log_file, filemode='w', level=logging.INFO)
main()
