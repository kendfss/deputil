from setuptools import setup, find_packages

with open('readme.md', 'r') as fob:
    long_description = fob.read()

setup(
    name='deputil',
    version='0.0.1',
    author='Kenneth Sabalo',
    author_email='kennethsantanasablo@gmail.com',
    url='https://github.com/kendfss/deputil',
    description="cli, and library, for listing a package(or file)'s dependencies",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='utilities operating path file system',
    license='GNU GPLv3',
    requires=[],
    entry_points={
        'console_scripts': [
            'deputil = deputil.cli:main'
        ]
    },
    python_requires='>3.9',
)