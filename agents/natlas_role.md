# N-ATLAS Role in Alaafia — Scientific Justification

## What N-ATLAS is NOT
N-ATLAS is not the "smartest" agent. It does not have superior causal reasoning capability compared to Llama 3.1. Using it as a judge because it is "Nigerian" without scientific justification would be tokenism, not methodology.

## What N-ATLAS IS
N-ATLAS is a Llama-3 8B model fine-tuned on approximately 400 million tokens of Nigerian multilingual content — Hausa, Igbo, Yoruba, and Nigerian-accented English — sourced from Nigerian news, civic content, and culturally relevant datasets. This fine-tuning gives it three specific capabilities that Llama 3.1 lacks:

### 1. Nigerian Social Context Grounding
N-ATLAS has been exposed to how Nigerian health, poverty, and social inequality are discussed in Nigerian public discourse. When it evaluates a causal pathway involving a North East woman with no education and high parity, it draws on representations of that social reality from Nigerian sources — not from Western epidemiological literature alone.

### 2. Linguistic and Cultural Nuance
Health-seeking behaviour, household decision-making dynamics, and community health practices in Nigeria are discussed differently in Nigerian sources than in international literature. N-ATLAS has learned these representations. This matters for the equity interrogation layer where we ask whether a proposed pathway makes sense in the Nigerian social context.

### 3. Policy Language Translation
N-ATLAS can evaluate whether a proposed causal pathway would be legible and actionable to Nigerian health policy audiences — the Federal Ministry of Health, UNICEF Nigeria, state-level nutrition programmes. This is distinct from scientific correctness and is a specific contribution of the cultural grounding layer.

## The Specific Role N-ATLAS Plays
N-ATLAS is the DAG Judge and Equity Interrogation agent. Its specific task is:

1. Given a proposed and critiqued causal DAG from Llama agents, evaluate whether the final accepted pathway is culturally and contextually coherent for the Nigerian zone it describes.

2. Assess whether the equity implications of the pathway — why this outcome is worse in this zone than another — make sense given Nigerian social realities.

3. Translate the accepted pathway into policy language that Nigerian health system actors would recognise and act on.

## What N-ATLAS Does NOT Do
N-ATLAS does not adjudicate on biological mechanisms. It does not evaluate statistical validity. It does not replace Llama 3.1 for structural causal reasoning. Those tasks remain with the Proposer and Critic agents.

## Validation of This Role Assignment
The assignment of N-ATLAS to the Judge role will be validated by:
1. Comparing N-ATLAS Judge outputs against Llama 3.1 Judge outputs on the same tokens
2. Having Nigerian epidemiologists rate the cultural appropriateness of outputs from each model
3. Documenting specific cases where N-ATLAS produces more contextually grounded equity flags than Llama 3.1

## Citation
N-ATLAS: Awarri Technologies and the Federal Ministry of Communications, Innovation and Digital Economy, Nigeria. 2025. Fine-tuned on Llama-3 8B with Nigerian multilingual instruction data.
