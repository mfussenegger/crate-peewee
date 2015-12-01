
from setuptools import setup, find_packages


setup(
    name='crate-peewee',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    platforms=['any'],
    install_requires=[
        'crate',
        'peewee'
    ]
)
