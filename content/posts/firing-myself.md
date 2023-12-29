---
author: ["goodalexander"]
title: "Firing Myself"
date: 2023-07-02T11:21:29Z
draft: false
tags: ["long-form","philosophy"]
---
deprecating Alex 1.0, applied accelerationism, ego death with a postgres backend 

## Encountering the Power of AI in Financial Decisions 

Algorithms from social media platforms like TikTok and Instagram, along with the whole digital marketing industry, work non-stop to hook us on products and services that aren't good for us.

AI differentiates itself from Tech 1.0 by giving users the power of algorithms to improve their lives, rather than be victimized by them. 

Below is an essay about how I’m thinking about using AI to vastly improve my personal decision making, and progress towards my goals.

After reading articles suggesting AI could replace human judgment in many industries, like my field (finance), I tested GPT-4 extensively on my own trading. I fed it my trading journals, backtests, as well as expert context from Market Wizards like George Soros. I discovered that, with the right context, information, and "prompts", AI could consistently outperform my past decisions. 

Let me be more blunt: it is clear to me that it is a waste of time for me to spend any time analyzing markets, looking at charts or constructing trades because AI systems can do it better. Naturally, this changed how I spend my time at work dramatically.

I feel fine focusing on building systems instead of trading - because 1] the systems are good enough to justify this now and 2] these systems won’t stop improving.  Yet as I audited the judgment of systems, especially how AIs would have traded the Covid19 crisis, an uneasy feeling crept over me. The output felt very human - articulating opinionated views about how things would go in markets and empathy for people affected by the virus. Besides generating good results - the trading journal that GPT4  generated felt jarringly personal.  

## Possible for Personal Decisions?

The “Follow the White Rabbit” moment came, and down the rabbit hole I went. AI based decision making need not just apply to trading. It could transform every aspect of my life.

But - if you let a system make your decisions, would you be sacrificing your basic freedom or existential identity? I found my answer to be, "No." I thought of it like how we opt into social contracts in society - giving up some freedom in exchange for better governance. Sure, you might have "freedom" in anarchy, such as in regions plagued by political instability and guerilla warfare. But in places like the US, you choose to obey certain rules and let judges decide on specific situations. You give up some options to exist in a better run system. As long as you agree with the system's premise - rules like "don't speed in a school zone," - getting pulled over by a cop for breaking that rule doesn't mean you've lost significant freedom. It just means you bought into the premises of a system before you decided to break the rules. 

Time and again, I have been unable to reach my own goals, continually letting myself down. It feels like I'm living in anarchy. I set huge goals but rarely meet them. I think many people can relate to this. We make up stories to justify why it's okay to fall short of our dreams, reframing the situation to make it easier to deal with. 

But what if there's another way? What if we could use AI and smart systems to give us a real chance of reaching our goals, and force us to stay on track? What if we could move from the chaos of our wandering minds to a well-ordered 'Democracy of the Self'? If we have a synthetic Tony Robbins, a personal trainer, and McKinsey at our fingertips, why wouldn’t we use them? 

## The Concept of Firing Myself

I came across Bryan Johnson, a wealthy payments entrepreneur turned health influencer. He developed a bio-feedback based algorithm that, in his words, "took better care of my health than I could." He named his system Blueprint. I liked that he applied this Blueprint to his own life, in his words, “firing himself” with regards to health decisions. Most health influencers talk the talk but do not walk the walk. Bryan does. 

So, I decided to follow suit, but with a more radical approach. I aimed to construct a "blueprint" not just for health decisions, but for every decision I make.

At the end of the day, it boiled down to one question. 

Why would I limit myself to improving my trading when I could revolutionize my entire existence?

## Getting to The Decision: Opting into Architecture 

I'll guide you through my journey of this undertaking - of replacing my ego with AI based decision making tools - ending with a short overview of the system I'm putting into place.

I identified 8 systems that I’d need to build for me to have enough confidence to Fire Myself. Afterall, the question is naturally - if you're firing yourself, what system are you replacing yourself with? In Bryan Johnson's case - it was biometric measurement and a team of experts constantly reviewing his data. Giving up judgment is a big deal, and I wanted enough scope for any system I opted into to handle edge cases, make decisions, deal with day to day workflows, and adapt.

Before I get into it, I should note that this is more a live, production software project than a philosophical musing. For each of these concepts I’ve built and refined prompts inside of GPT4, and use the OpenAI API extensively. In addition to GPT4, I make use of other tools including Python, PostgreSQL, Discord, and Google Sheets. I’ve deployed my system on a cloud Linux server I rent from Hetzner, a low cost provider. In a later post - likely after I’ve been in uninterrupted production for a few months - I will walk through an open source implementation of this.  

However - I wanted to write my higher order thoughts down so that other people might ask themselves how their own system might look, and also to gather thoughts from other smart people who follow me online. 

## System Architecture - 8 Features to Fire Myself

With this foundation in place, let's delve into the eight core systems that are crucial to the process of 'firing yourself' and allowing AI to take over your decision-making process.

### 1 Default Settings

A Default Setting has three parts:
1. Objective Function. The north star - what you’re moving towards, specifically.
2. Constraints. what you’re willing to sacrifice, and what you’re not in order to reach your objective function 
3. Values. Underlying judgments that you’ve made to land on your objective function and your constraints 

