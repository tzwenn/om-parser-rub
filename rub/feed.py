# -*- encoding: utf-8 -*-

import rub.parser
import rub.canteens

from pyopenmensa.feed import LazyBuilder


def build_menu(canteen_key):
	builder = LazyBuilder()
	parser = rub.canteens.canteens[canteen_key].parser_class(canteen_key)
	for date, category, title, notes, prices in parser.download_menu():
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
	builder.location(*map(str, (canteen.longitude, canteen.latitude)))

	builder.define(
		name='full',
		priority=0,
		url=menu_feed_url,
		source=None,
		dayOfWeek='*',
		dayOfMonth='*',
		hour="2-18/2",
		minute="13",
		retry='30 3',
	)

	return builder.toXMLFeed()
