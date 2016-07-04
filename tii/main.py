"""ThisImageIs main script"""
import json
import sys
import time

from tii.reddit import RedditBot
from tii.rcgenv.batch import BatchRecognizer


def main():
	config = None
	with file(sys.argv[1]) as cnffd:
		config = json.load(cnffd)

	recognizer = BatchRecognizer('/tmp/tii-recognizer')

	bot = RedditBot(config)
	bot.subscribe('test', 'funny', 'pics', 'mildlyinteresting')

	while True:
		for r in recognizer.recognize(bot.get_new_images()):
			print repr(r)
		time.sleep(10)


if __name__ == '__main__':
	main()
