from setuptools import setup
from oidc_client import __license__, __version__, __author__, __description__


setup(name='oidc_client',
      version=__version__,
      url='https://oidc-client.rtfd.io/',
      project_urls={
          'Source': 'https://github.com/CSCfi/oidc-client',
      },
      license=__license__,
      author=__author__,
      author_email='',
      description=__description__,
      long_description="",
      packages=['oidc_client', 'oidc_client/config', 'oidc_client/endpoints', 'oidc_client/utils'],
      package_data={'': ['*.ini']},
      entry_points={
          'console_scripts': [
              'start_oidc_client=oidc_client.app:main'
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
          'Intended Audience :: Information Technology',
          'Topic :: Internet :: WWW/HTTP :: HTTP Servers',

          # Pick your license as you wish
          'License :: OSI Approved :: Apache Software License',

          'Programming Language :: Python :: 3.6',
      ],
      install_requires=['aiohttp', 'gunicorn', 'uvloop'],
      extras_require={
          'test': ['coverage', 'pytest', 'pytest-cov',
                   'coveralls', 'testfixtures', 'tox',
                   'flake8', 'flake8-docstrings', 'asynctest', 'aioresponses'],
          'docs': [
              'sphinx >= 1.4',
              'sphinx_rtd_theme']}
      )
