---
layout:     post
title:      A Withering Trader’s Illustrated Primer 
date:       2023-07-14 11:21:29
summary:    the Last Samurai, Darth Vader, the world of entertainment bleeding into the world of things 
---


“There are only two industries. This has always been true....There is the industry of things, and the industry of entertainment....After people have the things they need to live, everything else is entertainment. Everything.” 
― Neal Stephenson, The Diamond Age: Or, a Young Lady's Illustrated Primer

Now that I’ve spent some more time in the weeds with LLMs as applied to capital markets, I have some reflections about what the building blocks are, how things are likely to play out as well as how I’m going to position myself. 

Let’s start with the key number, before I get into things. 42%. That’s how much more Nvidia and Tesla stock have traded than the entire S&P 500 ETF (SPY) on median, over the past 2 months. Gambling on AI has surpassed society’s interest in passive investment. This number (which also happens to be the meaning of the Universe) will frame our discussion today - but only in the background until it becomes relevant at the end 

## The Table Stakes Model 

First - it’s important to recognize that the “bet” of applying AI to capital markets is not contrarian. I.e. Citadel, Bridgewater, and many large firms have already started cranking applying both Open Source and Closed Source models to generate alpha. They will also be marketing this to investors by year end as a differentiator.

Most likely, hedge fund AI application is occurring in the area of “alpha capture” - i.e parsing large amounts of sell-side research as well as internal trade write ups to create models that deploy capital as “aggregates” of people within firms. Previously, such models relied mostly on momentum. I.e. you were trend trading people and how smart they’d been historically, with perhaps some meta information. Such as if they had numerical estimates that were consistently better than consensus. 

Now, with AI - more complex models can be built. LLMs allow you to extract numerical information from plain text so factors such as “logical consistency” or “ability to adapt to new information” can be quantified with a particular analyst’s write ups. Put simply - let’s say last year you had 2-3 factors per analyst write up. How contrarian it was. How good his/her hit rate was. How he’d been doing lately. Now you have maybe 100 relevant factors. So selecting analysis is going to be much better than it was previously. 

The first order implication of this is that quant teams focused on alpha capture will get more capital, as these models port easily to LLMs. The second order, more frightening implication is that hedge funds - especially mega cap hedge funds which force analysts to share large amounts of investment analysis or write ups as part of their process (i.e. Bridgewater, Bluecrest, Balyasny) - will increasingly have a model about “canonically good investment analysis”. 

Once you have a good model of what comprises good analysis, with its features, this can be looped back into large amounts of investment text to create completely AI based analysts. Bridgewater has stated that LLMs are performing at par with their top analysts already in various regards.

Broad deployment of “synthetic analysts” will take at least 12 months -- because the initial systems, even if rushed, are just coming online now. And the average hold period of larger funds is such that it takes some time before any meaningful model can be built on trading information (as opposed to HFTs where this information hits within hours). 

This creates a sort of 5 part formula for a hedge fund’s success in applying LLMs to investing:
1. Low hold time/ higher frequency but still qualitative strategies (need text to work) 
2. Analysts write up analysis in detail, transparently shared or at least tracked (especially when they change opinions)
3. Large number of analysts
4. An alpha capture team 
5. Internal AI researchers that can loop back all of the findings into a privately trained model that can then be deployed 

Intuitively this favors very large hedge funds. Simplistically if you have more text on more trades, with larger quant teams you’re going to win. This creates an enormous bar for an incumbent (yours truly) for succeeding in this space. I will address this bar later but next I want to discuss data

## The Data Issue - Speed, Scale and Depth

### Speed 

Second - the vast majority of the data that can usefully train LLM models is not publicly available. Bing, and Google Bard cannot even access management transcripts because they’re copyrighted by the Motley Fool and Seeking Alpha. Furthermore, to limit liability - models like GPT4 have increasingly added constraints on financial queries that instruct users to consult professionals. Earnings and management transcripts are of particular interest because of their transcription speed - i.e. there are audio events that analysts dial into before they’re widely syndicated. This gives buy side analysts time to position themselves ahead of likely upgrades/downgrades 

Market data is itself, one large segment of AI’s utility to capital markets. It’s not very glamorous, but if you can get real time transcriptions and analysis of 700 stocks that are all coming out with earnings at once - you have a fundamentally faster/ better framework than would be available to a human. 

