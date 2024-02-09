#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, Command, find_namespace_packages


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import django
        from django.conf import settings
        from django.core.management import call_command
        settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': 'partitioning',
                    'USER': 'postgres',
                    'PASSWORD': 'postgres',
                    'HOST': 'localhost',
                    'PORT': '5432',
                }
            },
            INSTALLED_APPS=['partitioning', 'tests.app']
        )
        django.setup()
        call_command('test', 'tests')


with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='django-partitioning',
    version='0.1.1',
    url='https://github.com/starnavi-team/django-postgres-partitioning',
    packages=find_namespace_packages(),
    include_package_data=True,
    license='BSD License',
    description='Add PostgreSQL table partitioning to Django models',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='starnavi.io',
    author_email='hello@starnavi.io',
    install_requires=[
        'Django>=1.11,<5.1', 'setuptools'
    ],
    tests_require=[
        'Django>=1.11,<5.1', 'setuptools'
    ],
    cmdclass={'test': TestCommand},
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ]
)
