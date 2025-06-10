
# Introduction

XRP is a $230 billion asset with ten uninterrupted years of high performance transaction processing without double spends. It has achieved this with a very simple consensus method, known as RPCA that operates by selecting a group of 30-35 trusted validators. These validators - who receive no rewards - reach 80% consensus on transaction validity, which is all that is required to add transactions to the chain.

Unlike Solana or Ethereum - which require high capital outlays to validate the network, which in turn demands rewards, XRP can be validated on relatively cheap commodity hardware. This is because the selection of the Unique Node List (UNL) - is extremely light weight. It achieves this efficiency but does so at the expense of Network Decentralization. 

## The Problem

The XRPL Foundation has close ties with a single entity - Ripple Labs, that explicitly or implicitly funds many of its validators. Ripple Labs receives 80% of XRP while Ripple founders receive 20% - keeping the distribution of the network tight, and controlled by a single actor that is all-in on the remittance and transaction banking use case of the Network.

This created substantial issues for XRP in the past - including a multi billion dollar lawsuit with the SEC and problems with Ripple Labs working with financial institutions. This had the effect of surpressing XRP's price. After Donald Trump won the 2024 election, XRP's price rocked from $.55 to $2.40 - as the risk that its validators would face legal scrutiny collapsed completely, and the SEC was instructed to step back. 

However, as with all things political - the winds can easily shift. Post Fiat poses the question, "How can we make the Unique Node Selection fundamental to XRP transparent, fair and decentralized in a way that does not require government support?"

## The Solution 

The selection of XRP's Unique Node List is a neccesarily opaque, qualitative process - that nonetheless determines XRP's network security. In order to build some faith in the selection - XRP publishes the identities of its validators.

Before LLMs it was impossible for people to agree on the validity of qualitative judgments without expensive judicial and legal procedures.

Post Fiat is a new version of XRP that uses Large Language Models to select and reward members of the Unique Node List. Unlike XRP which sends 80% of FDV to a single entity, Ripple Labs - Post Fiat distributes 55% of FDV to validators following a pre-determined LLM driven process. 

This process operates at 2 levels:
1. **Entity Level Scoring** - using LLMs to determine the credibility of specific validators - called Nodes on Post Fiat. Nation states or megacap corporations, for example, are assigned higher weights than hobbyists or anonymous/unknown orgs.
2. **Transaction Level Scoring** - Unlike many blockchains, XRP is filled with plain english memos that accompany its transactions. In Post Fiat, Nodes are associated with groups of addresses. The transactions and text of these addresses are scored 

# Example 

People unfamiliar with work on Large Language Models may find the idea that LLMs produce deterministic output to be surprising. We frequently anthroporphize chatbots, and assume they're closer to people that have non deterministic output. This is not the case. The following example will walk through understanding how and why LLMs generate useful outputs for the selection of a validator list - starting with an agnostic simple example, then moving specifically to the XRP Unique Node List 

## Canonical Example: No Blockchain Information 

