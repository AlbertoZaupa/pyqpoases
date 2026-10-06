from setuptools import setup, Extension
import pybind11
from config import *

wrapper_dir = Path(__file__).resolve().parent


ext = Extension(
    'pyqpoases',
    sources=[str(wrapper_dir / 'wrapper.cpp')],
    include_dirs=[pybind11.get_include(), path2qpoases + 'include'],
    language='c++',
    library_dirs=library_dirs,
    libraries=['qpOASES', 'm'],
    extra_link_args=extra_link_args,
    extra_compile_args=extra_compile_args,
    runtime_library_dirs=['$ORIGIN'] if OS == 'Linux' else library_dirs
)

setup(
    name='pyqpoases',
    version='0.1',
    ext_modules=[ext],
    options={'build_ext': {'build_lib': path2qpoases + 'bin'}},
    zip_safe=False
)
