Explorer Apps
====================================
There are four applications in this project, _KeywordExplorer_, _TweetsCountExplorer_, _TweetDownloader_, and _WikiPageviewExplorer_. A brief overview of each can be reached using the links below. 

[KeywordExplorer](./markup/KeywordExplorer.md) is a Python desktop app that lets you use the GPT-3 to search for keywords and Twitter to see if those keywords are any good.

[TweetCountsExplorer](./markup/TweetsCountExplorer.md)

[TweetDownloader](./markup/TweetDownloader.md)

[WikiPageviewExplorer](./markup/WikiPageviewExplorer.md)

## Before using!!
_KeywordExplorer_ **requires** that you have an OpenAI account and a Twitter developer account. _TweetCountExplorer_ requires a Twitter developer account, and _WikiPageviewExplorer_ requires a user agent. _TweetDownloader_ requres additional elements such as a database, which will be descussed in its section but not here.

OpenAI: https://openai.com/api/

Twitter: https://developer.twitter.com/en

In each case you'll have to get an ID and set it as an environment variable. The names must be OPENAI_KEY for your GPT-3 account and BEARER_TOKEN_2 for your Twitter account, as shown below for a Windows environment:

![Environment variables](./images/environment_vars.png)

If you don't have permissions to set up environment variables or just don't want to, you can set up a json file and load that instead:

```angular2html
{
  "BEARER_TOKEN_2": "AAAAAAAAAAAAAAAAAAAAAC-----------------------",
  "OPENAI_KEY": "sk-s------------------------------------",
  "USER_AGENT": "xyz@xyz.com",
}
```

In this case, BEARER_TOKEN_2 id for the Twitter V2 account, OPENAI_KEY is for the GPT-3, and USER_AGENT is for accessing the Wikipedia. 

To load the file click on the "File" menu and select "Load IDs". Then navigate to the json file and select it. After the ids are loaded, any application that depends on them will run. If you try using an app that doesn't have an active ID, it will complain.

![LoadID](./images/load_id.png)

You should be good to use the apps!
