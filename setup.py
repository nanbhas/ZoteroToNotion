from setuptools import setup, find_packages


setup(
    name='ZoteroToNotion', # name of the git repo
    description='A package to port Zotero data to Notion',
    author='Nandita Bhaskhar',
    author_email='nanbhas@stanford.edu',
    version='1.0.0',
    packages=find_packages(include=['src', 'globalStore', 'lib']) # folders to be installed as a pkg
)
