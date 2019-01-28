
package		= astrolib

##	Installation.

all:  setup conda-build conda-install

setup:
	python3 setup.py install --single-version-externally-managed --record=record.txt

conda-build:
	conda-build .

conda-install:
	conda install --use-local astrolib

##	Updating.

update:
	#git add -A;
	#git commit -m "updating";
	#git push;
	conda update --use-local ${package};

##	Housekeeping.

clean:
	rm -r astrolib.egg-info;
	rm -r build;
	rm record.txt;

