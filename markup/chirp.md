## Inspiration
Doing research in social media like Twitter is tricky. Finding the right keywords or hashtags is often just making guesses about what might make sense and working out from there. Large language models such as [OpenAI's GPT-3](https://openai.com/blog/openai-api/) have changed all that. Trained on **huge** amounts of text, these models can be _prompted_ to produce keywords about the topics that we might want to examine. For example, in response to the prompt:

```
Here's a short list of Simpsons characters:
1)
```

The GPT-3 can produce a list like:

```commandline
1) Homer Simpson
2) Marge Simpson
3) Bart Simpson
4) Lisa Simpson
5) Maggie Simpson
6) Apu Nahasapeemapetilon
7) Moe Szyslak
8) Chief Wiggum
9) Krusty the Clown
10) Sideshow Mel
11) Mr. Burns
12) Smithers
13) Itchy and Scratchy
```

That is _deep cut_ fan level of knowledge! Even Apu's name is spelled correctly! And if it works for this, then it can work for other topics as well. _I_ may not know that much about The Simpsons or any of the other countless things that might be worth researching, but the GPT does. All we have to do is harness that.

## What it does
>![TheApp](https://philfeldman.com/pix/app.png)

_KeywordExplorer_ is a standalone app that lets you use the GPT-3 to interactively search for keywords and Twitter to see if those keywords are any good. Below is the result of the "Simpson's" search, with only the topics that have a presence on Twitter over the last two weeks

>![TheApp](https://philfeldman.com/pix/simpsons.png)

The Simpsons provides a good idea of the power of the tool. For anything that was written about before the model was trained (sorry COVID), there are all kinds of topics that make for great research. I leave the specifics to your imagination.

## How we built it
In many respects, this is a straightforward Python desktop app. Using tkinter meant that there was no having to deal with full stack complexity. Things just work, even if they look like they are from the 1990's. 

The code is a series of reusable classes, about half of which are devoted to the UI, and the others to interacting with Twitter and the GPT-3. The package is available on PyPi as [_keyword-explorer_](https://pypi.org/project/keyword-explorer/) for anyone who wants to use it or its parts.

Probably the easiest way to use the app is this:
```commandline
import keyword_explorer.Apps.KeywordExplorer as app

app.main()
```
That will launch the app. Just remember that you need a Twitter developer account with an _application token_ and an OpenAI account with a GPT-3 key. Check out the full documentation at https://github.com/pgfeldman/KeywordExplorer for all the details.

## Challenges we ran into
Even without a full stack, coordinating interactions with two remote APIs is tricky. In particular the Twitter V2 has some... quirks. I'd love for the counts to be fleshed out to include weeks and months in addition to days. Randomly sampling tweets takes a **lot** of code.

## Accomplishments that we're proud of
I think we are just at the beginning of using large transformer models like the GPT-3 as ways of producing insight about human nature. What I really love is that we are able to take information from the GPT-3 and immediately test it in the real world using the TwitterV2 counts API. So cool.

## What we learned
Using a language model like the GPT-3 is a whole new way of interacting with knowledge. The ability to explore the latent areas around the texts that these models were training on is exhilarating. We are really only at the very beginning of the kinds of insights that these models can provide.

## What's next for KeywordExplorer
_KeywordExplorer_ is part of an expandig suite of tools based on social media and large language models. I am currently working on an app that will download keyword-related tweets, train a GPT-2 model on them, producing an interactive app where we can ask questions of the model about data that is not in the training text.
