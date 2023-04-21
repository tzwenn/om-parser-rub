# -*- encoding: utf-8 -*-

import rub.feed

import os
import urllib.parse

from flask import Flask, jsonify, make_response, url_for
from flask.logging import create_logger

app = Flask(__name__)
app.url_map.strict_slashes = False

log = create_logger(app)

canteens = ('q-west', )

if 'BASE_URL' in os.environ:  # pragma: no cover
	base_url = urllib.parse.urlparse(os.environ.get('BASE_URL'))
	if base_url.scheme:
		app.config['PREFERRED_URL_SCHEME'] = base_url.scheme
	if base_url.netloc:
		app.config['SERVER_NAME'] = base_url.netloc
	if base_url.path:
		app.config['APPLICATION_ROOT'] = base_url.path


def canteen_not_found(canteen_name):
    log.warning('Canteen %s not found', canteen_name)
    message = f"Canteen '{canteen_name}' not found"
    return make_response(message, 404)


def _canteen_feed_xml(xml):
	response = make_response(xml)
	response.minetype = 'text/html'
	return response

def canteen_meta_feed_xml(canteen_key):
    menu_feed_url = url_for(
		'canteen_menu_feed',
		canteen_name=canteen_key,
		_external=True)
    xml = rub.feed.render_meta(menu_feed_url)
    return _canteen_feed_xml(xml)


@app.route('/canteens/<canteen_name>')
@app.route('/canteens/<canteen_name>/meta')
def canteen_meta_feed(canteen_name):
	if canteen_name not in canteens:
		return canteen_not_found(canteen_name)
	return canteen_meta_feed_xml(canteen_name)


@app.route('/canteens/<canteen_name>/menu')
def canteen_menu_feed(canteen_name):
	if canteen_name not in canteens:
		return canteen_not_found(canteen_name)

	xml = rub.feed.render_menu()
	return _canteen_feed_xml(xml)

@app.route('/')
@app.route('/canteens')
def canteen_index():
	key = 'q-west'
	return jsonify({
		key: url_for('canteen_meta_feed', canteen_name=key, _external=True)
		for key in canteens
	})


@app.route('/health_check')
def health_check():
	return make_response("OK", 200)