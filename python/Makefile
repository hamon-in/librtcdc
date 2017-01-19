all:
	pip install cython
	CFLAGS="-I../src:-I../src/libnice/nice:-I../src/libnice/agent" LDFLAGS="-L../src/vendor/build" python setup.py build_ext -i
test:
	export LD_LIBRARY_PATH=../src/vendor/build && python example.py
