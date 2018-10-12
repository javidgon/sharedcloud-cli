import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


class NoseTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import nose
        errcode = nose.main(self.test_args)
        sys.exit(errcode)


setup(name='sharedcloud-cli',
      version='0.0.5',
      description='Command Line Interface (CLI) for Sharedcloud.',
      maintainer='Sharedcloud',
      maintainer_email='admin@sharedcloud.io',
      author='Sharedcloud',
      author_email='admin@sharedcloud.io',
      url='https://github.com/sharedcloud/sharedcloud-cli',
      license='MIT',
      long_description=open('README.md').read(),
      platforms='any',
      keywords=[
          'sharedcloud',
          'cloud',
          'computing',
          'development',
          'gpu',
          'cpu',
          'deep-learning',
          'machine-learning',
          'data-science',
          'neural-networks',
          'artificial-intelligence',
          'ai',
          'reinforcement-learning',
          'devops',
      ],
      packages=find_packages(),
      install_requires=[
          'click==6.7',
          'requests==2.19.1',
          'tabulate==0.8.2',
          'timeago==1.0.8',
      ],
      entry_points={
          "console_scripts": [
              "sharedcloud = sharedcloud_cli.main:cli",
          ],
      },
      classifiers=[
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Artificial Intelligence'
      ],
      tests_require=['nose'],
      cmdclass={'test': NoseTest}
      )
