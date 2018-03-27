from setuptools import setup, find_packages

DESCRIPTION = """
    Library for generating building OCDS API
"""


install_requires = [
    'setuptools',
    'CouchDB',
    'requests',
    'Flask',
    'ocdsmerge==0.2'
]

test_requires = [
    'pytest',
    "pytest-flask"
]

entry_points = {
    'console_scripts': [
        'runserver = openprocurement.ocds.api.app:run'
    ]
}

setup(name='openprocurement.ocds.api',
      version='0.1.0',
      description=DESCRIPTION,
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      license='Apache License 2.0',
      include_package_data=True,
      namespace_packages=['openprocurement', 'openprocurement.ocds'],
      packages=find_packages(exclude=['ez_setup']),
      zip_safe=False,
      install_requires=install_requires,
      tests_require=test_requires,
      entry_points=entry_points
      )
