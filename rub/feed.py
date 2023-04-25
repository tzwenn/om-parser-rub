# -*- encoding: utf-8 -*-

import rub.parser
import rub.canteens

from pyopenmensa.feed import LazyBuilder


def build_menu(canteen_key):
	builder = LazyBuilder()
	parser = rub.canteens.canteens[canteen_key].parser_class(canteen_key)
	for date, category, title, notes, prices in rub.parser.download_menu():
		builder.addMeal(
			date=date,
			category=category,
			name=title,
			notes=notes,
			prices=prices
		)
	return builder


def render_menu(canteen_key):
	builder = build_menu(canteen_key)
	return builder.toXMLFeed()


def render_meta(canteen_key, menu_feed_url):
	builder = LazyBuilder()

	canteen = rub.canteens.canteens[canteen_key]
	
	builder.name = canteen.name
	builder.address = canteen.address
	builder.city = canteen.city

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
