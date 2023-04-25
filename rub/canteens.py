# -*- encoding: utf-8 -*-

from collections import namedtuple

import rub.parser

Canteen = namedtuple('Canteen', 'parser_class name address city latitude longitude')

canteens = {
	'q-west': Canteen(
		rub.parser.RubQWestParser,
		'Q-West Ruhr-Universität Bochum',
		'M-Südstraße, 44801 Bochum',
		'Bochum',
		51.44408440826269,
		7.258830686304531,
	),
	'ruhr-universitaet-bochum': Canteen(
		rub.parser.RubAkafoeParser,
		'AKAFÖ Mensa Ruhr-Universität Bochum',
		'Universitätsstraße 150, 44801 Bochum',
		'Bochum',
		51.44310140155152,
		7.262401913336785,
	),
	'rote-bete': Canteen(
		rub.parser.RubAkafoeParser,
		'Rote Bete Ruhr-Universität Bochum',
		'Universitätsstraße 150, 44801 Bochum',
		'Bochum',
		51.442954283080546,
		7.262558324989616,
	),
	'hochschule-bochum': Canteen(
		rub.parser.RubAkafoeParser,
		'AKAFÖ Mensa Hochschule Bochum',
		'Lennershofstraße 1540, 44801 Bochum',
		'Bochum',
		51.44626433404547,
		7.271747653258097,
	),
}
