# -*- encoding: utf-8 -*-

import logging

from bs4 import BeautifulSoup
import requests

import pyopenmensa.feed

URL = 'https://q-we.st/speiseplan/'

MEAL_NAME_TEMPLATE = 'Angebot %d'
PRICE_ROLES = ('student', 'other')

LOG = logging.getLogger(__name__)

def parse_meal(meal_div):
	title_span = meal_div.find('span', 'live_speiseplan_item_title')
	# All `live_speiseplan_item_title` entries that have a sub (thus no valid string), 
	# are actual entries and not the "table header". But the header
	# is a string, just not of importance
	if title_span.string is not None:
		return

	title, notes_s = title_span.stripped_strings
	notes = [n for n in notes_s.split(',') if n]
	price_div = meal_div.find('span', 'live_speiseplan_item_price')
	prices = dict(zip(PRICE_ROLES, price_div.string.split(' | ')))
	return title, notes, prices


def parse_day(day_div):
	date_tag = day_div.find('span', 'live_speiseplan_title')
	if date_tag.string is None:
		return

	date = pyopenmensa.feed.extractDate(date_tag.string)
	meal_id = 0
	for meal_div in day_div.find_all('div', 'live_speiseplan_item'):
		m = parse_meal(meal_div)
		if m is not None:
			meal_id += 1
			yield date, MEAL_NAME_TEMPLATE % meal_id, *m


def download_menu():
	request = requests.get(URL, timeout=30)
	soup = BeautifulSoup(request.text, 'html.parser')
	for day_div in soup.find_all('div', 'live_speiseplan_single_day'):
		yield from parse_day(day_div)
