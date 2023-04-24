# -*- encoding: utf-8 -*-

from abc import ABC, abstractmethod
import logging

from bs4 import BeautifulSoup
import requests

import pyopenmensa.feed

URL = 'https://q-we.st/speiseplan/'

MEAL_NAME_TEMPLATE = 'Angebot %d'
PRICE_ROLES = ('student', 'other')

LOG = logging.getLogger(__name__)

class RubParser(ABC):

	URL = None

	def __init__(self):
		pass


	@abstractmethod
	def parse_menu(self):
		pass


	def download_menu(self):
		request = requests.get(URL, timeout=30)
		soup = BeautifulSoup(request.text, 'html.parser')
		yield from self.parse_menu(soup)
		


class RubQWestParser(RubParser):
	
	def __init__(self):
		super().__init__()


	def parse_notes_block(self, notes_block_div):
		if not notes_block_div:
			return {}
		notes_list = [
			e.strip() for e in 
			notes_block_div.string.partition(': ')[2].split(',')
		]
		return {k.lstrip('('): v.strip() for k,v in (e.split(')', 2) for e in notes_list)}


	def parse_notes(self, notes_div):
		res = {}
		if notes_div:
			for block in notes_div.find_all('div', 'kennzeichen'):
				b = self.parse_notes_block(block)
				res.update(b)
		
		return res


	def parse_meal(self, meal_div):
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


	def parse_day(self, day_div):
		date_tag = day_div.find('span', 'live_speiseplan_title')
		if date_tag.string is None:
			return

		date = pyopenmensa.feed.extractDate(date_tag.string)
		meal_id = 0
		for meal_div in day_div.find_all('div', 'live_speiseplan_item'):
			m = self.parse_meal(meal_div)
			if m is not None:
				meal_id += 1
				yield date, MEAL_NAME_TEMPLATE % meal_id, *m


	def translate_notes(self, _date, _meal, _title, notes, _prices, notes_dict):
		return _date, _meal, _title, [notes_dict.get(n, n) for n in notes], _prices


	def parse_menu(self, soup):
		notes_dict = self.parse_notes(soup.find('div', 'live_speiseplan_kennzeichnung_content'))
		for day_div in soup.find_all('div', 'live_speiseplan_single_day'):
			yield from map(lambda t: self.translate_notes(*t, notes_dict), self.parse_day(day_div))


def download_menu():
	p = RubQWestParser()
	yield from p.download_menu()