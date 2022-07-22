# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name='project',
    version='1.0',
    packages=find_packages(),
    package_data={'elixier': ['resources/*.json', 'templates/*.html']},
    entry_points={'scrapy': ['settings = elixier.settings']},
)