This introduces a new mental model. Let’s say before you had quant teams that were very good at deploying fast models. And you had qualitative teams that were very good at doing detailed/ correct analysis but were very slow. The AI application in the early days are going to be like a really fast qualitative analyst. We always suspected the guys in the Patagonia Vests were part NPC, and with LLMs this transformation will become complete

Think of a dude who is dialed into 100 different management calls at the same time, trading them all live. That’s this earnings season. 

### Scale 

Once you get over the speed issue for “relevant market info” such as management transcripts, and central bank transcripts. Then you enter a wider horizon. All government legislation. All TV news. All social media. Anything that creates vast amounts of text that is possibly market relevant is going to get sucked into LLMs, processed and turned into quantitative weights 

Taking a step back, and zooming out - I think the “big point” I am getting at is that anything that previously was a 1000 page PDF some investment analyst might pore over and write a Twitter Thread about (i.e. the Build Back Better Bill), now an LLM is going to do this. 

### Depth

Most news sentiment bots or existing bots written by hedge funds ingest information and come up with very rote “buy” or “sell” signals. But LLMs are capable of much more nuanced analysis. Depth will come in two parts that I can see

First - you have depth as applied to interpreting news as part of a larger mental model. For example you might evaluate all news as propaganda, or not - and also measure the efficacy of that propaganda in real time. Or you might map world views on to news items or Twitter accounts and meta-classifiers to say, for example, that news is being routinely broken by anarcho capitalist adjacent accounts. LLMs basically give us the ability to manufacture huge amounts of meta-information about any piece of text on the internet, turn that information into a classifier, then add a timeseries to that classifier. I use the term depth here to point out that the timeseries being evaluated will be more 3 dimensional or nuanced, as opposed to simply “bullish” or “bearish”. 

Second - Depth can apply to real time market analysis. Much like Sell Side analysts write reports, which I suppose are “formal” market moving information - a vast number of substack authors, hedge fund managers, as well as online personalities such as myself opine on markets to decently large numbers of people. Let’s say the old model was “consensus” or “non consensus” as the binary tag. Now there are far more tags such as “analytically deep”, “reliant on momentum as proof of claim”, “logically flawed but highly engaging”, “humorous”, “acerbic” which might be applied to a piece of analysis  

I’ll coin a term here. Augmented LLM Alt Data. ALAD. ALAD will basically create new dynamic timeseries by parsing vast amounts of unstructured internet text into timeseries that represent specific concepts. Like retail investor appeal. Brand strength. Contrarianism. Appeal to Right Wing Investors. Etc. ALAD will apply equally to directly market related topics, as well as more broad categories. 

But at its core, ALAD will involve scraping the entire textual output of the internet in real time (and its entire history) to generate market alpha. ALAD is why the Wayback Machine is pissed right now due to overages on its data servers. Increasingly there will be an arms race to get cached copies of the internet. This problem will get only worse with time as LLMs themselves start generating data. 

Data scientists are probably squirming right now as they should be. The amount of scraping throttles / and script breakages on Twitter and countless other sites are about to go parabolic. 

## The Analysis Issue

But let’s say you get the data loaded. You have all the timeseries of real time factors that you want. Market related. Non market related. You’ve got current output (your firehose) as well as your historical models built. Still - you need an analytical engine. Essentially a model to interpret these things, and put them into the correct context to make trading decisions. 

There are basically 2 hurdles you need to overcome to make LLMs apply to capital markets

First - generic LLMs aren’t natively trained as portfolio managers. Second - generic LLMs don’t have enough industry data to be useful

Regarding the first point, there are only a few portfolio managers who have been verbose enough about their process to train analysts on. Most great PMs don’t talk very much to others about how they make money. And the ones who do talk a lot might be lying - either for compliance reasons, or because it's a positive expected value to confuse your opponents. 

I once heard from someone credible that you only do a Markets Wizards interview if you’ve done something sketchy to make money and need to wrap a story around your wealth. It made sense to me intuitively. Hedge fund managers, are for the most part, not very altruistic characters. Do you really want to trust their writing to train your LLM?

