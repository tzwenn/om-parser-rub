APPNAME=rub.views

all: debug

run:
	flask --app $(APPNAME) run

debug:
	flask --app $(APPNAME) --debug run


.PHONY: run debug
