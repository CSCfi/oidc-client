from setuptools import setup
from elixir_oauth2 import __license__, __version__, __author__, __description__


setup(name='elixir_oauth2',
      version=__version__,
      url='https://elixir-aai-oauth2-service.rtfd.io/',
      project_urls={
          'Source': 'https://github.com/CSCfi/elixir-aai-oauth2-service',
      },
      license=__license__,
      author=__author__,
      author_email='',
      description=__description__,
      long_description="",
      packages=['elixir_oauth2'],
      # If any package contains *.json, include them:
      package_data={'': ['*.json', '*.ini']},
      entry_points={
          'console_scripts': [
              'elixir-service=elixir_oauth2.server:main'
          ]
      },
      platforms='any',
      classifiers=[  # Optional
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 5 - Production/Stable',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Intended Audience :: Healthcare Industry',
          'Intended Audience :: Information Technology',
          'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
          'Topic :: Scientific/Engineering :: Bio-Informatics',

          # Pick your license as you wish
          'License :: OSI Approved :: Apache Software License',

          'Programming Language :: Python :: 3.6',
      ],
      install_requires=['aiohttp', 'asyncpg', 'python-jose[cryptography]',
                        'jsonschema==3.0.0', 'gunicorn'],
      extras_require={
          'test': ['coverage', 'pytest', 'pytest-cov',
                   'coveralls', 'testfixtures', 'tox',
                   'flake8', 'flake8-docstrings', 'asynctest', 'aioresponses'],
          'docs': [
              'sphinx >= 1.4',
              'sphinx_rtd_theme']}
      )
