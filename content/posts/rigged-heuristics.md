---
author: ["goodalexander"]
title: "Heuristics for Rigged Markets"
date: 2023-12-27T11:21:29Z
draft: false
---
going to talk a bit about some things I've learned about rigged markets, signal extraction and how to fit market manipulation into your overall mosaic 

## Rule 1: understanding you're a gremlin not a genius.

if you're reading this chances are you're not as smart as quants so don't try to be. I practice a very special variety of quantitative trading, called "find someone rigging a market and front-run them". Leave other quant strategies (like stat arb, or complex machine learning alphas) to PHDs. What I do is not even quant trading. It just uses quantitative methods to express a view that an asset is being rigged.

Typically rigged markets are a pre-requisite for bubbles, and crashes. You remove volatility and create free lunches, things get out of hand. I would argue you should *never even trade a market that has no sign of being rigged*. because why would you? who is your counterparty?  

If markets were not rigged I would not even trade or do this for a living. 

Don't be a monkey throwing darts at a board. BET ON SURE THINGS

Rigging is not a conceptual or intellectual idea, but  a pragmatic, or even mundane reality. Sure some guy at Davos decides how it's going to play out but when it comes to the execution there's some muppet in charge of doing the rigging. Is Tether rigging Bitcoin? Well - you can test that, and monetize it if it's true ;)

Let's talk about some heuristics for said 'signal extraction'

## Heuristic 1: you need a 'peer cloud' that is unrelated to the studied manipulation. 
For example, if you think that the BOJ is buying the EWJ ETF, you need a group of peers that is not inside of the EWJ ETF but is listed on the Nikkei - just as an example

in crypto for example, if you're studying Binance manipulation you should be taking an asset that is listed on Binance and a highly correlated asset that is listed

## Heuristic 2: you need to properly  adjust the relationship between the rigged asset and the peer cloud. 
part of the  adjustment process should be 
a. Dropping members out of the peer cloud when the standard deviation of their correlation spikes and the correlation goes down 
b. creating a system that creates a peer cloud on a rolling basis. this is hard and needs to incorporate heuristic 1. For example, the list of stocks in EWJ (the Japan ETF) is dynamic. If you're studying EWJ manipulation from the BOJ (a real phenomena) you need to peer it with stocks that aren't in the ETF basket. That means you need historical EWJ membership. Similarly if you're looking at Binance membership, there are new exchange listings. You need dates of those listings. What is the return of Listed vs Unlisted correlated cryptos?
c. when creating the market neutral "residual return" or alpha of the rigged asset, make sure to account for the beta of the asset to the basket of peers

Curating the peer cloud and weighting it correctly is important because it allows you to do an effective backtest. 

## Heuristic 3: you need to determine that an asset is being rigged. 

This means that statistically - someone is jamming the index vs its beta adjusted peer cloud over a "window". Here are some useful definitions of "windows" that someone might consider rigging an asset

a. After the rigged asset is down a lot
b. When the rigged asset is not trading a lot (low volume periods)
c. During holidays or weekends (see b) or end of months or any meaningful calendar date (such as futures rolls, dividends, or earnings releases) 
d. After the rigged asset is up a lot on low volume 
e. After the rigged asset is down a lot versus its peers 

## Heuristic 4: you need a written (or strongly implied) confirmation of when the rigging was started. 

For example if you're studying the Ripple foundation dumping XRP - there are periods when these sales have been restricted. Similarly there are periods where the Fed stopped balance sheet expansion or took it into reverse. 

Whatever heuristic of rigging you observed needs to be window dependent for you to accept that it is occurring 

The profitability of betting on the rigged pattern persisting should be higher during periods where the market was explicitly being rigged versus when it was not being rigged.

## Heuristic 5: You should determine the strength of the counterparty doing the rigging. 

A high strength counterparty like the Central Bank is one type. A lower strength counterparty like a market making firm, or message board is a low strength counterparty.

If you are evaluating a low strength counterparty, it's important to remember you're trading market manipulation. Market manipulation has a consistent pattern I call "the Exit Scam". An exit scam is a catastrophic down wick on high liquidity. It can come in the form of a share offering, insider selling. After the exit scam comes, the rigging pattern should stop for a while. 

Pragmatically this means you need some quantitative definition for "has exit scammed recently"

A high strength counterparty should have some effect when they exit the market as well , that you should be able to measure but it less extreme than the exit scam dynamic. This usually manifests in terms of a stock index having a lower valuation vs its peers

## Heuristic 6: Rigged markets consistently create retail feeding frenzies - but usually well after they started being rigged.

Market rigging is one of the best strategies to overlay with retail data tracking for this reason. 

Finally - once you've detected a "rigging" you need a checklist to initialize the strategy.
1] Who is doing the rigging (most likely)
2] What indication is there publicly that the rigging has started (central bank minutes, telegram chat, reddit forum, company management statement etc)
3] Scraping methodology or process to determine that the rigging has stopped
4] Production infrastructure to apply the strategy to said market 
5] sizing determination 

Trading rigged markets is definitely profitable but a lot of the times it doesn't scale particularly well because you're basically front running someone doing small incremental trades on a somewhat regular basis. But it's a good fixed income vanilla return

The real juice comes from looking at the net effect of the rigging and sizing up bets on bubbles, feeding frenzies or potentially shorting ahead of exit scams. 

The end of asset class rigging is also itself a qualitative input. For example, the Carbon market - was at one point, rigged. And then, one day it stopped being rigged. This preceded a very large drop in the clean energy sector that coincided with decline in demand from European buyers.

Can you make a living profiting on stuff like this sure? But I think you can get a scale invariant outcome mixing it with judgment, data tracking and other more proprietary things. I view this concept less as a pure alpha strategy and more a lens to view the world through, which is why I think it's productive to share it.

More philosophically, a trader need not be upset that the society he's a part of is being dominated by corrupt overlords. Because without them, he would be a fortune teller, peddling the nonsensical belief that he sees the future better than others. 

Thus - understanding market manipulation is an essential part of the non-fundamental mosaic for those monetizing the post-capitalist reality .
