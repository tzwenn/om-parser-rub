# -*- encoding: utf-8 -*-

from collections import namedtuple

import rub.parser

Canteen = namedtuple('Canteen', 'parser_class name address city')

canteens = {
	'q-west': Canteen(
		rub.parser.RubQWestParser,
		'Q-West Ruhr-Universität Bochum',
		'M-Südstraße',
		'44801 Bochum',
	),
	'ruhr-universitaet-bochum': Canteen(
		rub.parser.RubAkafoeParser,
		'AKAFÖ Mensa Ruhr-Universität Bochum',
		'Universitätsstraße 150',
		'44801 Bochum',
	),
	'rote-bete': Canteen(
		rub.parser.RubAkafoeParser,
		'Rote Bete Ruhr-Universität Bochum',
		'Universitätsstraße 150',
		'44801 Bochum',
	),
	'hochschule-bochum': Canteen(
		rub.parser.RubAkafoeParser,
		'AKAFÖ Mensa Hochschule Bochum',
		'Lennershofstraße 1540',
		'44801 Bochum',
	),
}
