# -*- coding: utf-8 -*-
#In order to figure out why the found reference indexes aren't matching up, I need to isolate a single post.
#Call locate_references
import requests
import pprint
import json
import sys


biblia_apikey = 'ea842c369c1e41ac8c433e088f3dee79'

refparser_url = "http://api.biblia.com/v1/bible/scan/?"
se_body = "&gt; Genesis 2:2 וַיְכַל אֱלֹהִים בַּיֹּום הַשְּׁבִיעִי מְלַאכְתֹּו אֲשֶׁר עָשָׂה וַיִּשְׁבֹּת בַּיֹּום הַשְּׁבִיעִי מִכָּל־מְלַאכְתֹּו אֲשֶׁר עָשָֽׂה׃ The word translated as &quot;rest&quot; in English, is actually the conjugated word from which we get the English word `Sabbath`, which actually means to &quot;cease doing&quot;. &gt; וַיִּשְׁבֹּת or by its root: &gt; שָׁבַת Here&#39;s BlueletterBible&#39;s concordance entry: [Strong&#39;s H7673][1] It is actually the same root word that is conjugated to mean &quot;[to go on strike][2]&quot; in modern Hebrew. In Genesis it is used to refer to the fact that the creation process ceased, not that God &quot;rested&quot; in the sense of relieving exhaustion, as we would normally understand the term in English. The word &quot;rest&quot; in that sense is &gt; נוּחַ Which can be found in Genesis 8:9, for example (and is also where we get Noah&#39;s name). More here: [Strong&#39;s H5117][3] Jesus&#39; words are in reference to the fact that God is always at work, as the psalmist says in Psalm 54:4, He is the sustainer, something that implies a constant intervention (a &quot;work&quot; that does not cease). The institution of the Sabbath was not merely just so the Israelites would &quot;rest&quot; from their work but as with everything God institutes in the Bible, it had important theological significance (especially as can be gleaned from its prominence as one of the 10 commandments). The point of the Sabbath was to teach man that he should not think he is self-reliant (cf. instances such as Judges 7) and that instead they should rely upon God, but more specifically His mercy. The driving message throughout the Old Testament as well as the New (and this would be best extrapolated in c.se) is that man cannot, by his own efforts (&quot;works&quot;) reach God&#39;s standard: &gt; Ephesians 2:8 For by grace you have been saved through faith, and that not of yourselves; it is the gift of God, 9 not of works, lest anyone should boast. The Sabbath (and the penalty associated with breaking it) was a way for the Israelites to weekly remember this. See Hebrews 4 for a more in depth explanation of this concept. So there is no contradiction, since God never stopped &quot;working&quot;, being constantly active in sustaining His creation, and as Jesus also taught, the Sabbath was instituted for man, to rest, but also, to &quot;stop doing&quot; and remember that he is not self-reliant, whether for food, or for salvation. Hope that helps. [1]: http://www.blueletterbible.org/lang/lexicon/lexicon.cfm?Strongs=H7673&amp;t=KJV [2]: http://www.morfix.co.il/%D7%A9%D7%91%D7%99%D7%AA%D7%94 [3]: http://www.blueletterbible.org/lang/lexicon/lexicon.cfm?strongs=H5117&amp;t=KJV"
#se_body = se_body.decode('utf-8')

nchunk_start=0
nchunk_size=1000
found_refs = []

while nchunk_start < len(se_body):
	body_chunk = se_body[nchunk_start:nchunk_size]

	refparser_params = {'text': body_chunk, 'key': biblia_apikey }
	print refparser_params
	headers = {'content-type': 'text/plain; charset=utf-8', 'Accept-Encoding': 'gzip,deflate,sdch'}

	refparse = requests.get(refparser_url, params = refparser_params, headers=headers)

	if (refparse.status_code == 200):
		foundrefs = json.loads(refparse.text)
		for foundref in foundrefs['results']:
			foundref['textIndex'] += nchunk_start
			found_refs.append( foundref )  #['passage'].encode('utf-8')
	else:
		print "Status Code {0}: Failed to retrieve valid parsing info at {1}".format(refparse.status_code, refparse.url)
		print "  returned text is: =>{0}<=".format(refparse.text)

	nchunk_start += (nchunk_size-50)
	#Note: I'm purposely backing up, so that I don't accidentally split a reference across chunks


for ref in found_refs:
	print ref
	print se_body[ref['textIndex']:ref['textIndex']+ref['textLength']]