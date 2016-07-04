"""Functions for handling rate limits"""
import re

REGEX = re.compile(r'[tT]ry\s+again\s+in\s+(\d+)\s+([Mm]inute|[Ss]econd|[Hh]our)s?')
CONVERSIONS = {
	'second': lambda x: x,
	'minute': lambda x: x * 60,
	'hour': lambda x: x * 60 * 60
}


def rate_limit(exception):
	message = str(exception)
	seconds = _get_rate_limit_seconds(message)
	return seconds


def _get_rate_limit_seconds(message):
	matcher = REGEX.search(message)
	if matcher is None:
		print 'could not determine rate-limit (defaulting to 10 minutes): %s' % str(message)
		return 600

	unit = matcher.group(2).lower()
	amount = int(matcher.group(1))

	if unit not in ['hour', 'minute', 'second']:
		print 'unknown rate limit unit (defaulting to 10 minutes): %s (%s)' % (unit, str(message))
		return 600

	return CONVERSIONS[unit](amount)