Just as an example: your Objective Function might be building a healthy food business and bringing wellness to as many people as possible through holistic food. You might be unwilling to sacrifice your time with your family to do this, but you are willing to risk most of your savings (Constraints). The values underpinning this Objective Function and Constraints might be your day to day experience, living up to your family’s dreams and your own visceral feeling of how much better things are now you’re healthy. 

### 2 Scoring

The scoring system has two core parts:
1. A set of three to four metrics that allow you to clearly quantify your progress towards your objective function
2. An AI driven system that can ask you questions about how well you’re hitting the underlying drivers of your metrics and assign you a daily score

Per the example above you might track 1] your weekly sales 2] your repeat rate 3] progress on your new product pipeline and 4] your brand’s digital engagement. And you might have a system that asks you questions about actions you've taken to drive sales, greater customer loyalty, product innovation and marketing efficiency. Note this is very business oriented - but your own scoring system might have much more personal objectives. 

### 3 Decision Making

After you’ve defined your values and how to quantify them - the primary next action is to *stop making your own decisions*. It would be impossible to say you’ve “fired yourself” if you keep putting your ego in charge. 

My initial decision-making system has five parts:
1. The creation of a synthetic board of directors that is highly aligned with, and has extreme expertise relevant to the Objective Function 
2. An iterative process to force me to upload relevant context to the decision 
3. An application of the Values, and Constraints to reduce the problem space to a couple choices I can accept or alter
4. A board vote on the options as well as quantitative scoring
5. A final recommendation

Whenever I need to make a big decision, my agreement is to use this system if at all possible. 

Per the example – you might be tempted to work over the weekend if you have a big product launch coming. You might be gearing up to tell your wife. Instead, if you’ve “fired yourself” - you would run a prompt that used your decision making system and follow the decision that had the highest score. 

### 4 Tactical Tracking

Most of the time, you’re not making decisions. You’re taking action. The question is, how well are those actions going and contributing to your Objective Function?

A tactical system has:
1. A way for you to upload what you’ve worked on for your full time job. I built tools in Discord for me to upload my Pomordoros (25 minute blocks of work). 
2. A context relevant way for you to upload other things that have moved your Objective Function the right direction. If your objective function is reaching enlightenment, you might want specific tooling for meditation. If your objective function is athletic, workout logging could make sense. 
3. A KPI sheet - A KPI sheet should give you an idea of how much work you’re doing and how effective that work is at moving you towards your goals. It should be something you can look at every day. And it should be referenced in your system if possible. 

### 5 Compliance
 
Ideally a compliance system should have 
1. A morning check in, similar to a corporate stand up - where goals are set
2. An evening check in where KPIs get updated, reflected upon and progress is tracked

The compliance system should have push notifications to insist that you actually follow through. If you ignore the push notifications, that should be logged and flow back into your KPIs. I call these “compliance events” - i.e. User Did Not Show Up to Stand Up. It sounds inhumane but they are quite similar to what is common at most start ups. Why would we demand less of our own lives? 

### 6 Coaching / Error Handling

A coaching system has four major elements
1. A weekly recap of how KPIs are tracking, with wins, losses and context relevant recommendations
2. A chatbot with the full context from the recaps that I can interact with to brainstorm ways to reach my objective function as well as to motivate myself
3. A system to ingest personal context from coaching chats. This ensures the systems have a good and full picture of both my ethical boundaries as well as my current emotional state.
4. The “professional help” off ramp/ onramp. There are some situations where OpenAI and other AI based systems will deem themselves unworthy (i.e. severe emotional distress, major life events like divorce or death, and legal situations) and suggest the user gets professional help - such as a trained doctor, financial advisor, lawyer, therapist etc. As a result there needs to be a system for the user to voluntarily upload the content of these consultations back into the system, or upload the key summaries in a way that preserves confidentiality and upholds ethical and legal considerations. 

### 7 Indoctrination 

Imagine your coach is Tony Robbins, your priest or your guru. Indoctrination are the exercises he assigns you to improve your buy in and performance.

Indoctrination consists of:
1. Mantras to be repeated
2. NLP tactics such as hypnosis or suggested journal writing

And tooling for each of these. 

### 8 System Meta and Feature Suggestions 

The system should log 
1. How much each part of the system is being used
2. KPI breaches - i.e. when the user has stopped showing up to stand up/ or has stopped goal setting, indoc, journaling etc
3. Periodic user feedback 

Each month the system should generate a report of what is working and what isn’t to generate a feature backlog to be implemented. In this way, you’re not firing yourself to be replaced with a static manager, but rather a dynamically improving architecture.

## Conclusion and Next Steps

In conclusion - I don’t think I’m sacrificing my freedom by firing myself. But rather choosing to get rid of impulsivity and child-like short-termism, replacing it with technology augmented context relevant judgment with world-class mental models. Much as you might opt to move out of an anarchy, and become the citizen of a Republic. I believe that by doing so I will give up some "freedom" but gain much greater capability. This is, of course, an experiment rather than an argument (and certainly not advice) and I’m at the beginning of this journey. 

Nonetheless, I’m excited about living in a world where technology makes us smarter and better, instead of weak and addicted - and hoping to contribute to that vision as best I can. 

Indeed - the systems are now live. I did not decide to publish this article. I just uploaded the context, ran the prompts, got the buy in and pushed the button. We will see what happens next. 
