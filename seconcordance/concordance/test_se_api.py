import requests
import json
import pprint

def get_post_by_id(site_name, post_num):
	#se_api_url = 'http://api.stackexchange.com/posts?{0}&filter=!BJyHsUt9WLl9dRFPUz(Uyr874YYvNH&site={1}'.format(post_num, site_name)

	se_api_url = 'http://api.stackexchange.com/questions/{0}?filter=!BJyHsUt9WLl9dRFPUz(Uyr874YYvNH&site={1}'.format(post_num, site_name)
	print se_api_url

	headers = {
		'Accept-Encoding':'utf-8',
		'content-type': 'application/json'
	}

	r = requests.get(se_api_url, headers=headers)

	if (r.status_code == 200):
		print r.headers

		all_posts = json.loads(r.text)
		se_post = all_posts['items'][0]
		#se_post = all_posts

		pprint.pprint(se_post)

		#post_id = se_post['post_id']
		owner = se_post['owner']['display_name'].encode('utf-8')
		pprint.pprint(owner)

		#post_type = se_post['post_type'].encode('utf-8')[0]
		title = se_post['title'].encode('utf-8')	#.replace(u"\u2014", "-").replace(u"\u2013", "-").replace(u"\u2019", "'")
		#title = se_post['title'].encode('ascii',errors='ignore')
		pprint.pprint(title)

		link = se_post['link'].encode('utf-8')
		score = se_post['score']
		#body = se_post['body'].encode('utf-8').replace('\'', '\\\'') 

		#pprint.pprint(se_post)
		#pprint.pprint(body)

get_post_by_id('hermeneutics', 7519)