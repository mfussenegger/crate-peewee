
from setuptools import setup, find_packages

try:
    with open('README.rst', 'r', encoding='utf-8') as f:
        readme = f.read()
except IOError:
    readme = ''

setup(
    name='crate-peewee',
    author='Mathias Fußenegger',
    author_email='pip@zignar.net',
    url='https://github.com/mfussenegger/crate-peewee',
    description='Crate driver for peewee',
    long_description=readme,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    platforms=['any'],
    install_requires=[
        'crate',
        'peewee'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    use_scm_version=True,
    setup_requires=['setuptools_scm']
)
