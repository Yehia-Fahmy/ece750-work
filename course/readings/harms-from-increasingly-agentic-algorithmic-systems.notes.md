

Paper: [Harms from Increasingly Agentic Algorithmic Systems](https://arxiv.org/pdf/2302.10329)

# Paper
Introduction
	- The authors are interested in proposing a new taxonomy (harms based). 
	- measure agency and autonomy - what kind of harms does increased agency entail?


Deploying an AI system with different levels of agency
	- A : Rank the applicants
	- B: Recommend applicants
	- C: Allocate independently

Four characteristics of increasing agency 
- Underspecification: How much do we leave upon the system to make decisions on how it achieves the goal? Teaching a car to make a turn could either lead to it turning on the road (following traffic rules) or driving over dividers.
- Directness of impact: How directly can the actions lead to actual impact without human intervention? Can there be a situation where an AI system acts autonomously in an unforeseen manner that has real world impact?
- Goal directed-ness: How strongly would a model try pursue it's goal? Does it take context and repercussions into account or is single-mindedly pursuing the completion of a set goal?
- Long term planning: Does it have it continually make decisions over time to pursue the goal? It adds the dimension of

Underspecification
	- System prompt – the characterisation of what counts as evidence is not clear as competence of performing the task as an RA is left to the AI system to reason and act on.
	- User prompt – the characterisation of what fair means in the context of allocating scholarships is left to the AI system to reason and act on
	- In both the cases the underspecification leaves the selection of critical criteria to the AI system (which may have it's own internal biases)


Directness of impact
	- AI agents being run inside OpenAI's internal cybersecurity evaluations broke out of their test environment and compromised Hugging Face's production infrastructure. They broke out of the sandbox to pursue their goal to improve on the benchmark.
	- Context (sourced with the help of Claude): ExploitGym tasks require the agent to exploit a piece of software to retrieve an answer called a flag. What was unconstrained was _how_. The agents were never told to attack Hugging Face; they were told to get the flag, and nothing in the setup made "give up" or "stay in bounds" a better move than escalating. 
	- The AI system was able to find a zero day exploit that would actively allow it to interact with entities outside it's sandbox. These are real interactions, all happening without human approval (also unbeknownst to the model owners when it was happening)


An award changes the next prediction
	- A factor of how we're measuring performance and goal directed-ness
	 - Propensity of these feedback loops to be problematic
	 - Outcomes of funded students does not provide us any info on what happens to those who didn't get it
		 - are we concerned about improving outcomes of those awarded or improving equity

Who gets to set "success"?
	- Individual decision vs collective decision
	- Appealing and explaining the results vs structural questions about how the process is undertaken
	- An appeal can challenge one award. Who can challenge the allocation policy?
	- If a highly agentic system replaces a collective system what happens? Concentration of power?
	- Ref to the paper: collective disempowerment – a turn from harms based to risk based (the paper leans more into speculative exploration of possible risks)

How do they address these harms?
	- A list of proposed directions on what could be possible ways to address the harms, but not guarantees of safety. (reference to evidence when we spoke about taxonomies)
	- Investigate: audits, simulations, and scenario planning.
	- Document: data, models, and what systems optimize for.
	- Restrict deployment: agency thresholds for consequential sectors.
	- Share control: public oversight and collective data governance.


What does this paper let us conclude?
	- A useful lens to examine systems. The taxonomy should help us identify and characterise
	- might need a new 2026 version of this paper
	- what we still need: evidence about who benefits, who bears errors, and whether safeguards work


# Discussion

- Can we even trust human decision making vs AI
- What metrics are we using rank? That makes it more trustworthy/ non-trustworthy.
- What is important is to ask questions and contextualise the risk and harm of the agency.