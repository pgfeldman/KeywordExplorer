## ~~KeywordExplorer~~ (Deprecated due to Twitter/X API access)

KewordExplorer is a Python desktop app that lets you use the GPT-3 to search for keywords and Twitter to see if those keywords are any good. Below is an example of the running app:

![KeywordExporer](../images/app.png)

And this is an example of the Twitter results:

![Tweets for pets](../images/example_plot.png)

## How to use

Using the tool is pretty straightforward. That being said, it's possible to break it. If you are running it in the console, then you will get additional information on the command line that might help you figure out things. Most often, it is a poorly-formed keyword that gets sent off to Twitter. Also, setting up your twitter account properly is tricky, so make sure that you have that working for counts. See

https://developer.twitter.com/en/docs/twitter-api/tweets/counts/introduction

if you run into trouble.

Setting up the OpenAI GPT-3 account is more straightforward, and the API is more robust

The screen is divided into 6 panels:
- [Experiment name](#experiment-name-panel)
- [GPT](#gpt-panel)
- [GPT Params](#gpt-params-panel)
- [Twitter](#twitter-panel)
- [Twitter Params](#twitter-params-panel)
- [Console](#console-panel)

### Experiment Name <span id="experiment-name-panel"/>
>![Experiment name](../images/experiment_name_panel.png)

The experiment name is used by the application to provide a default name for output such as Excel files or entries in databases. Editing the name here will change the default suggestion in the file explorer when saving a file.

### GPT <span id="gpt-panel"/>
>![GPT panel](../images/gpt_panel.png)

This is where you interact with the GPT-3 directly. You might want to use the GPT-3 playground a bit to get the hang of writing prompts (https://beta.openai.com/playground). The app starts up with a default prompt. You can replace that with your prompt directly, or load a saved prompt using the "File->Load Experiment" menu dropdown.

Let's look at the default prompts a little more closely:

    Here's a short list of popular pets
    1)

The extra line with the "1)" prompts the GPT to return a numbered list. Most of the time. Sometimes it will return a paragraph about how great dogs or cats are. The GPT-3 has a value called _temperature_ which adds some randomness to the prompt response. In this app, the value is fixed at 0.4 on a scale from 0.0 to 1.0.

Clicking on 'New Prompt' will send that prompt to the GPT-3. You'll see that it was sent, along with the selected engine and the number of tokens in the *Console* window. If you want to continue prompting, then 'Extend Prompt', which will add the results to the initial prompt. You may have to edit the text a bit, since the GPT can stop in mid-word while generating a response.

Clicking on 'Parse Response' will apply the regex in the 'Parse Regex' field to each line in the resonse text that is longer than _Max Chars_ and place the parsed results in the 'Test Keyords' area in the Twitter section (described [Twitter](#twitter-panel) below). You can edit or try new regexes if you have a different form of output. I highly recommend (https://regex101.com) as a place to test out regexes on text. You can copy the text from the Response field into their playground.

Clicking on 'Extend Prompt' will use the current prompt, plus the text that has already been returned to create a new prompt. The result will be appended to the current response.

### GPT Params <span id="gpt-params-panel"/>
>![GPT params panel](../images/gpt_params_panel.png)

This part of the app lets you determine the number of [tokens](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them) to let the GPT-3 use when its generating a response. Tokens cost money, so the choices are limited to values that get results but don't go overboard.

The second part of this section lets you choose the GPT-3 [model](https://beta.openai.com/docs/models/gpt-3) (or engine as it's refered to in their API). There are several choices, ranging from "davinci" (the most powerful and expensive) to "ada", (the cheapest and fastest, but not as powerful) the default is davinci, but play around and see what works for you.


### Twitter <span id="twitter-panel"/>
>![Twitter panel](../images/twitter_panel.png)

This panel lets you explore counts of keywords and hashtags for the period of time that you're interested in. You set your start and end dates in the date fields. You can adjust the sampling rate in the [Twitter Params](#twitter-params-panel) panel. 

The algorithm for getting keyword counts has two elements - the keyword, and the span of days. Twitter breaks the response into several pieces. Each piece counts as a resuest of the Twitter V2 API, and it only allows so many requests, so don't try to pull in a full year of daily Tweets for a large set of keywords. 

Keywords can be edited in the **Test Keyword(s)** window. Using 'OR' allows you to combine keywords. For example, "Hampsters OR Rabbits". They can also be loaded using the **File->Load Experiment** menu. If you make changes to the keywords and you want to save the results, use the **File->Save Experiment** menu. Examples are in the data directory.

Pressing the **Test Keyword** button will send a series of qaueries to Twitter that gets the number of tweets per day over a given time range. It will also open a window with a plot showing the values for each keyword over time. If you close the plot, you can reopen it by clicking **Plot**. Clicking **Save** will open a dialog that lets you save the data in the chart as an excel file.

Running the same query over a range of dates will accumulate the results in the same plot (Known bug - the app treats each new sample as a different label). This allows quickly compare keaywords over a range of dates without blowing through your API limits. To start a new plot, press **Clear** before running.

Lastly, clicking **Launch Twitter** will open a set of tabs in your default browser - one for each keyword within the range of dates specified. This allows you to quickly explore keywords in context. For example, you could see if the "Birds" keywords referred to [the group of warm-blooded vertebrates constituting the class Aves](https://en.wikipedia.org/wiki/Bird), , or the [Baltimore Orioles](https://en.wikipedia.org/wiki/Baltimore_Orioles) if you were looking at dates that included games during their 2014 season.

### Twitter Params <span id="twitter-params-panel"/>
>![Twitter params panel](../images/twitter_params_panel.png)

If your request spans too much time, you can subsample across weeks or months. Unlike the "day" option, these are not complete counts. Instead they subsample a week or month (Hey [@TwitterDev](https://twitter.com/TwitterDev)! Could you add these as options?). As such they are not accurate counts, but are still good for determining realative trends between keywords.

### Console <span id="console-panel"/>
>![Console panel](../images/console_panel.png)

The console window is where much of the logging output of the app goes. In addition, if you launch the app from the command line, more information will be available there.

The newest output is inserted at the top of the list. The console is only for output. Typing text here has no effect
