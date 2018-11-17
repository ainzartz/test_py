PROJECT = $(shell pwd)

SOURCE  = $(PROJECT)/src
BINARY  = $(PROJECT)/udta-server
LOG     = $(PROJECT)/logs

all: clean
	cd $(SOURCE) &&\
	   zip -rv $(BINARY).zip * &&\
	   echo "#!$(shell which python3.4)" > $(BINARY) &&\
	   cat $(BINARY).zip >> $(BINARY)
	rm -fv $(BINARY).zip
	chmod u+x -v $(BINARY)

run:
	python $(SOURCE) || true

test:
	python $(SOURCE) --test

clean:
	rm -rfv $(LOG)
	rm -fv $(BINARY)
	find $(SOURCE) \
	     -type f \
	     -iname "*.py[oc]" \
	     -exec rm -fv "{}" \;
	find $(SOURCE) \
	     -type d \
	     -name "__pycache__" \
	     -exec rm -rfdv "{}" \; ||\
	     true
