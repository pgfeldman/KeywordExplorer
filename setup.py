# I spent a good deal of time trying to figure out how to deploy to PyPI using the JetBrains IDE. You can read
# the details at https://viztales.com/2022/04/05/phil-4-5-2022/
from  distutils.core import  setup

long_s = '''Explorer Apps
====================================
There are six applications in this project: KeywordExplorer, TweetsCountExplorer, TweetDownloader, WikiPageviewExplorer, TweetEmbedExplorer, and ModelExplorer. They, and the classes that support them, can be installed with pip:

    pip install keyword-explorer

**KeywordExplorer** is a Python desktop app that lets you use the GPT-3 to search for keywords and Twitter to see if those keywords are any good.

**TweetCountsExplorer** is a Python desktop app that lets you explore the quantity of tweets containing keywords over days, weeks or months.

**TweetDownloader** is a Python desktop app that lets you select and download tweets containing keywords into a database. The number of Tweets can be adjusted so that they are the same for each day or proportional. Users can apply daily and overall limits for each keyword corpora.

**WikiPageviewExplorer**  is a Python desktop app that lets you explore keywords that appear as articles in the Wikipedia, and chart their relative page views.

**TweetEmbedExplorer** is a Python desktop app for analyzing, filtering, and augmenting tweet information. Augmented information can them be used to create a train/test corpus for finetuning language models such as the GPT-2.

**ModelExplorer** is a Python desktop app that lets a user interact with a finetuned GPT-2 model trained using EmbeddingExplorer

Full documentation is available at https://github.com/pgfeldman/KeywordExplorer#readme'''

setup(
    name='keyword_explorer',
    version= "0.6.alpha",
    packages=['keyword_explorer',
              'keyword_explorer.utils',
              'keyword_explorer.TwitterV2',
              'keyword_explorer.mastodon',
              'keyword_explorer.tkUtils',
              'keyword_explorer.tkUtilsExt',
              'keyword_explorer.OpenAI',
              'keyword_explorer.Panda3D',
              'keyword_explorer.huggingface',
              'keyword_explorer.Apps'],
    url='https://github.com/pgfeldman/KeywordExplorer',
    license='MIT',
    author='Philip Feldman',
    author_email='phil@philfeldman.com',
    description='A set of tools for computational sociology using LLMs',
    long_description=long_s,
    install_requires=[
        'pandas',
        'matplotlib',
        'numpy',
        'scikit-learn',
        'requests',
        'transformers',
        'wikipedia',
        'openai[embeddings]',
        'openai',
        'networkx',
        'tkinterweb',
        'PyMySQL',
        'python-dateutil',
        'panda3d',
        'XlsxWriter',
        'pyperclip'],

    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

