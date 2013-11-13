import urllib2, cookielib
from bs4 import BeautifulSoup
from hn import HN
from datetime import datetime
import json
import os
import time

def download_story(story_id, url, date_code, sleep_time = 1):
	stories_folder_path = './stories/' + date_code
	try:
		os.makedirs(stories_folder_path)
	except:
		""" Nothing """
	story_file_path = stories_folder_path + '/' + str(story_id) + '.html'
	if not os.path.exists(story_file_path):
		print "Downloading story " + str(story_id) + " from url " + url
		try:
			cj = cookielib.CookieJar()
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
			opener.addheaders = [('User-agent', 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25')]
			story_response = opener.open(url, timeout=5)
			#print(story_response.info())
			story_text = story_response.read()
			story_response.close()
			story_file = open(story_file_path, 'w')
			story_file.write(story_text)
		except Exception, err:
			print err
			print "Sleeping for " + str(sleep_time) + " seconds."
			time.sleep(sleep_time)
			if sleep_time >= 4:
				return
			download_story(story_id, url, date_code, sleep_time = sleep_time*2)

def update_via_hn(sleep_time = 1):
	current_time = datetime.now()
	date_code = current_time.strftime('%Y%m%d')
	data_file_path = './story_metadata/story_log_' + date_code + '.json'
	data_file = open(data_file_path, 'a')
	hackernews = HN()
	
	try:
		print "Getting front page stories..."
		front_page_stories = hackernews.get_stories()
		print "Getting new stories..."
		new_stories = hackernews.get_stories(story_type='newest')
	except Exception, err:
		if sleep_time <= 8:
			print err
			time.sleep(sleep_time)
			update_via_hn(sleep_time = sleep_time*2)
		return

	print "Logging story statuses"
	for story in front_page_stories:
		story['is_front_page'] = True
		story['timestamp'] = str(current_time)
		data_file.write(json.dumps(story) + '\n')
		download_story(story['story_id'], story['link'], date_code)
	for story in new_stories:
		story['is_front_page'] = False
		story['timestamp'] = str(current_time)
		data_file.write(json.dumps(story) + '\n')
		download_story(story['story_id'], story['link'], date_code)

def begin_regular_updates(minutes_interval=1):
	try:
		os.makedirs('./stories')
	except:
		print "Stories directory already exists"

	try:
		os.makedirs('./story_metadata')
	except:
		print "Story metadata directory already exists"

	while True:
		print "Refreshing HN data..."
		update_via_hn()
		print "Sleeping for " + str(minutes_interval) + " minutes."
		time.sleep(minutes_interval*60)

begin_regular_updates()