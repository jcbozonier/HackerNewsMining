import urllib2, cookielib
from bs4 import BeautifulSoup
from hn import HN
from datetime import datetime
import json
import os
import time

def download_story(story_id, url, sleep_time = 1):
	story_file_path = './stories/' + str(story_id) + '.html'
	if not os.path.exists(story_file_path):
		print "Downloading story " + str(story_id) + " from url " + url
		print "Sleeping for " + str(sleep_time) + " seconds."
		try:
			cj = cookielib.CookieJar()
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
			opener.addheaders = [('User-agent', 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25')]
			story_response = opener.open(url)
			#print(story_response.info())
			story_text = story_response.read()
			story_response.close()
			story_file = open(story_file_path, 'w')
			story_file.write(story_text)
		except Exception, err:
			print err
			time.sleep(sleep_time)
			if sleep_time >= 4:
				return
			download_story(story_id, url, sleep_time = sleep_time*2)

def update_via_hn(sleep_time = 1):
	current_time = datetime.now()
	data_file_path = './article_metadata/today.json'
	data_file = open(data_file_path, 'a')
	hackernews = HN()
	
	try:
		front_page_stories = hackernews.get_stories()
		new_stories = hackernews.get_stories(story_type='newest')
	except Exception, err:
		if sleep_time <= 8:
			print err
			time.sleep(sleep_time)
			update_via_hn(sleep_time = sleep_time*2)
		return

	for story in front_page_stories:
		story['is_front_page'] = True
		story['timestamp'] = str(current_time)
		data_file.write(json.dumps(story) + '\n')
		download_story(story['story_id'], story['link'])
	for story in new_stories:
		story['is_front_page'] = False
		story['timestamp'] = str(current_time)
		data_file.write(json.dumps(story) + '\n')
		download_story(story['story_id'], story['link'])

def begin_regular_updates():
	while True:
		print "Refreshing HN data..."
		update_via_hn()
		print "Sleeping for 1 minute."
		time.sleep(60)

begin_regular_updates()