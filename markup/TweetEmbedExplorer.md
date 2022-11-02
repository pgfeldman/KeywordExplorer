# TweetEmbedExplorer

_TweetEmbedExplorer_ is a standalone Python application for analyzing, filtering, and augmenting tweet information. Augmented information can them be used to create a train/test corpus for finetuning language models such as the GPT-2.

![Embed-Explorer](../images/tweet_embed_explorer.png)

## Before Starting
The app **requires** that you have a Twitter developer account and an OpenAI GPT-3 account:

See Twitter for how to get an account and bearer token: https://developer.twitter.com/en

See OpenAI for how to get an account: https://openai.com/api/

See the [**Before Using** in the README](../README.md) for how to set up the app to access the Twitter bearer token and use you OpenAI identifier.  

_TweetEmbedExplorer_ requres additional a MySQL-compatable database. My favorite is MariaDB, wich comes with the [XAMPP stack](https://www.apachefriends.org/). The code uses the LOCAL_ROOT_MYSQL system variable, which you can set up in Windows by using the [Environment Variables](https://docs.oracle.com/en/database/oracle/machine-learning/oml4r/1.5.1/oread/creating-and-modifying-environment-variables-on-windows.html) control panel as shown below:

![Env-Vars](../images/mysql_env_variable.png)

The schema for the database is in the **data** directory. The database must be named **twitter_v2**. The easiest way that I know to create the database is to open a console window in the directory with the sql file, then access the database (e.g. <span style="font-family:Courier;">mysql -u root -pmy_sql_password123</span>). At the sql prompt, type the following

```
MariaDB [(none)]> create database twitter_v2;
MariaDB [(none)]> use twitter_v2;
MariaDB [twitter_v2]> source twitter_v2.sql;
MariaDB [twitter_v2]> describe twitter_v2;
+-----------------------------------+
| Tables_in_twitter_v2              |
+-----------------------------------+
| keyword_tweet_view                |
| table_experiment                  |
| table_query                       |
| table_tweet                       |
| table_user                        |
| tweet_user_cluster_view           |
+-----------------------------------+
6 rows in set (0.001 sec)
```

At this point the app should be ready to use.

## How to use

Using the tool is pretty straightforward. That being said, it's possible to break it. If you are running it in the console, then you will get additional information on the command line that might help you figure out things. Also, setting up your twitter account properly is tricky, so make sure that you have that and your OpenAi accounts working first.

There are three tabs, _Get/Store_, _Canvas_, and _Corpora_. All of these share a common interface at the top of the App that lets you set the experiment name (for spreadsheet file names), and then load the part of the database you're interested in. Note that the database is populated initially by [TweetDownloader](TweetDownloader.md). As with all the Apps in this suite, there are extensive tooltips to help you with using the tool.

![tweet-embed-common](../images/tweet_embed_common.png)
<br/>Figure 1: _Common Elements_

###Get/Store Tab

This tab handles the generation and storing of text embeddings. The app uses GPT-3 embeddings as the basis. The size of the embedding vector is based on the engine selected (see more [here](https://beta.openai.com/docs/guides/embeddings)). Clicking the **Get Embeddings** will iterate through the selected items in the database and add the GPT embeddings to them. It's surprisingly quick, though be patient. Num rows shows the number of tweets that were updated

The _Update DB_ row handles additional items that can be added to the database. The **Reduced+Clusters** and **Clusters** store data that is generated in the _Canvas_ tab. The **Topic Names** button is currently nonfunctional, but will use the GPT-3 to come up with human-readable cluster names. The **Users** button causes the user associated with each tweet to be downloaded from Twitter. This is important for getting location, since tweets rarely have that information associated with them.
<br/>
![tweet-embed-get-store](../images/tweet_embed_get_store.png)

###Canvas Tab

The _Canvas_ tab is the most complex, with a lot of capability. The first row contains the parameters used for calculating the dimension reduction from the GPT-3 vectors to a 2D display. This is done by clicing the **Reduce** button. It has two passes - the first pass is a [Principal Components Analysis](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html) that reduces the GPT vectors to a smaller value that can be processed into 2 dimensions using [T-SNE](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html). The parameter that affects behavior the most is [perplexity](https://scikit-learn.org/stable/auto_examples/manifold/plot_t_sne_perplexity.html?highlight=perplexity), which can be adjusted using the **Perplex:** field.

Once the 2D mapping is generated, then the embedding can be displayed using the **Plot** button. This brings up a [matplotlib scatter plot](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html) that allows for a quick evaluation of the current state of the embeddings.

Once the embedding looks satisfactory, it can be clustered using [DBSCAN](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html)  by clicking on the **Cluster** button (more here)

**Explore**, **Limit**, and then **Exclude**

Lastly, the **Retrieve** button can pull all embedding information from the database for new analysis or corpora generation
<br/>
![tweet-embed-canvas](../images/tweet_embed_canvas.png)

###Corpora Tab

![tweet-embed-corpora](../images/tweet_embed_corpora.png)

Once a model test train corpora has been created, you can finetune a GPT model to generate new tweets that are similar to the training set. A trained model has been shown to be able to accurately predict, for example, the vegetarian preferences of Yelp reviewers when all vegetarian data has been excluded from the test/train data (https://arxiv.org/abs/2204.07483). This means that you can train a model on a set of tweets that may not contain the explicit information you are looking for (e.g. how a target group might react to a new product) and the model will still be able to generate tweets that are likely to contain that information.

To train a model, follow these directions: [How to train a model](../markup/model_train.md).

