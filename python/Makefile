.PHONY: all test stress

all:
	rm -rf pyrtcdc.so
	cd ../src/ && make && cd ..
	python pyrtcdc_build.py
test:
	export LD_LIBRARY_PATH=../src/vendor/build && python dc_test.py
stress:
	export LD_LIBRARY_PATH=../src/vendor/build && python stress_test.py

