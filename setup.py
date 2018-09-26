from distutils.core import Command

from setuptools import find_packages, setup


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
                    'PASSWORD': '123456',
                    'HOST': '127.0.0.1',
                    'PORT': '5432',
                }
            },
            INSTALLED_APPS=['partitioning', 'tests.app']
        )
        django.setup()
        call_command('test', 'tests')


setup(
    name='django-partitioning',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='Add partitioning to django models',
    long_description=open('README.md').read(),
    author='Soin Sergey',
    author_email='soins1992@gmail.com',
    install_requires=['Django >= 1.11'],
    tests_require=['Django >= 1.11'],
    cmdclass={'test': TestCommand},
)
