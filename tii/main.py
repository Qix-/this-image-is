"""ThisImageIs main script"""
import json
import sys
import time
import traceback

from praw.errors import RateLimitExceeded
from tii.reddit import RedditBot
from tii.rcgenv.batch import BatchRecognizer


def main():
	config = None
	with file(sys.argv[1]) as cnffd:
		config = json.load(cnffd)

	recognizer = BatchRecognizer('/tmp/tii-recognizer')

	bot = RedditBot(config)
	bot.subscribe('test')

	while True:
		sleep_amount = 10
		try:
			bot.post_captions(recognizer.recognize(bot.get_new_images()))
		except RateLimitExceeded:
			print 'detected rate limit'
			sleep_amount = 8.5 * 60
		except:
			print traceback.format_exc()
			print 'sleeping for a few minutes to recover...'
			sleep_amount = 3 * 60
		finally:
			if bot.backlog > 0:
				print 'comment backlog: %d' % bot.backlog

		time.sleep(sleep_amount)

if __name__ == '__main__':
	main()
