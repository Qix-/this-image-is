"""Runs the Reddit bot"""
import json
import os
from os import path
from urlparse import urlparse, urlunparse

import praw

SUPPORTED_EXTENSIONS = ['.jpg', '.png', '.gif']


def populate(template, **kwargs):
	for key, val in kwargs.iteritems():
		template = template.replace('{{%s}}' % key, str(val))
	return template


class RedditBot(object):
	USER_AGENT = 'ThisImageIs daemon (by u/i-am-qix)'
	SESSFP = './tii-session.json'

	def __init__(self, config):
		self._subreddit = {}
		self._subscriptions = set()
		self._comment_queue = []

		self._reddit = praw.Reddit(user_agent=RedditBot.USER_AGENT, log_requests=0, cache_timeout=10)  # XXX DEBUG TODO SET cache_timeout TO 120
		self._reddit.set_oauth_app_info(**config.get('oauth'))

		# refresh access
		self._refresh_access()

		me = self._reddit.get_me()
		print 'signed into Reddit as %s' % me.name

	def subscribe(self, *args):
		self._subscriptions |= set(args)

	def get_new_images(self):
		def filter():
			for link in self._get_new_links():
				urll = urlparse(link.url)
				base, ext = path.splitext(urll.path)
				if urll.scheme not in ['http', 'https']:
					continue
				if urll.netloc in ['www.imgur.com', 'imgur.com']:
					inetloc = 'i.imgur.com'
					ipath = '%s.png' % path.basename(urll.path)
					yield (link, urlunparse([urll.scheme, inetloc, ipath, None, None, None]))
				elif ext is not None and ext in SUPPORTED_EXTENSIONS:
					yield (link, link.url)
		return filter()

	def post_captions(self, pairs):
		template = ''
		with file('./template.txt', 'r') as templatefd:
			template = templatefd.read()

		for submission, caption in pairs:
			self._comment_queue.insert(0, (submission, caption))

		# the following block is to be as terse as possible
		# so that any RateLimiting exceptions that are raised
		# can be caught by the consumer and acted upon in an
		# appilcation specific way.
		to_hide = []
		try:
			while len(self._comment_queue) > 0:
				submission, caption = self._comment_queue[-1]
				content = populate(template, caption=caption)
				submission.add_comment(content)
				print '\x1b[1m%s\x1b[m -> %s' % (caption, submission.permalink)
				self._comment_queue.pop()
				to_hide.append(submission.name)
		finally:
			if len(to_hide) > 0:
				print 'hiding %d things' % len(to_hide)
				self._reddit.hide(to_hide)

	@property
	def backlog(self):
		return len(self._comment_queue)

	def _get_new_links(self):
		def filter():
			for submission in self._get_new_submissions():
				if not submission.is_self:
					yield submission
		return filter()

	def _get_new_submissions(self):
		def compose():
			for r in self._subscriptions:
				for ns in self._get_r_submissions(r):
					yield ns
		return compose()

	def _refresh_access(self, force_init=False):
		if force_init and path.isfile(RedditBot.SESSFP):
			os.unlink(RedditBot.SESSFP)

		if not path.isfile(RedditBot.SESSFP):
			# we have to init the bot.
			url = self._reddit.get_authorize_url('uniqueKey', ['identity', 'submit', 'report', 'read'], True)
			print 'Please visit the following URL and click allow. It will redirect you to a 404; the URL will have a `code` query param. Copy its value here.'
			print url
			code = raw_input('Code: ')

			print 'authorizing...'
			access_information = self._reddit.get_access_information(code.strip())

			print 'writing refresh token...'
			with file(RedditBot.SESSFP, 'w') as sessfp:
				sessfp.write(json.dumps(access_information.get('refresh_token')))

			print 'signing in'
			self._reddit.set_access_credentials(**access_information)

		else:
			# try to refresh the id
			print 'found existing refresh token; attempting to log in...'
			refresh_token = None
			with file(RedditBot.SESSFP) as sessfp:
				try:
					refresh_token = json.load(sessfp)
					if len(refresh_token.strip()) == 0:
						raise Exception()
				except:
					print 'invalid/missing token in session file; re-initing (requires user input)'
					return self._refresh_access(force_init=True)

			print 'refreshing access information...'
			access_information = self._reddit.refresh_access_information(refresh_token)

			print 'signing in'
			self._reddit.set_access_credentials(**access_information)

	def _get_r_submissions(self, r):
		if r not in self._subreddit:
			print 'initializing subreddit: %s' % r
			self._subreddit[r] = {'sub': self._reddit.get_subreddit(r)}

		sub = self._subreddit[r]

		# we create a wrapper generator here so we can hold the latest placeholder
		def wrap():
			place_holder = sub.get('place_holder')
			new = sub.get('sub').get_new(place_holder=place_holder)
			placed = False

			for submission in new:
				if submission.id == place_holder:
					continue
				if not placed:
					sub['place_holder'] = submission.id
					placed = True
				yield submission

		return wrap()
