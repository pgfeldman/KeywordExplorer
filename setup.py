from  distutils.core import  setup
from datetime import datetime

setup(
    name='keyword_explorer',
    version=datetime.now().strftime("%d.%m.%Y"),
    packages=['keyword_explorer'],
    url='https://github.com/pgfeldman/KeywordExplorer',
    license='MIT',
    author='Philip Feldman',
    author_email='phil@philfeldman.com',
    description='A tool for producing and exploring keywords',
    install_requires=[
        'pandas~=1.3.5',
        'matplotlib~=3.2.2',
        'numpy~=1.19.5',
        'sklearn~=0.0',
        'scikit-learn~=0.24.2',
        'requests~=2.27.1',
        'wikipedia~=1.4.0',
        'openai~=0.11.5',
        'networkx~=2.6.2',
        'tkinterweb~=3.12.2'],

    entry_points={
        'console_scripts': [
            'keyword-explorer = KeywordExplorer.__main__:main',
            'tweet-count-explorer = TweetCountExplorer.__main__:main',
            'wiki-page-explorer = WikiPageviewExplorer.__main__:main',
            'google-explorer = GoogleExplorer.__main__:main',
        ]},

    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],)
