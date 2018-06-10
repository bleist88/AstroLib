
package		= astrolib

##	Installation.

all:  setup conda-build conda-install

setup:
	python setup.py install --single-version-externally-managed --record=record.txt

conda-build:
	conda-build .

conda-install:
	conda install --use-local astrolib

##	Updating.

update:
	conda update --use-local ${package};

push:
	git add -A;
	git commit -m "updating";
	git push;

##	Housekeeping.

clean:
	rm -r astrolib.egg-info;
	rm -r build;
	rm record.txt;