You probably can trust the PM to some extent in a closed environment like Bridgewater, where there are severe guardrails around sharing the information as well as incentives to upload credible information (they have an entire system called DOTs that tracks peoples’ credibility in real time). But nobody outside the walled garden has that info. 

So the first problem - i.e. training an LLM to be a PM is very very hard, because you can’t trust market writing. I call this the ‘unreliable narrator’ problem. Anyone smart talking about markets (including yours truly) is probably not telling the full truth - or has some vested interest in sharing information which isn’t aligned with your objective function. 

Going back to my days as a hedge fund analyst - the unreliable narrator problem is even more intractable because we’d only be writing a lot about our trades when we were losing money. I.e. compliance / risk management was asking why we were doing things. This kind of leave a would-be LLM portfolio manager creator with a best case scenario that a manager talking about his process is lying, and a worst case scenario that the manager is a clown / out of sync with markets. 

The second point - industry analysis - is easier to get around. You basically load up every book and analyst report imaginable relevant to a sector and train Vicuna 65b with it. Congrats you now have the world’s best expert in any particular topic with vast historical context and training data. However, your edge doing this won’t be very large relative to large hedge funds who will all do the same thing and it’s probably a short matter of time before Bloomberg or other market data firms (such as IHS Markit / MSCI etc) create and license said models as a commodity service.   

That doesn’t mean you still don’t need to do it or buy these services. It just means that doing so is table stakes, and will only stop you from not getting destroyed. You have a steering wheel but that doesn’t mean you’re going to win the race. 

This of course begs the question, how do you train a Synthetic Portfolio Manager? That is to say, how do you make an LLM trade profitably and actually pull the trigger?

I believe I have my answer, and a rough formulation or a hypothesis - but before I get into it - one last point

## The Reflexivity Issue

One thing which hedge funds continually cannot adapt to is the reflexive, internet and metaverse native world that we live in. Meme stocks. Doge. Pepe. The fact Elon Musk is the richest man in the world. That we elected a meme as President. And look like we’re considering doing it again. 

The reflexive world has a data scale which hedge funds simply do not want to engage with, because it exists at a click level. As one $40+B’s fund head of data put it to me “Look. I know there’s alpha in your world. But it’s not something we, as a firm, will engage with. Even if it makes money. It’s simply not something our investors would be happy about. Would be proud of, what we’d want to tell our kids about -  or - is - from a risk management perspective - the type of thing we’d want to underwrite. And - just to reiterate this, I know memes are real. I’m not dumb. I know Tesla is huge, options, what not. It’s just - at a personal level - something I am not going to put a lot of thought into and I don’t think anyone serious is going to either.” 

This meeting obviously went very well. Kek. But it echoes a lot of how hedge funds think about mimetic finance. Or crypto largely. 

Market fundamentalists are willing to acknowledge things like HFT being “valid” ways to make money, because it requires taking no view on the underlying fundamentals. But at scale - the buy side industry largely refuses to acknowledge that the average person clicks on 8 articles before they trade. And that finance and ecommerce increasingly are indistinct.  

Retail trading is at all time highs again, and - interestingly, has looped into AI. Per the NVDA/TSLA being 42% of the S&P 500 ETF statistic I cited at the beginning of this article. Incremental retail interest in AI is at catastrophic highs - outpacing interest even in index investing with the market up mid teens year to date. 

So - going back to the idea of simultaneously being contrarian and long a large market  - which I (and many other people agree) is a necessary prerequisite to making a 10 year bet with asymmetric upside. 

I’d say that AI is very interesting in the context of retail trading. Retail generates vast amounts of data. One day of crypto twitter and on-chain crypto data is approximately the size of a year of Industrial sector sell side research. Granted, it’s of much lower *textual* quality. But it has vastly more meta data and intraday overlap. This tightens the feedback loop between analytical judgments and outcomes. 

This sounds very grandiose - but basically if you’re pulling in a ton of qualitative and quantitative data at once, you end up with an unreadable firehose with short term trading recommendations that result. Machines and AI will almost certainly outperform humans in the resulting strategy set due to limits of attention span, and info processing capability. A single trader - like me - would be able to replicate the entire output of a boiler room filled with penny stock traders, as a simplistic visual. 

Finally - I’d say the bar remains extremely low in the information available to retail traders and the ability to generate engagement there remains high. Especially in crypto, options and meme stocks where the analytical quality is terrible relative to the amount of volume traded. 

