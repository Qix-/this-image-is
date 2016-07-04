"""ThisImageIs main script"""
import json
import sys

from tii.reddit import RedditBot


def main():
	config = None
	with file(sys.argv[1]) as cnffd:
		config = json.load(cnffd)

	bot = RedditBot(config)


if __name__ == '__main__':
	main()
