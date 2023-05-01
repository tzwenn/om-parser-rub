# -*- encoding: utf-8 -*-

from abc import ABC, abstractmethod
import datetime
import logging
import re

import bs4
import requests

import pyopenmensa.feed

MEAL_NAME_TEMPLATE = 'Angebot %d'
PRICE_ROLES = ('student', 'other')

LOG = logging.getLogger(__name__)

class RubParser(ABC):

	URL = None
	NOTES_DIV_CLASS = None

	def __init__(self, *_placeholder_args):
		self.notes_dict = {}


	@abstractmethod
	def parse_menu(self):
		pass


	@abstractmethod
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
		self.soup = bs4.BeautifulSoup(request.text, 'html.parser')
		self.notes_dict = self.parse_notes(self.find_notes())
		yield from self.parse_menu()


class RubQWestParser(RubParser):
	
	URL = 'https://q-we.st/speiseplan/'
	NOTES_DIV_CLASS = 'kennzeichen'

	PRICE_SEP = '|'

	def __init__(self, *_placeholder_args):
		super().__init__(*_placeholder_args)


	def parse_meal(self, meal_div):
		title_span = meal_div.find('span', 'live_speiseplan_item_title')
		# All `live_speiseplan_item_title` entries that have a sub (thus no valid string), 
		# are actual entries and not the "table header". But the header
		# is a string, just not of importance
		if title_span.string is not None:
			return

		elements = list(title_span.stripped_strings)
		if len(elements) != 2:
			return
		title, notes_s = elements
		notes = self.translate_notes(notes_s.split(','))
		price_div = meal_div.find('span', 'live_speiseplan_item_price')
		prices = dict(zip(PRICE_ROLES, map(str.strip, price_div.string.split(self.PRICE_SEP))))
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

	URL_BASE = 'https://www.akafoe.de/gastronomie/speiseplaene-der-mensen/{}'

	NOTES_HEADING = 'Erläuterungen:'
	NOTES_DIV_CLASS = 'col-sm-4'

	PRICE_SEP = '/'


	def __init__(self, key):
		self.URL = self.URL_BASE.format(key)
		super().__init__()


	def find_notes(self):
		header = self.soup.find('h4', string=self.NOTES_HEADING)
		return header.find_next('div', 'row')


	def search_item_siblings(self, category_tag):
		current = category_tag
		while current := current.next_sibling:
			if not isinstance(current, bs4.element.Tag):
				continue
			if current.name == 'div' and 'item' in current.attrs.get("class", []):
				yield current
			else:
				break


	def parse_category(self, category_tag):
		category = category_tag.string

		for item_tag in self.search_item_siblings(category_tag):
			l = list(item_tag.find('h4').stripped_strings)
			title = (l or [''])[0]

			notes_s = item_tag.find('small').text.lstrip('(').rstrip(')')
			notes = self.translate_notes(notes_s.split(','))

			price_div = item_tag.find('div', 'price')
			if price_div is None or price_div.stripped_strings is None:
				prices = {}
			else:
				prices = dict(zip(PRICE_ROLES, map(str.strip, list(price_div.stripped_strings)[0].split(self.PRICE_SEP))))
			yield category, title, notes, prices


	def parse_day(self, date, day_div):
		for category_tag in day_div.find_all('h3'):
			for meal in self.parse_category(category_tag):
				yield date, *meal


	def fix_date(self, date_s):
		# The date string on the AKAFÖ site is missing the year.
		# We assume it is the current year and at wrap arounds,
		# (defined as more than half a year in the past), we add one year

		today = datetime.date.today()
		date = pyopenmensa.feed.extractDate(date_s.strip() + str(today.year))

		if (today - date).days > 365 / 2:
			return datetime.date(date.year + 1, date.month, date.day)
		else:
			return date


	def parse_menu(self):
		calender_div = self.soup.find('div', 'week')
		dates = [self.fix_date(date_tag.string) for date_tag in calender_div.find_all('div', 'day')]

		for date, day_div in zip(dates, self.soup.find_all('div', 'row', 'list-dish')):
			yield from self.parse_day(date, day_div)
