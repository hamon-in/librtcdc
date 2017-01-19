all:
	pip install cython
	cd ../src/ && make && cd ..
	python setup.py build_ext -i
test:
	export LD_LIBRARY_PATH=../src/vendor/build && python example.py
