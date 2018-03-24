import io
import os.path

from setuptools import find_packages, setup


with io.open(os.path.join(os.path.dirname(__file__), 'README.rst'),
             encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='hypothesis-mongoengine',
    version='1.1.0',
    description='Hypothesis strategy for MongoEngine models',
    long_description=long_description,
    url='https://github.com/gmacon/hypothesis-mongoengine',
    author='George Macon',
    author_email='george.macon@gmail.com',
    license='MIT',
    packages=find_packages(exclude=('*.tests',)),
    install_requires=[
        'hypothesis',
        'mongoengine',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Testing',
    ],
)
