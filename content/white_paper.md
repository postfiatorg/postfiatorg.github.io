
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

## Canonical Example

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




Sources:

1. 
