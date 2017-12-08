from setuptools import find_packages, setup


setup(
    name='hypothesis-mongoengine',
    version='0.1.0',
    description='Hypothesis strategy for MongoEngine models',
    packages=find_packages(exclude='*.tests'),
    install_requires=[
        'hypothesis',
        'mongoengine',
    ],
)
