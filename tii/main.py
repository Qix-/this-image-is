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
	while True:
		for p in bot._get_r_submissions('test'):
			print p.id
		time.sleep(2)


if __name__ == '__main__':
	main()
