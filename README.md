# GitAra 🦜🎸: **A small function-calling git agent you can run locally**
![gitara](gitara.png)

*Gitara = **git** + **ara**: your local stochastic parrot for git commands (with a knack for music).*

We fine-tuned a small, tool-calling language model to turn plain English into `git` commands with the accuracy of a cloud LLM. Because it's small, you can run it locally on your own machine - no API keys, no cloud dependencies, full privacy.

| Model | Parameters | Accuracy | Model link |
| --- | --- | --- | --- |
| GPT-OSS 120B (teacher) | 120B | 0.92 +/- 0.02 |  |
| **Llama 3.2 3B Instruct (tuned)** | **3B** | **0.92 +/- 0.01** | [huggingface](https://huggingface.co/distil-labs/Distil-gitara-v2-Llama-3.2-3B-Instruct) |
| **Llama 3.2 1B Instruct (tuned)** | **1B** | **0.90 +/- 0.01** | [huggingface](https://huggingface.co/distil-labs/Distil-gitara-v2-Llama-3.2-1B-Instruct) |
| Llama 3.2 3B Instruct (base) | 3B | 0.12 +/- 0.05 |  |
| Llama 3.2 1B Instruct (base) | 1B | 0.0 +/- 0.01 |  |

The tuned 3B model matches the 120B teacher while being **25x smaller** while the 1B model is **within one standard deviation while being 120x smaller.**

---

## Quick Start

### 1. Install Ollama

Install [Ollama](https://ollama.com/) following the instructions on their website.

### 2. Set up the environment

```bash
python -m venv .venv
. .venv/bin/activate
pip install huggingface_hub openai

```

### 3. Download and build the model

```bash
hf download distil-labs/Distil-gitara-v2-Llama-3.2-1B-Instruct --local-dir distil-model
cd distil-model
ollama create gitara -f Modelfile

```

### 4. Run gitara

```bash
python gitara.py "your git question here"

```

## Usage Examples

Gitara translates natural language into git commands. It **prints the command but does not execute it** so you stay in control.

```bash
> python gitara.py "what's in the latest stash, show diff"
git stash show --patch

> python gitara.py "push feature-x to origin, override any changes there and track it"
git push origin feature-x --force --set-upstream

> python gitara.py "show staged changes with diffs"
git status --verbose

> python gitara.py "undo last commit but keep the changes"
git reset --soft HEAD~1

> python gitara.py "show 8 commits for current branch with graph"
git log -n 8 --graph

> python gitara.py "merge vendor branch preferring ours"
git merge vendor --strategy ours

```

### Supported Commands

Gitara covers the commands that make up 95% of daily git usage:

`status` · `add` · `commit` · `push` · `pull` · `branch` · `switch` · `restore` · `merge` · `stash` · `rebase` · `reset` · `log`

Each command supports a reasonable subset of common options. Note: we use `switch` and `restore` instead of `checkout` - they're the [modern, clearer alternatives](https://github.blog/open-source/git/highlights-from-git-2-23/).

## How We Trained Gitara

This section walks through the full training journey: from problem definition, through validating that base models fail, to distilling a small model that matches a 70B teacher.

### The Problem

If you still remember learning `git`, chances are it's not all happy recollections. Remembering the correct commands and options to achieve a given task takes time and trips to Stack Overflow.

We wanted to build a local assistant that could translate plain English into correct git commands. The key requirements:

- **Runs locally:** no API calls, works offline, keeps your workflow private
- **Fast:** responds in under 2 seconds on a laptop
- **Accurate:** matches the quality of much larger cloud models
- **Uses tool-calling:** outputs structured JSON that maps cleanly to git commands

This is exactly the kind of narrow, well-defined task where small language models can shine, if properly trained.

### Validating the Base Model Fails

Before investing in training, we needed to confirm that off-the-shelf small models can't already do this. We tested [Llama 3.2 3B Instruct](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct) on our test set of 50 git queries.

The base model achieved **0.12 accuracy -** essentially random guessing. Common failure modes:

- Outputting malformed JSON
- Hallucinating non-existent git options or choosing the wrong command entirely
- Missing required parameters

This confirmed the task is learnable but not already learned. A perfect candidate for fine-tuning.

### Establishing a Teacher Baseline

Next, we needed a ceiling - how well can a large model do? We tested [GPTOSS-120B](https://huggingface.co/openai/gpt-oss-120b) with a system prompt explaining the tool-calling format and a few examples.

The 120B model achieved **0.92 accuracy** on the same test set. This became our target: could we get a 3B model to match this performance?

### Defining the Tool Schema

We use the OpenAI function calling format to specify each git command as a tool. Here's an example for `git add`:

```json
{
  "type": "function",
  "function": {
    "name": "git_add",
    "description": "Stage files for commit",
    "parameters": {
      "type": "object",
      "properties": {
        "files": {
          "type": "array",
          "description": "List of file paths to stage (use ['.'] for all files)",
          "items": { "type": "string" },
          "minItems": 1
        }
      },
      "required": ["files"]
    }
  }
}

```

The model outputs structured JSON like:

```json
{"name": "git_add", "parameters": {"files": ["README.md"]}}

```

We also include a `do_nothing` tool so the model can gracefully handle off-topic requests ("make me a sandwich") rather than hallucinating arbitrary git commands.

The full schema for all 13 commands is available in `finetuning/data/job_description.json`

### Creating Seed Data

Fine-tuning requires training examples, but we don't need thousands of hand-written ones. We started with ~100 seed examples covering the range of supported commands and realistic query phrasings:

| Input | Output |
| --- | --- |
| apply stash@{5} | `{"name": "git_stash", "parameters": {"action": "apply", "stash_ref": "stash@{5}"}}` |
| merge vendor branch preferring ours | `{"name": "git_merge", "parameters": {"branch": "vendor", "strategy": "ours"}}` |
| show 8 commits for current branch with graph | `{"name": "git_log", "parameters": {"limit": 8, "graph": true}}` |

Writing 100 examples by hand would be tedious. Instead, we generated candidates using a large model, then validated and filtered them manually. This hybrid approach gives you coverage without the grind.

The seed data is available in available in `finetuning/data/{train, test}.jsonl`

### Generating Synthetic Training Data

100 examples isn't enough to fine-tune reliably. We used our platform's data synthesis pipeline to expand the seed data into **10,000 training examples**.

The synthesis process:

1. Takes seed examples as style and format guides
2. Picks a single command to generate input/output pairs
3. Validates outputs against the schema
4. Filters for quality and deduplicates

This gives us broad coverage of query variations while maintaining consistent output format.

### Training the Student Model

With 10k examples ready, we fine-tuned [Llama 3.1 3B Instruct](distil-labs/Distil-gitara-v2-Llama-3.2-1B-Instruct) using standard supervised fine-tuning.

Training configuration:

- **Base model:** Llama 3.1 3B Instruct
- **Training examples:** 10,000
- **Method:** LoRA fine tuning

The training config is available in `finetuning/synthetic-data/{train, test}.jsonl`

### Evaluation

We evaluate by parsing both ground-truth and model outputs into Python dicts, normalizing to remove default-value arguments, and comparing for structural equality. This catches real errors while ignoring irrelevant differences like whitespace or key ordering.

Results on 50 held-out test examples:

| Model | Parameters | Accuracy |
| --- | --- | --- |
| GPT-OSS 120B (teacher) | 120B | 0.92 +/- 0.02 |
| **Llama 3.2 3B Instruct (tuned)** | **3B** | **0.92 +/- 0.01** |
| **Llama 3.2 1B Instruct (tuned)** | **1B** | **0.90 +/- 0.01** |
| Llama 3.2 3B Instruct (base) | 3B | 0.12 +/- 0.05 |
| Llama 3.2 1B Instruct (base) | 1B | 0.0 +/- 0.01 |

The tuned 3B model matches the 120B teacher exactly, with 40x fewer parameters. On an M4 MacBook Pro, most queries return in under 2 seconds.

We also trained a 1B variant that achieves 0.90 accuracy—slightly lower but even more resource-efficient for constrained environments.

---

## Train Your Own Model

The workflow we used for Gitara is generic across tool-calling tasks. Here's how to apply it to your own domain:

### 1. Define your tools

Create JSON schemas for each tool/function your model should call. Be specific about parameter types and descriptions.

### 2. Create seed examples

Write 50-100 examples covering your tool set. You can use a large model to generate candidates, tor do it directly on the [distillabs.ai](http://distillabs.ai) platform.

### 4. Fine-tune

Train a small model (1B-3B parameters work well for narrow tasks) on your synthetic dataset on the [distillabs.ai](http://distillabs.ai) platform.

### 5. Evaluate

Test on held-out examples. Compare against a large model baseline to know when you've succeeded.

For custom training assistance, visit [distillabs.ai](https://www.distillabs.ai/) or reach out to us directly.

## FAQ

**Q: Why not just use GPT-4 / Claude for this?**

Because your git workflow shouldn't depend on internet connectivity or API rate limits. Gitara runs locally, works offline, and keeps your commands private.

**Q: Why not use Llama 3.2 3B directly?**

The base model only achieves 0.12 accuracy on this task - it can't reliably produce valid tool calls. Fine-tuning is essential.

**Q: Can Gitara execute the commands it generates?**

No, by design. Gitara only prints commands for you to review and run yourself. We believe in keeping humans in the loop for operations that modify your repository.

**Q: The model gives an incorrect command**

The model achieves 0.94 accuracy, which means ~1 in 20 queries may be wrong. Always review the output before running. If you find consistent errors, please open an issue.

**Q: Can you train a model for my company's CLI tools?**

Yes! Visit [distillabs.ai](https://www.distillabs.ai/) to discuss custom solutions.

---

## Links

- [Distil Labs Blog Post](https://www.distillabs.ai/blog/gitara)
- [Distil Labs Website](https://www.distillabs.ai/)
- [Join our Slack community](https://join.slack.com/t/distil-labs-community/shared_invite/zt-36zqj87le-i3quWUn2bjErRq22xoE58g)
- [Follow us on LinkedIn](https://www.linkedin.com/company/distil-labs/)