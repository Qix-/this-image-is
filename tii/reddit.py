"""Runs the Reddit bot"""
import json
import os
from os import path

import praw


class RedditBot(object):
	USER_AGENT = 'ThisImageIs daemon (by u/i-am-qix)'
	SESSFP = './tii-session.json'

	def __init__(self, config):
		self._access = None
		self._reddit = praw.Reddit(user_agent=RedditBot.USER_AGENT)
		self._reddit.set_oauth_app_info(**config.get('oauth'))

		# refresh access
		self._refresh_access()

		me = self._reddit.get_me()
		print 'signed into Reddit as %s' % me.name

	def _refresh_access(self, force_init=False):
		if force_init and path.isfile(RedditBot.SESSFP):
			os.unlink(RedditBot.SESSFP)

		if not path.isfile(RedditBot.SESSFP):
			# we have to init the bot.
			url = self._reddit.get_authorize_url('uniqueKey', 'identity', True)
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

			self._reddit.refresh_access_information(refresh_token)
