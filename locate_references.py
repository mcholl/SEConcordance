import requests
import json
import ConfigParser
from datetime import date, datetime, tzinfo, timedelta, time


def process_newPosts(site_name, from_date, sepost_process_function, se_post_save_function):

	# !-My9VsefIqes2OA9EyxQhzUNuqNvraT4i - requires authentication
	# !2.5sIHWRk9kld4Sb1Qn6N - no title
	# !BJyHsUt9WLl9dRFPUz(Uyr874YYvNH

	se_api_url = 'http://api.stackexchange.com/posts?fromdate={0}&order=desc&sort=creation&filter=!BJyHsUt9WLl9dRFPUz(Uyr874YYvNH&site={1}'.format(from_date, site_name)
	r = requests.get(se_api_url)

	if (r.status_code == 200):
		se_posts = json.loads(r.text)
		for post in se_posts['items']:
			found_refs = sepost_process_function(post)
			se_post_save_function(post, found_refs)

def locate_references(se_post):

	refparser_url = "http://api.biblia.com/v1/bible/scan/?"
	se_body = se_post['body'].encode('utf-8')
	se_body = se_body.replace('"','')

	nchunk_start=0
	nchunk_size=1600
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
				found_refs.append( foundref['passage'].encode('utf-8') )
		else:
			print refparse.status_code
			print refparse.url
		

		nchunk_start += 1500
		#Note: I'm purposely backing up, so that I don't accidentally split a reference across chunks

		return found_refs

def save_post_to_mysql(se_post, found_refs):
	if not found_refs:
		#print "No References found"
		return

	post_id = se_post['post_id']
	owner = se_post['owner']['display_name'].encode('utf-8')
	post_type = se_post['post_type'].encode('utf-8')[0]
	title = se_post['title'].encode('utf-8')
	link = se_post['link'].encode('utf-8')
	score = se_post['score']
	body = se_post['body'].encode('utf-8') #TODO: Get the tagged version rather than the placed.

	qry_Insert_Post = "INSERT INTO post (sepost_id, owner, type, title, link, score, body) VALUES ({0}, '{1}', '{2}', '{3}', '{4}', {5}, '{6}')".format(post_id, owner, post_type, title, link, score, '<body>' )
	print qry_Insert_Post

	for found in found_refs:
		ref_startbook_num, ref_startchapter_num, ref_startverse_num, ref_endchapter_num, ref_endverse_num = serialize_reference(found)
		qry_Insert_Ref = "INSERT INTO foundrefs (sepost_id, reference, ref_startbook_num, ref_startchapter_num, ref_startverse_num, ref_endchapter_num, ref_endverse_num) VALUES ('{0}', '{1}');".format(post_id, found)
		print qry_Insert_Ref

	pass

def serialize_reference(verse):
	#Given something like "1 Corinthians 12 - 13:4", returns enough information so it can all be easily sorted
	# ref.startbook_num, ref.startchapter_num, ref.startverse_num, ref.endchapter_num, ref.endverse_num
	#Note: I specifically am not going to handle references that go beyond the boundaries of a book

	pass 

def get_last_run(site_name):
    config = ConfigParser.ConfigParser()
    config.read(ini_file)
    if 'last_run' not in config.sections():
        cfg = open(ini_file,'w')
        config.add_section('last_run')
        config.write(cfg)
        cfg.close()
    
    try:
    	lr = config.get('last_run', site_name)
    except ConfigParser.NoOptionError:
    	print "No default set"
        lr= 'Jan 1 1970 12:00'

    return datetime.strptime(lr, "%b %d %Y %H:%M")

def set_last_run(site_name):
    config = ConfigParser.ConfigParser()
    config.read(ini_file)
    
    cfg = open(ini_file,'w')
    last_run = config.set('last_run', site_name, datetime.now().strftime("%b %d %Y %H:%M"))
    config.write(cfg)
    cfg.close()

def get_ini_value(section, key_name):
    config = ConfigParser.ConfigParser()
    config.read(ini_file)
    return config.get(section, key_name)

ini_file = 'seconcord.ini'

biblia_apikey = get_ini_value('keys', 'biblia_apikey')

refr = serialize_reference("1 Corinthians 13:4-7")
print vars(refr)

#process_newPosts('christianity', '2014-02-24', locate_references, save_post_to_mysql)

# for site_name in ['christianity', 'hermeneutics']:
# 	last_run_date = get_last_run(site_name).strftime("%Y-%m-%d")

# 	print "{0}.stackexchange.com last checked on {1}".format(site_name, last_run_date)
# 	process_newPosts(site_name, last_run_date, locate_references, save_post_to_mysql)

# 	set_last_run(site_name)
