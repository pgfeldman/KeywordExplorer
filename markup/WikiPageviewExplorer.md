# WikiPageviewExplorer

Don't have a Twitter or OpenAI account? Not to worry! _WikiPageviewExplorer_ is a Python desktop app that lets you interactively search for (English) entries using keywords. Pages that contain or relate to the keywords are presented in a list that can then be queried for the number of daily pageviews within a date range.

>![WikiPageviewExplorer](../images/WikiPageviewExplorer.png)

And this is an example of the page views:

>![simpsons](../images/wiki_putin_zelensky_plot.png)

Best of all, the Wikipedia is free, and their API is _fast_. You can do a lot of keywords research here too. And show your love for the Wikimedia foundation by [donating](https://donate.wikimedia.org/wiki/Ways_to_Give) so that this app continues to work!

## How to use

Using the tool is pretty straightforward. That being said, it's possible to break it. If you are running it from the command line, then you will get additional information in the console that might help you figure out things. Most often, it is a poorly-formed keyword that gets sent off to the Wikipedia.

The screen is divided into 5 panels:
- Experiment name - see description in [KeywordExplorer](../markup/KeywordExplorer.md)
- [Topic Search](#topic-search-panel)
- [Page Views](#page-views-panel)
- [Page View Params](#page-view-params-panel)
- Console - see description in [KeywordExplorer](../markup/KeywordExplorer.md)

## Topic Search <span id="topic-search-panel"/>
>![WikiTopicSearch](../images/wiki_topic_panel.png)

The topic search panel takes keywords that are typed (or loaded using **File->Load Experiments**)). When the user clicks the **Search** button, a request is sent that looks for Wikipedia entries that are exact or approximate matches. In this example, we have two somewhat vague keywords: "zelensky" and "putin". The wikipedia returns multiple matches, ranging from [Igor Zelensky](https://en.wikipedia.org/wiki/Igor_Zelensky), the Russian ballet dancer, to [Lyudmila Putina](https://en.wikipedia.org/wiki/Lyudmila_Putina), the former wife of Vladimir Putin.  

Selecting the [Volodymyr Zelenskyy](https://en.wikipedia.org/wiki/Volodymyr_Zelenskyy) and [Vladimir Putin](https://en.wikipedia.org/wiki/Vladimir_Putin) entries and clicking **Copy Selected** will copy the entry to the **Pages** text area in the [Page Views](page-views-panel) panel for exploring page views.

## Page Views <span id="page-views-panel"/>
>![WikiPageViews](../images/wiki_page_views_panel.png)

## Page View Params <span id="page-view-params-panel"/>
>![WikiPageViewParams](../images/wiki_page_view_params_panel.png)