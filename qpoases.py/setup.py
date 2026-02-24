from setuptools import setup, Extension
import pybind11
from config import *


ext = Extension(
    'pyqpoases',
    sources=['wrapper.cpp'],
    include_dirs=[pybind11.get_include(), path2qpoases + 'include'],
    language='c++',
    library_dirs=library_dirs,
    libraries=['qpOASES', 'm'],
    extra_link_args=extra_link_args,
    extra_compile_args=extra_compile_args,
    runtime_library_dirs=['.', path2qpoases + 'bin']
)

setup(
    name='pyqpoases',
    version='0.1',
    ext_modules=[ext],
    zip_safe=False
)