# -*- encoding: utf-8 -*-

import rub.parser

from pyopenmensa.feed import LazyBuilder


def render_meta():
	builder = LazyBuilder()
	for meal in rub.parser.download_menu():
		canteen.addMeal(*meal)


if __name__ == '__main__':
	pass