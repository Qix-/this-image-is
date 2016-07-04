"""ThisImageIs main script"""
import json
import os
import shutil
import sys
import time

from tii.reddit import RedditBot
from tii.rcgenv.batch import BatchRecognizer

REC_PATH = '/tmp/tii-recognizer'


def main():
	config = None
	with file(sys.argv[1]) as cnffd:
		config = json.load(cnffd)

	# clear out any old tmp directory
	if os.path.exists(REC_PATH):
		shutil.rmtree(REC_PATH)
	os.makedirs(REC_PATH)

	recognizer = BatchRecognizer(REC_PATH)

	bot = RedditBot(config)
	bot.subscribe('test', 'funny', 'pics', 'mildlyinteresting')

	while True:
		recognizer.recognize(bot.get_new_images())
		time.sleep(10)


if __name__ == '__main__':
	main()