## One Last Dance. Ritual Seppuku 

When I first began my journey interacting with LLMs and applying them to capital markets my knee jerk reaction, and resulting existential crisis boiled down to something like this: 

“I will not be able to become an old man trading markets because AI is going to destroy my industry”

I still believe this to be true.

I asked “If human judgment is to die in capital markets, who will plunge the knife?”

But as I’ve been training both synthetic portfolio managers (SPMs) and synthetic analysts - there’s one very obvious truth. A blackpill, if you will. The guy who wrote Market Wizards isn’t rich. He’s just providing fund managers with their compliance outs. The guys writing Twitter threads about Warren Buffett are not rich. They’re selling newsletters to afford their single share of Berkshire. 

Soros was lying about his trading process in his books. His son even said as much. Reflexivity was just an elaborate code word for insider trading with Central Bankers. 

And even if there are shreds of truth, I know for a fact - when I study the last 3 years of my own trading, that there’s ever so much you don’t talk about. What you talk about after the fact is drastically different from how the sausage is made in real time. And no fund manager would ever provide consistent forward looking market commentary because this would put him/her at a consistent disadvantage from a front running perspective. Even within a fund, like a pod shop - when you have PNL momentum the amount of analysis you have to send in prior to doing your trades is minimal. And over time - due to the rise of LLMs, Portfolio Managers will likely be even more tight lipped than usual due to concerns of career preservation 

Let’s be more direct: an attempt to train a real AI driven Portfolio Manager from historical market analysis / disjointed Soros babblings will not work. 

So I’ve come to 4 axiomatic observations relevant to “solving this” problem
You can only train a Synthetic Portfolio Manager with a real trading journal. This is an intractable cold-start problem 
The trading journal needs to incorporate real time interaction with retail investors in order to be sufficiently differentiated from other funds in the arms race and data rich 
AI has enormous amounts of hype and can generate excellent market analysis provided a human curates it 
AI itself is good at generating content

That lead me to my inescapable conclusion

## The Plan & The Conclusion

I think back to the movie the Last Samurai.

Basically Tom Cruise stubbornly insists on dying by the sword - as his opponents gun him down with new technology (machine guns). 

This was the analogy I originally thought was the case with AI and capital markets. That you could switch over to machine guns and that was that.

But it’s the wrong analogy. Instead imagine Tom Cruise was fighting with his sword not to “die with honor” but instead to train robotic samurais that were immune to bullets. And like Darth Vader he gradually replaced one piece of himself with code / AI to improve his battle performance until his entire body was artificial. 

Really, that’s what the correct play is. 

So let’s review. 

The Sword:

* ALAD I (Alternative LLM Alternative Data) Real time and historical parsing of all important market data including earnings releases, transcripts, central bank data releases
* ALAD II - Real time parsing of all company relevant text blocks including influencer content, corporate tweets, news events, podcasts, product reviews 
Trained LLM Analysts for each important sector to analyze parsed information in context of history. 
LLM Content Creator Bots that apply LLM Analyst workflows to the market mosaic combined with 
Backtests / real time implementation on all of the above 
The Battle:
* Live trading (my own + external capital) 
* A web property broadcasting 1-4 with intensive data tracking
* My Twitter account 

The Question “If human judgment is to die in capital markets who will plunge the sword?”

The Answer: I will, first into my opponents, and finally - once the training is done, into myself.

How long will it take? 

6 months? A year? At least. It will require my entire focus, and I’m beginning to brace myself for it.

I had fantasies - in some ways, that I’d be able to stop The Grind. That AI would nearly immediately do my job for me. But now I see the truth. That I not only have to perform the dance. I need to record it, and all its metadata meticulously. So meticulously that I have ironclad IP and training data sets. My only advantage is my willingness to do this publicly. 

I will go until I’ve made a robotic version of myself that can beat me at my own game. Some of my limbs are already replaced, and my use of my new LLM appendages should make a fine spectacle. 

I breathe in deeply. One more go. To reference the book, “The Diamond Age” - I must make my Illustrated Primer. An Illustrated Primer is a mechanical training guide for trading profitably. 

The grand joke, perhaps funny to only me, is that it’s entertainment - capitalized by trading - that will allow AI to enter the world of things. 
