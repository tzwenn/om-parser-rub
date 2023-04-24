# -*- encoding: utf-8 -*-

from abc import ABC, abstractmethod
import logging
import re

from bs4 import BeautifulSoup
import requests

import pyopenmensa.feed

MEAL_NAME_TEMPLATE = 'Angebot %d'
PRICE_ROLES = ('student', 'other')

LOG = logging.getLogger(__name__)

class RubParser(ABC):

	URL = None
	NOTES_DIV_CLASS = None

	def __init__(self):
		self.notes_dict = {}

	@abstractmethod
	def parse_menu(self):
		pass


	def find_notes(self):
		pass


	def translate_notes(self, notes_l):
		return [self.notes_dict.get(n, n) for n in notes_l if n]


	def parse_notes_block(self, notes_block_div):
		if not notes_block_div:
			return {}
		text = re.sub('\s+' ,' ' , ''.join(notes_block_div.stripped_strings))
		notes_list = [
			e.strip() for e in 
			text.partition(': ')[2].split(',')
		]
		return {k.strip().lstrip('('): v.strip() for k,v in (e.split(')', 1) for e in notes_list)}


	def parse_notes(self, notes_div):
		res = {}
		if notes_div:
			for block in notes_div.find_all('div', self.NOTES_DIV_CLASS):
				b = self.parse_notes_block(block)
				res.update(b)
		
		return res


	def download_menu(self):
		request = requests.get(self.URL, timeout=30)
		self.soup = BeautifulSoup(request.text, 'html.parser')
		self.notes_dict = self.parse_notes(self.find_notes())
		yield from self.parse_menu()


class RubQWestParser(RubParser):
	
	URL = 'https://q-we.st/speiseplan/'
	NOTES_DIV_CLASS = 'kennzeichen'

	def __init__(self):
		super().__init__()


	def parse_meal(self, meal_div):
		title_span = meal_div.find('span', 'live_speiseplan_item_title')
		# All `live_speiseplan_item_title` entries that have a sub (thus no valid string), 
		# are actual entries and not the "table header". But the header
		# is a string, just not of importance
		if title_span.string is not None:
			return

		title, notes_s = title_span.stripped_strings
		notes = self.translate_notes(notes_s.split(','))
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


	def find_notes(self):
		return self.soup.find('div', 'live_speiseplan_kennzeichnung_content')

	
	def parse_menu(self):
		for day_div in self.soup.find_all('div', 'live_speiseplan_single_day'):
			yield from self.parse_day(day_div)


class RubAkafoeParser(RubParser):


	URL = 'https://www.akafoe.de/gastronomie/speiseplaene-der-mensen/ruhr-universitaet-bochum'

	NOTES_HEADING = 'Erläuterungen:'
	NOTES_DIV_CLASS = 'col-sm-4'


	def find_notes(self):
		header = self.soup.find('h4', string=self.NOTES_HEADING)
		return header.find_next('div', 'row')


	def parse_menu(self):
		return ()


def download_menu():
	p = RubAkafoeParser()
	#p = RubQWestParser()
	yield from p.download_menu()