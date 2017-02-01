# setup.py
# Copyright (c) 2015 Xiaohan Song <chef@dark.kitchen>
# This file is licensed under a BSD license.

from setuptools import setup, find_packages

setup(name = "pyrtcdc",
      version = "0.1",
      packages = find_packages(),
      setup_requires=["cffi>=1.0.0"],
      cffi_modules=["pyrtcdc_build.py:ffibuilder"],
      install_requires = ["cffi>=1.0.0"],
      author = "Labeeb Ibrahim, Mohammed Irfan",
      author_email = "labeeb@hamon.in, irfan@hamon.in",
      description = "Python bindings for the librtcdc library using Out of line API mode of CFFI",
      url = "http://github.com/hamon-n/librtcdc",
      )

