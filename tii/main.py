"""ThisImageIs main script"""
import json
import sys
import time
import traceback

from praw.errors import RateLimitExceeded
from tii.ratelimit import rate_limit
from tii.reddit import RedditBot
from tii.rcgenv.batch import BatchRecognizer


def main():
	config = None
	with file(sys.argv[1]) as cnffd:
		config = json.load(cnffd)

	recognizer = BatchRecognizer('/tmp/tii-recognizer')

	bot = RedditBot(config)
	bot.subscribe(*config.get('subscriptions'))

	while True:
		sleep_amount = 10
		try:
			bot.post_captions(recognizer.recognize(bot.get_new_images()))
		except RateLimitExceeded as e:
			print 'detected rate limit (%s)' % str(e)
			sleep_amount = rate_limit(e)
			print 'sleeping for %d seconds...' % sleep_amount
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
