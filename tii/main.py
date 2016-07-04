"""ThisImageIs main script"""
import json
import sys
import time

from tii.reddit import RedditBot


def main():
	config = None
	with file(sys.argv[1]) as cnffd:
		config = json.load(cnffd)

	bot = RedditBot(config)
	bot.subscribe('test', 'funny', 'pics', 'mildlyinteresting')

	while True:
		for sub, url in bot.get_new_images():
			print '%s: %s' % (sub.subreddit, url)
		time.sleep(2)


if __name__ == '__main__':
	main()