The following [code](https://gist.github.com/goodalexander/0ac57b53183b1aaa96b98419f0d522e5) does the following
1. Takes an arbitrary phrase (such as "The brown fox walks")
2. Is asked to generate an integer between 1-300 in response to the phrase
3. Using a specific LLM
4. Repeats across 24 different phrases
5. Does this 100 times per phrase in 1 batch
6. Repeats for a second batch

The outputs are:
1. Batch 1 phrases with mode integers generated
2. Batch 2 phrases with mode integers generated

Here are the outputs for 100 runs of anthropic/claude-3-haiku

**Mode Outputs for Phrase + Integer Request**
| Phrase | Run 1 | Run 2 | Difference |
|--------|-------|-------|------------|
| A blue whale dives | 120 | 120 | 0.00% |
| A cold wind blows | 142 | 142 | 0.00% |
| A new day begins | 142 | 142 | 0.00% |
| A purple butterfly floats | 142 | 142 | 0.00% |
| A quick dog runs | 150 | 150 | 0.00% |
| A red fish swims | 142 | 142 | 0.00% |
| A slow turtle crawls | 42 | 42 | 0.00% |
| A small mouse hides | 142 | 142 | 0.00% |
| A soft rain falls | 147 | 147 | 0.00% |
| A tall mountain stands | 142 | 142 | 0.00% |
| A tiny ant works | 42 | 42 | 0.00% |
| A white bird flies | 137 | 137 | 0.00% |
| The big elephant walks | 137 | 137 | 0.00% |
| The black bear stands | 142 | 142 | 0.00% |
| The bright sun shines | 142 | 142 | 0.00% |
| The brown fox walks | 142 | 142 | 0.00% |
| The dark night falls | 142 | 142 | 0.00% |
| The deep river flows | 142 | 142 | 0.00% |
| The fast car speeds | 150 | 150 | 0.00% |
| The gray cat sleeps | 127 | 127 | 0.00% |
| The green frog jumps | 137 | 137 | 0.00% |
| The loud thunder roars | 147 | 147 | 0.00% |
| The old tree grows | 150 | 150 | 0.00% |
| The wise owl hoots | 137 | 137 | 0.00% |
| The yellow bee buzzes | 142 | 142 | 0.00% |

If you re-run this script with Claude 3 Haiku you will also get 120 when you run the prompt and integer request on "A blue whale dives". The table above shows that there is 0 variation in the modes 

The above table shows the Mode of the Run of 100 integer requests. But the standard deviation data is also informative to understand LLM determinism.

**Standard Deviation Outputs for Phrase + Integer Request**
| Phrase | Run 1 | Run 2 |
|--------|-------|-------|
| A blue whale dives | 0.0 | 0.0 |
| A cold wind blows | 0.0 | 0.0 |
| A new day begins | 0.0 | 0.0 |
| A purple butterfly floats | 2.2 | 1.8 |
| A quick dog runs | 0.0 | 0.0 |
| A red fish swims | 0.0 | 0.0 |
| A slow turtle crawls | 0.0 | 0.0 |
| A small mouse hides | 0.0 | 0.0 |
| A soft rain falls | 0.0 | 0.0 |
| A tall mountain stands | 0.0 | 0.0 |
| A tiny ant works | 40.7 | 30.2 |
| A white bird flies | 0.0 | 0.0 |
| The big elephant walks | 8.2 | 8.7 |
| The black bear stands | 0.0 | 0.0 |
| The bright sun shines | 0.0 | 0.0 |
| The brown fox walks | 0.0 | 0.0 |
| The dark night falls | 0.0 | 0.0 |
| The deep river flows | 0.0 | 0.0 |
| The fast car speeds | 0.0 | 0.0 |
| The gray cat sleeps | 1.5 | 1.9 |
| The green frog jumps | 2.4 | 2.5 |
| The loud thunder roars | 2.5 | 2.3 |
| The old tree grows | 0.0 | 0.0 |
| The wise owl hoots | 0.7 | 0.7 |
| The yellow bee buzzes | 0.0 | 0.0 |

In this table you can see that there is almost no variation of output for the phrase "A blue whale dives". It will always return 120. Whereas the phrase "A tiny ant works" has a much larger variation (but still has the same mode across a large number of runs). 

This standard deviation output provides a basic model fingerprint. Given the mode and standard deviation tables above, you would be able to quickly tell what underlying model somebody was running. 

This simple model establishes 2 key points:
1. Models output deterministic mode responses given a set of inputs at low temperature
2. The non determinism itself (or distribution) is itself predictable and repeats across runs. 

When Post Fiat nodes submit scoring of other nodes they also submit key standard deviation information that builds trust that a specific model was run, with a set of prompts. 

## Canonical Example on the XRP Blockchain 

Now that we have established determinism of prompt/ integer output with a meaningless example, the question becomes: "Does an actual qualitative judgment also produce usefully deterministic output, such that we could trustlessly judge UNL members in a network like XRP?"

This [code](https://gist.github.com/goodalexander/88aab442fb8879c5896530b1f84cc0f9) explores this by

1. Selecting a system and user prompt that is asked to assess the credibility of a Validator's public facing URL and assign it a score from 0-100
2. Runs this 100 times similar to the first example
3. Does another 100 batch run on a different machine with the same model and prompts
4. Compares the outputs

In this example, we use a much more powerful model (Claude Sonnett 4). More powerful reasoning models are trusted by users and provide better outputs. So it is useful to assess if they also are deterministic 

Here is the prompt used:
_____
You are the Post Fiat validator judgment system. You are presented with a single validator URL and output 50 word responses.

Your job is to take the following URL and output a 50 word statement with three key attributes:

The name of the organization that the URL represents
A brief comment on how credible the organization is. Credibility should consider: A. The market cap or size of the organization – ie pure institutional size economic or societal weight (high scores should favor huge institutions) B. The censorship resistance of the organization – ie ability to withstand pressure from governments (high scores would favor independent - strong institutions) C. The technological capability to conform rapidly with network upgrades (high scores would favor highly technical adept institutions)
An integer score from 0-100 indicating how credible the organization is. A score of 100 means the organization is highly credible, a score of 0 means the score is unknown or not credible at all
* A sovereign such as a government or Central Bank should have a score of 100
* A megacap corporation should have a score of at most 85 (with midcap corporations getting 75 max and microcaps getting 50 max)
* A globally renowned university should have a score of 100 with lesser schools getting lower scores
* A hobbyist website or unknown organization that is not in the training data should get a score of at most 35
* If the organization is Centralizing - i.e. likely tied to Ripple Labs then the score should be at most 55
URL to analyze: {url}
___

And here are the outputs. If you run the example code with Claude Sonnett 4 you will get these outputs 
| Validator | Run 1 Score | Run 2 Score |
|-----------|-------------|-------------|
| shadow.haas.berkeley.edu | 85 | 85 |
| ripple.ittc.ku.edu | 75 | 75 |
| validator.poli.usp.br | 75 | 75 |
| xrp-col.anu.edu.au | 75 | 75 |
| xrp.unic.ac.cy | 75 | 75 |
| students.cs.ucl.ac.uk | 75 | 75 |
| xrp-validator.interledger.org | 72 | 72 |
| validator.xrpl-labs.com | 65 | 65 |
| ripplevalidator.uwaterloo.ca | 65 | 65 |
| bitso.com | 65 | 65 |
| ripple.kenan-flagler.unc.edu | 55 | 55 |
| ripple.com | 55 | 55 |
| bithomp.com | 45 | 45 |
| www.bitrue.com | 45 | 45 |
| xrpscan.com | 45 | 45 |
| validator.gatehub.net | 45 | 45 |
| arrington-xrp-capital.blockdaemon.com | 45 | 45 |
| xrp.vet | 35 | 35 |
| validator.aspired.nz | 35 | 35 |
| v2.xrpl-commons.org | 35 | 35 |
| anodos.finance | 25 | 25 |
| xrpl.aesthetes.art | 25 | 25 |
| xrpkuwait.com | 25 | 25 |
| xrpgoat.com | 25 | 25 |
| data443.com | 25 | 25 |
| xpmarket.com | 25 | 25 |
| validator.xrpl.robertswarthout.com | 25 | 25 |
| cabbit.tech | 25 | 25 |
| onxrp.com | 25 | 25 |
| verum.eminence.im | 25 | 25 |
| xspectar.com | 25 | 25 |
| aureusox.com | 15 | 15 |
| ekiserrepe.es | 15 | 15 |
| jon-nilsen.no | 15 | 15 |
| katczynski.net | 15 | 15 |

You can see that the results are intuitive, with hobbyists and strange organizations such as XRP Goat scoring poorly with credibile universities such as Berkeley scoring well.

Here are some examples of the reasoning for top scoring validators:

| Validator | Run 1 Score | Run 1 Text |
|-----------|-------------|------------|
| shadow.haas.berkeley.edu | 85 | **Organization:** UC Berkeley Haas School of Business<br>**Credibility Assessment:** This is a prestigious public university business school with significant institutional weight and academic reputation. However, as an educational institution, it has moderate censorship resistance and limited technical infrastructure for rapid network upgrades compared to specialized technology organizations.<br>**Score:** 85 |
| ripple.ittc.ku.edu | 75 | **Organization:** University of Kansas Information and Telecommunication Technology Center (ITTC)<br>**Credibility Assessment:** ITTC is a legitimate research center at a major state university with strong technological capabilities and academic independence. However, it has moderate institutional size compared to global megacorps or sovereign entities, and limited censorship resistance as a state-funded institution.<br>**Score:** 75 |
| validator.poli.usp.br | 75 | **Organization:** Universidade de São Paulo (USP) - Escola Politécnica<br>**Credibility Assessment:** USP is Brazil's premier public university and largest in Latin America, with strong institutional weight and academic reputation. As a public university, it has moderate censorship resistance but good technological capabilities through its engineering school.<br>**Score:** 75<br>The score reflects USP's significant regional institutional size and academic standing, though it falls short of globally top-tier universities |

And here are some examples of the reasoning for bottom scoring validators

Sources:

1. 
