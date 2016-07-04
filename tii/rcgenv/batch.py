"""A captioner implementation that batch-processes new images.

In the future, this could be switched out with a streaming implementation
that doesn't require the image recognition framework to boot up each time
for potentially sizable speed increases."""
import os
import requests
import shutil
from urlparse import urlparse

from tii.reddit import RedditBot


class BatchRecognizer(object):
	def __init__(self, root_dir):
		self._root = root_dir

	def recognize(self, urls):
		# set up a session (empty object)
		__session = {}

		# create a reverse map of filenames urls
		for submission, url in urls:
			urll = urlparse(url)
			_, ext = os.path.splitext(urll.path)
			filepath = os.path.join(self._root, submission.name) + ext

			__session[filepath] = submission
			headers = {'User-Agent': RedditBot.USER_AGENT}
			response = requests.get(url=url, headers=headers, stream=True)
			with file(filepath, 'wb') as out:
				response.raw.decode_content = True
				shutil.copyfileobj(response.raw, out)

		# run recognizer
		# return parser generator
