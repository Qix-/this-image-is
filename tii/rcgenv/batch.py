"""A captioner implementation that batch-processes new images.

In the future, this could be switched out with a streaming implementation
that doesn't require the image recognition framework to boot up each time
for potentially sizable speed increases."""
import glob
import os
import re
import requests
import shutil
import subprocess
from urlparse import urlparse

from tii.reddit import RedditBot


class BatchRecognizer(object):
	REGEX = re.compile(r'^cp\s+"([^"]+)"\s+(?:(?:[^\/\r\n]+)(?:\/[^\/\r\n]+)*)(?:\r?\n)+image \d+:\s+?(.+)$', re.M)

	def __init__(self, root_dir):
		self._root = root_dir

		# find the model
		results = glob.glob('./env/*.t7')
		if len(results) < 1:
			raise Exception('didn\'t find model in env/')
		elif len(results) > 1:
			raise Exception('found more than one model in env/')
		self._model = os.path.abspath(results[0])
		print 'using model %s' % self._model

	def recognize(self, urls):
		# set up a session (empty object)
		session = {}

		# clean directory if necessary
		if os.path.exists(self._root):
			shutil.rmtree(self._root)
		os.makedirs(self._root)

		# create a reverse map of filenames urls
		for submission, url in urls:
			urll = urlparse(url)
			_, ext = os.path.splitext(urll.path)
			filepath = os.path.join(self._root, submission.name) + ext

			session[filepath] = submission

			headers = {'User-Agent': RedditBot.USER_AGENT}
			response = requests.get(url=url, headers=headers, stream=True)
			with file(filepath, 'wb') as out:
				response.raw.decode_content = True
				shutil.copyfileobj(response.raw, out)

		process = subprocess.Popen(['th', './eval.lua', '-model', self._model, '-image_folder', self._root, '-num_images', '-1', '-gpuid', '-1'], stdout=subprocess.PIPE, cwd='./ext/neuraltalk2')

		output = process.communicate()[0]

		# run recognizer
		matcher = BatchRecognizer.REGEX.finditer(output)

		# return parser generator
		def iter():
			for match in matcher:
				submission = session[match.group(1)]
				caption = match.group(2).strip()
				yield (submission, caption)
		return iter()
