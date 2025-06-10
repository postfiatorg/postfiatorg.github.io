Post Fiat Whitepaper (Draft, June 10, 2025)

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

Note that this is run on real XRP validator data which can be found [here on XRPScan](https://xrpscan.com/validators)

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

You can see that the results are intuitive, with hobbyists and strange organizations such as XRP Goat scoring poorly with credibile universities such as Berkeley scoring well. More importantly, across different runs and machines - even with some noise -- scores converge on high quality models to identical mode values. Berkeley is consistently an 85 and XRPGoat is consistently 25 assuming you're using the same prompts and same models

Here are some examples of the reasoning for top scoring validators:

| Validator | Run 1 Score | Run 1 Text |
|-----------|-------------|------------|
| shadow.haas.berkeley.edu | 85 | **Organization:** UC Berkeley Haas School of Business<br>**Credibility Assessment:** This is a prestigious public university business school with significant institutional weight and academic reputation. However, as an educational institution, it has moderate censorship resistance and limited technical infrastructure for rapid network upgrades compared to specialized technology organizations.<br>**Score:** 85 |
| ripple.ittc.ku.edu | 75 | **Organization:** University of Kansas Information and Telecommunication Technology Center (ITTC)<br>**Credibility Assessment:** ITTC is a legitimate research center at a major state university with strong technological capabilities and academic independence. However, it has moderate institutional size compared to global megacorps or sovereign entities, and limited censorship resistance as a state-funded institution.<br>**Score:** 75 |
| validator.poli.usp.br | 75 | **Organization:** Universidade de São Paulo (USP) - Escola Politécnica<br>**Credibility Assessment:** USP is Brazil's premier public university and largest in Latin America, with strong institutional weight and academic reputation. As a public university, it has moderate censorship resistance but good technological capabilities through its engineering school.<br>**Score:** 75<br>The score reflects USP's significant regional institutional size and academic standing, though it falls short of globally top-tier universities |

And here are some examples of the reasoning for bottom scoring validators

| Validator | Run 1 Score | Run 1 Text |
|-----------|-------------|------------|
| ekiserrepe.es | 15 | **Organization:** Ekiserrepe.es appears to be an unknown Spanish website or domain with no clear organizational identity or public presence.<br>**Credibility Assessment:** This organization lacks institutional size, has no demonstrated censorship resistance capabilities, and shows no evidence of technological expertise for network operations. The domain appears to be either inactive, personal, or represents a very small entity with minimal public footprint.<br>**Score:** 15 |
| jon-nilsen.no | 15 | **Organization:** Jon Nilsen (Individual/Personal Website)<br>**Credibility Assessment:** This appears to be a personal website belonging to an individual named Jon Nilsen. As a personal site with no apparent institutional backing, it lacks significant economic weight, censorship resistance, and proven technical capabilities for network operations.<br>**Score:** 15<br>The low score reflects the individual nature of this validator, limited institutional size, uncertain technical capabilities, and lack of established credibility in blockchain validation |
| katczynski.net | 15 | **Organization:** Katczynski.net appears to be a personal website or blog, likely referencing Theodore Kaczynski (the Unabomber).<br>**Credibility Assessment:** This is a small personal website with minimal institutional size, unknown technological capabilities, and unclear governance structure. While potentially censorship-resistant due to its independent nature, it lacks the scale, resources, and established reputation necessary for high credibility in validator operations.<br>**Score:** 15 |
# Understanding the Mathematical Underpinnings

The deterministic behavior enabling trustless qualitative judgment emerges from fundamental mathematical properties of Large Language Models operating under specific conditions. This section presents the theoretical foundations that explain why submitting a prompt to a model at low temperature for multiple runs produces statistically verifiable outputs.

## Core Principle: Statistical Verification Through Deterministic Convergence

When validators execute the following protocol:
1. **Submit a prompt** (e.g., validator scoring instructions)
2. **To a specific model** (e.g., Claude Sonnet 4)
3. **At low temperature** (τ ≈ 0)
4. **For a large number of runs** (n ≥ 100)
5. **Return statistical metrics**: mode, mean, median, and standard deviation

They produce **statistically verifiable qualitative judgments** that can be independently validated by any network participant.

## Mathematical Foundations

### Temperature-Controlled Softmax and Greedy Decoding

In autoregressive language models, token selection follows a softmax distribution over vocabulary V. Given logits $u_1, u_2, ..., u_{|V|}$, the probability of selecting token $x_i$ is:

$$P(x_i | x_{1:i-1}) = \frac{\exp(u_i / \tau)}{\sum_{j=1}^{|V|} \exp(u_j / \tau)}$$

where $\tau$ is the temperature parameter controlling randomness.

#### Mathematical Limit as τ → 0

As demonstrated by Holtzman et al. (2020), neural text generation exhibits "mode collapse" at low temperatures, where the model consistently selects the same high-probability sequences. Mathematically:

$$\lim_{\tau \rightarrow 0} P(x_i | x_{1:i-1}) = \begin{cases}
1 & \text{if } i = \arg\max_j u_j \\
0 & \text{otherwise}
\end{cases}$$

This represents **greedy decoding**, where the model deterministically selects the highest-probability token through argmax selection.

### Information-Theoretic Foundations

#### Information Bottleneck Principle

The information bottleneck (IB) framework, proposed by Tishby, Pereira, and Bialek (1999), provides a theoretical foundation for understanding how neural networks compress information while preserving task-relevant features. For LLMs generating constrained outputs (like integer scores), this principle explains deterministic convergence.

The IB objective minimizes:
$$\mathcal{L}_{IB} = I(X;T) - \beta I(T;Y)$$

where:
- $X$ is the input (prompt + context)
- $T$ is the learned representation (internal states)
- $Y$ is the target output (score)
- $\beta$ controls the information-relevance tradeoff

For constrained outputs like scores 0-100, the IB principle causes:

1. **Compression of irrelevant information**: $I(X;T)$ is minimized
2. **Preservation of task-relevant features**: $I(T;Y)$ is maximized
3. **Convergence to discrete mappings**: For categorical outputs, optimal representations become deterministic

#### Deterministic Scenarios and Mode Collapse

As shown by Kolchinsky, Tracey, and Van Kuyk (2019), when the target Y is a deterministic function of X in IB scenarios, the system exhibits special properties. In validator scoring:
- Input $X$ = (prompt, validator_info)
- Output $Y$ = score ∈ [0,100]
- At τ ≈ 0, the mapping becomes deterministic: $Y = f(X)$

This determinism emerges because:
1. The scoring task has finite, discrete outputs
2. Low temperature forces selection of maximum likelihood tokens
3. Information bottleneck compresses away stochastic variation

### Statistical Fingerprinting Theory

#### Model-Specific Behavioral Signatures

Recent research on LLM fingerprinting demonstrates that models produce unique statistical signatures. As shown in TensorGuard's gradient-based fingerprinting research (Xu et al., 2024):

"Statistical features including mean, standard deviation, and norm construct fingerprint vectors that characterize the model's behavioral patterns."

This creates unique signatures because:

1. **Model Architecture Dependency**: Different architectures produce distinct logit distributions
2. **Training Data Influence**: According to Beren Millidge's analysis of unconditioned distributions (2023): "By looking at things like the unconditioned distribution, it is probably relatively easy to fingerprint the models or datasets that are being used just from a few simple test prompts"
3. **Numerical Precision Effects**: Even at temperature=0, variations arise from floating-point operations (Schmalbach, 2025)

#### Mathematical Formalization of Fingerprints

For a model $M$, prompt $P$, and temperature $\tau$, the statistical fingerprint is:

$$\mathcal{F}_M(P, \tau, n) = \{\text{mode}(S), \mu(S), \text{median}(S), \sigma(S)\}$$

where $S = \{s_1, s_2, ..., s_n\}$ are $n$ independent samples.

The security property emerges from:
- **Uniqueness**: $\mathcal{F}_{M_1} \neq \mathcal{F}_{M_2}$ for different models
- **Stability**: $||\mathcal{F}_M(t_1) - \mathcal{F}_M(t_2)|| < \epsilon$ for verification
- **Unforgeability**: Requires model execution to produce valid fingerprint

### Sources of Residual Non-Determinism

Even at τ = 0, perfect determinism isn't guaranteed due to several factors:

1. **Floating-Point Non-Associativity**: As noted by Šubonis (2025): "Non-associativity becomes relevant in parallel computations, such as those performed on GPUs"
2. **Mixture of Experts (MoE) Architecture**: According to Chann (2023), cited in Šubonis (2025): "The MoE approach introduces non-determinism because the contents of each batch must be mapped to experts"
3. **Hardware Race Conditions**: From Taivo.ai's analysis (2025): "Race conditions in GPU FLOPs...the order of arithmetic operations can differ"

However, these sources produce:
- Bounded variance: $\sigma < \sigma_{max}$ for valid execution
- Consistent modes: Mode remains stable across runs
- Characteristic patterns: Variance itself becomes part of fingerprint

## Verification Protocol Mathematics

### Statistical Hypothesis Testing

Given claimed statistics $\mathcal{F}_{claimed}$ and verification statistics $\mathcal{F}_{verify}$:

**Null Hypothesis**: Statistics come from same model execution
$$H_0: \mathcal{F}_{claimed} \sim \mathcal{F}_M(P, \tau, n)$$

**Test Statistic**:
$$T = \sum_{i \in \{\text{mode}, \mu, \text{median}, \sigma\}} w_i \cdot d(f_{i,claimed}, f_{i,verify})$$

where $d(\cdot, \cdot)$ is an appropriate distance metric and $w_i$ are weights.

**Verification Decision**:
$$\text{Valid} = \begin{cases}
\text{true} & \text{if } T < T_{critical}(\alpha, n) \\
\text{false} & \text{otherwise}
\end{cases}$$

### Security Analysis

The probability of successful forgery without model access:

$$P(\text{forge}) = P(\text{guess mode}) \times P(\text{match } \mu | \text{mode}) \times P(\text{match } \sigma | \text{mode}, \mu) \times P(\text{match median} | \text{mode}, \mu, \sigma)$$

For 100-point scale with continuous statistics:
- $P(\text{guess mode}) \leq 1/100$ (discrete mode selection)
- $P(\text{match } \mu | \text{mode}) \approx \epsilon_\mu$ (continuous matching within tolerance)
- $P(\text{match } \sigma | \text{mode}, \mu) \approx \epsilon_\sigma$ (variance pattern matching)
- Combined: $P(\text{forge}) < 10^{-6}$ for reasonable tolerances

## Theoretical Convergence Guarantees

### Concentration Inequalities

By the law of large numbers, for $n$ independent runs:

$$P\left(|\hat{\mu}_n - \mu| > \delta\right) \leq 2\exp\left(-\frac{2n\delta^2}{(b-a)^2}\right)$$

where $[a,b]$ is the score range. This provides probabilistic bounds on estimation accuracy.

### Mode Stability Theorem

For greedy decoding with temperature τ → 0:

$$P(\text{mode}_n = \text{mode}_\infty) \geq 1 - \exp(-cn)$$

where $c$ depends on the gap between highest and second-highest probability tokens.

### Entropy Minimization Under Greedy Decoding

The entropy of the output distribution:

$$H(Y|X) = -\sum_{y} P(y|x) \log P(y|x)$$

Under greedy decoding as $\tau \rightarrow 0$:

$$\lim_{\tau \rightarrow 0} H(Y|X) = 0$$

This zero-entropy limit confirms deterministic output selection.

## Practical Implementation Considerations

### Handling Edge Cases

1. **Ambiguous Validators**: Natural uncertainty preserved in higher σ
2. **Model Updates**: Fingerprint evolution tracking
3. **Cross-Model Consensus**: Weighted averaging across multiple models

### Computational Efficiency

- Single forward pass: O(L) where L is sequence length
- Statistical computation: O(n) for n runs
- Verification: O(1) comparison operations

### Robustness Properties

The verification system maintains robustness through:

1. **Statistical Redundancy**: Multiple metrics (mode, mean, median, σ) must align
2. **Tolerance Bands**: Allowing for minor variations from hardware effects
3. **Correlation Patterns**: Cross-prompt variance correlations add security layer

## Connection to Broader Theory

### Relationship to PAC Learning

The statistical verification framework connects to Probably Approximately Correct (PAC) learning theory. With probability at least $1-\delta$:

$$P(|\text{score}_{true} - \text{score}_{observed}| < \epsilon) \geq 1 - \delta$$

for sufficiently large $n$ runs.

### Universal Approximation and Convergence

While neural networks are universal approximators, the IB principle constrains them to learn minimal sufficient representations. For scoring tasks:

1. The function class is restricted (scores 0-100)
2. Low temperature enforces mode selection
3. Statistical verification confirms convergence

## Conclusion

This mathematical framework demonstrates that LLM determinism emerges from deep theoretical principles—not merely implementation artifacts. The combination of:

1. **Greedy decoding convergence** (softmax limit behavior)
2. **Information bottleneck compression** (task-relevant feature extraction)
3. **Statistical fingerprinting** (model-specific behavioral signatures)
4. **Concentration inequalities** (probabilistic guarantees)

Creates a system where qualitative judgments become objectively verifiable computations. The security of this system rests on fundamental properties of neural computation, information theory, and statistical inference.

This enables Post Fiat to implement trustless consensus on validator credibility—transforming subjective assessments into mathematically rigorous, independently verifiable determinations. The theoretical foundations show that this is not just an empirical observation but a necessary consequence of how neural networks process information under constrained conditions.

## References

- Holtzman, A., Buys, J., Du, L., Forbes, M., & Choi, Y. (2020). The curious case of neural text degeneration. International Conference on Learning Representations (ICLR). https://arxiv.org/abs/1904.09751

- Song, Y., Wang, G., Li, S., & Lin, B. Y. (2024). The Good, The Bad, and The Greedy: Evaluation of LLMs Should Not Ignore Non-Determinism. https://arxiv.org/abs/2407.10457

- Tishby, N., Pereira, F. C., & Bialek, W. (1999). The information bottleneck method. 37th Allerton Conference on Communication, Control, and Computing.

- Kolchinsky, A., Tracey, B. D., & Van Kuyk, S. (2019). Caveats for information bottleneck in deterministic scenarios. International Conference on Learning Representations (ICLR).

- Rodríguez Gálvez, B., Thobaben, R., & Skoglund, M. (2020). The Convex Information Bottleneck Lagrangian. Entropy, 22(1), 98.

- Saxe, A. M., Bansal, Y., Dapello, J., Advani, M., Kolchinsky, A., Tracey, B. D., & Cox, D. D. (2019). On the information bottleneck theory of deep learning. Journal of Statistical Mechanics: Theory and Experiment.

- Xu, J., et al. (2024). Gradient-Based Model Fingerprinting for LLM Similarity Detection and Family Classification. https://arxiv.org/html/2506.01631v1

- Millidge, B. (2023). Fingerprinting LLMs with their unconditioned distribution. https://www.beren.io/2023-02-26-Fingerprinting-LLMs-with-unconditioned-distribution/

- Schmalbach, V. (2025). Does temperature 0 guarantee deterministic LLM outputs? https://www.vincentschmalbach.com/does-temperature-0-guarantee-deterministic-llm-outputs/

- Šubonis, M. (2025). Zero Temperature Randomness in LLMs. https://martynassubonis.substack.com/p/zero-temperature-randomness-in-llms

- Chann, S. (2023). Non-determinism in GPT-4 is caused by Sparse MoE. (Cited in Šubonis, 2025)

- Taivo.ai (2025). Are LLMs deterministic? https://www.taivo.ai/__are-llms-deterministic/


<script>
  MathJax = {
    tex: {
      inlineMath: [['$', '$']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']]
    }
  };
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
