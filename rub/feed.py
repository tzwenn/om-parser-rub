# -*- encoding: utf-8 -*-

import rub.parser

from pyopenmensa.feed import LazyBuilder


def build_menu():
	builder = LazyBuilder()
	for meal in rub.parser.download_menu():
		date, category, title, notes, prices = meal
		builder.addMeal(
			date=date,
			category=category,
			name=title,
			notes=notes,
			prices=prices
		)
	return builder


def render_menu():
	builder = build_menu()
	return builder.toXMLFeed()


def render_meta(menu_feed_url):
	builder = LazyBuilder()
	
	builder.name = 'Q-West Ruhr-Universität Bochum'
	builder.address = 'Universitätsstraße 150'
	builder.city = '44801 Bochum'

	builder.define(
		name='full',
		priority=0,
		url=menu_feed_url,
		source=None,
		dayOfWeek='*',
		dayOfMonth='*',
		hour="8-18",
		minute="23",
		retry='30 1',
	)

	return builder.toXMLFeed()
