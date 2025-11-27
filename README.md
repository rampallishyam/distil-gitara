# gitara: an SLM converting your requests to git commands

![gitara](gitara.png)

This project demonstrates how to use a fine-tuned Small Language Model to convert natural language into git commands.

It is a wrapper around our fine-tuned Small Language Model [available on 🤗 Hugging Face](https://hf.co/distil-labs/Llama-3_2-gitara-3B). It's based on [Llama 3.2 3B](https://huggingface.co/meta-llama/Llama-3.2-3B) and fine-tuned using the [distil labs](https://www.distillabs.ai/) platform to generate git commands as tool calls. Check out [our blog](https://www.distillabs.ai/blog) for more details.


**It will not execute any git commands!** Instead, it will just print them out for you:

```bash
> gitara "how do I stage README.md for commit"
git add README.md
```

## Installation

1. First, make sure you have prerequisites installed:
  - Ollama [https://ollama.com/download](https://ollama.com/download)
  - `uv` [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
2. Pull [the fine-tuned model](https://huggingface.co/distil-labs/Llama-3_2-gitara-3B) from 🤗 Hugging Face:
   ```bash
   ollama pull hf.co/distil-labs/Llama-3_2-gitara-3B
   ```
3. Check out this project
   ```bash
   git clone git@github.com:distil-labs/gitara.git
   cd gitara
   ```
4. Finally, run:
   ```bash
   > uv run gitara "create and check out a new branch feat-1"
   git switch -c feat-1
   ```

  You can also add `--show-json` flag to see the JSON output of the model's prediction:

  ```bash
  > uv run gitara "create and check out a new branch feat-1" --show-json
  # Tool call: {'name': 'git_switch', 'arguments': {'branch': 'feat-1', 'create': True}}
  git switch -c feat-1
  ```

## Queries to try

```bash
> uv run gitara "pull latest changes from main while rebasing"
git pull origin main --rebase

> uv run gitara "push to remote named fork on branch test-fixes"
git push fork test-fixes

> uv run gitara "I forgot to write a good commit message, can I update the last message?"
git commit --amend

> uv run gitara "abort the current rebase"
git rebase --abort

> uv run gitara "restore settings.json to what it was in HEAD"
git restore --source=HEAD settings.jso

> uv run gitara "go back to main branch"
git switch main

> uv run gitara "create and check out a new feat/1 branch"
git switch -c feat/1
```
