from setuptools import setup

version = '0.22.3.dev0'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('TODO.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'Django',
    'django-extensions',
    'djangorestframework <= 1.0',
    'django-nose',
    'lizard-ui >= 3.0',
    'lizard-map <= 4.14',
    'lizard-geo',
    'lizard-security',
    'lizard-task',
    'timeseries >= 0.13',
    'pkginfo',
    'django-compositepk',
    ],

tests_require = [
    ]

setup(name='lizard-fewsnorm',
      version=version,
      description="Lizard interface to fewsnorm.",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Framework :: Django',
                   ],
      keywords=[],
      author='Jack Ha',
      author_email='jack.ha@nelen-schuurmans.nl',
      url='',
      license='GPL',
      packages=['lizard_fewsnorm'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require = {'test': tests_require},
      entry_points={
          'console_scripts': [
          ],
          'lizard_map.adapter_class': [
            'adapter_fewsnorm = lizard_fewsnorm.layers:AdapterFewsNorm',
            ],
          },
      )
