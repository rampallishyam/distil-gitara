import argparse
import logging
import json

from openai import OpenAI, ChatCompletion


DEFAULT_QUESTION = "First time pushing this new branch to establish tracking with upstream."

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Check the current status of the repository (modified files, staged changes, branch info)",
            "parameters": {
                "type": "object",
                "properties": {
                    "verbose": {
                        "type": "boolean",
                        "description": "Show detailed status including diffs",
                        "default": False,
                    },
                    "ignored": {
                        "type": "boolean",
                        "description": "Show ignored files",
                        "default": False,
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
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
                        "items": {"type": "string"},
                        "minItems": 1,
                    }
                },
                "required": ["files"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Create a commit with staged changes",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Commit message describing the changes (required unless amend=true)",
                        "minLength": 1,
                    },
                    "amend": {
                        "type": "boolean",
                        "description": "Amend the previous commit instead of creating new one",
                        "default": False,
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_push",
            "description": "Push commits to remote repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "remote": {
                        "type": "string",
                        "description": "Remote name",
                        "default": "origin",
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name (current branch if not specified)",
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force push (use with caution)",
                        "default": False,
                    },
                    "set_upstream": {
                        "type": "boolean",
                        "description": "Set upstream tracking for the branch",
                        "default": False,
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_pull",
            "description": "Pull changes from remote repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "remote": {
                        "type": "string",
                        "description": "Remote name",
                        "default": "origin",
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name (current branch if not specified)",
                    },
                    "rebase": {
                        "type": "boolean",
                        "description": "Rebase instead of merge",
                        "default": False,
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_branch",
            "description": "List, or delete branches (use `git_switch` for branch creation)",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["delete", "list"],
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Name of the branch (required for delete)",
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force delete even if not merged (only for delete action)",
                        "default": False,
                    },
                    "all": {
                        "type": "boolean",
                        "description": "Show all branches including remotes (only for list action)",
                        "default": False,
                    },
                },
                "required": ["action"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_switch",
            "description": "Switch to a different branch",
            "parameters": {
                "type": "object",
                "properties": {
                    "branch": {
                        "type": "string",
                        "description": "Branch name to switch to (not needed if detach is true)",
                    },
                    "create": {
                        "type": "boolean",
                        "description": "Create new branch before switching",
                        "default": False,
                    },
                    "detach": {
                        "type": "boolean",
                        "description": "Switch to a commit in detached HEAD state",
                        "default": False,
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_restore",
            "description": "Restore files in working tree and/or staging area",
            "parameters": {
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "description": "List of file paths to restore",
                        "items": {"type": "string"},
                        "minItems": 1,
                    },
                    "source": {
                        "type": "string",
                        "description": "Restore source (e.g., HEAD, commit hash)",
                        "default": "HEAD",
                    },
                    "restore_target": {
                        "type": "string",
                        "enum": ["worktree", "staged", "both"],
                        "default": "worktree",
                    },
                },
                "required": ["files"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_merge",
            "description": "Merge branches together",
            "parameters": {
                "type": "object",
                "properties": {
                    "branch": {
                        "type": "string",
                        "description": "Branch to merge into current branch",
                    },
                    "no_ff": {
                        "type": "boolean",
                        "description": "Always create a merge commit, even if fast-forward is possible",
                        "default": False,
                    },
                    "ff_only": {
                        "type": "boolean",
                        "description": "Only allow fast-forward merges (fail if not possible)",
                        "default": False,
                    },
                    "strategy": {
                        "type": "string",
                        "description": "Merge strategy to use",
                        "enum": ["recursive", "resolve", "ours", "subtree"],
                        "default": "recursive",
                    },
                },
                "required": ["branch"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_stash",
            "description": "Temporarily save uncommitted changes",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Stash operation",
                        "enum": [
                            "save",
                            "pop",
                            "apply",
                            "list",
                            "drop",
                            "clear",
                            "show",
                        ],
                    },
                    "message": {
                        "type": "string",
                        "description": "Message for stash save (only for save action)",
                    },
                    "stash_ref": {
                        "type": "string",
                        "description": "Stash reference (e.g., 'stash@{0}', 'stash@{2}') for pop/apply/drop/show actions",
                        "default": "stash@{0}",
                    },
                    "include_untracked": {
                        "type": "boolean",
                        "description": "Include untracked files in stash (only for save action)",
                        "default": False,
                    },
                    "patch": {
                        "type": "boolean",
                        "description": "Show full patch/diff when using action=show",
                        "default": False,
                    },
                },
                "required": ["action"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_rebase",
            "description": "Reapply commits on top of another base",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target branch or commit to rebase onto (required unless continue or abort are true)",
                    },
                    "continue": {
                        "type": "boolean",
                        "description": "Continue after resolving conflicts",
                        "default": False,
                    },
                    "abort": {
                        "type": "boolean",
                        "description": "Abort the rebase operation",
                        "default": False,
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_reset",
            "description": "Reset current HEAD to specified state",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Reset mode",
                        "enum": ["soft", "mixed", "hard"],
                    },
                    "target": {
                        "type": "string",
                        "description": "Commit hash or reference (e.g., HEAD~1)",
                        "default": "HEAD",
                    },
                },
                "required": ["mode"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_log",
            "description": "View commit history",
            "parameters": {
                "type": "object",
                "properties": {
                    "ref": {
                        "type": "string",
                        "description": "Branch, tag, or commit to show history for (default: current branch)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of commits to show",
                        "default": 10,
                        "minimum": 1,
                    },
                    "oneline": {
                        "type": "boolean",
                        "description": "Condensed one-line format",
                        "default": False,
                    },
                    "graph": {
                        "type": "boolean",
                        "description": "Show branch graph",
                        "default": False,
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
]


class DistilLabsLLM:
    def __init__(self, model_name: str, port: int = 11434) -> None:
        self.model_name = model_name
        self.client = OpenAI(base_url=f"http://127.0.0.1:{port}/v1", api_key="EMPTY")

    def get_prompt(
        self,
        question: str,
    ) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": """
You are a tool-calling model working on the task in the 'task_description' XML block:

<task_description>Respond with the next git operation tool call based on the desired action</task_description>

You will be given a single task in the 'question' XML block.
Solve the task in 'question' block by generating an appropriate tool call according to the provided tool schema.
Generate only the answer, do not generate anything else.


Rules for generating the answers:
- It should be a JSON object with exactly two keys: "name" and "parameters".
- Do not include any other keys.
- Do not add anything, except valid JSON.
- Do not include trailing commas.
- Do not add anything before/after the tool call.
- Stick to the format of the following examples:

{"name": "refresh_page", "parameters": {}}
{"name": "get_weather", "parameters": {"location": "Paris, France"}}
""",
            },
            {
                "role": "user",
                "content": f"""Here are examples that show how this task can be solved
In examples, contexts are in the context XML block, tasks in the question XML block, solutions in the answer XML block
When solving a real task, generate only the answer, do not generate anything else


<example>
<question>apply stash@{{5}}</question>
<answer>{{"name": "git_stash", "parameters": {{"action": "apply", "stash_ref": "stash@{{5}}"}}}}</answer>
</example>


<example>
<question>commit fix: typos</question>
<answer>{{"name": "git_commit", "parameters": {{"message": "fix: typos"}}}}</answer>
</example>
Now for the real task, solve the task in question block.
Generate only the solution, do not generate anything else.

<question>{question}</question>""",
            },
        ]

    def is_valid_response(self, response: ChatCompletion) -> bool:
        tool_calls = response.choices[0].message.tool_calls
        return tool_calls is not None and len(tool_calls) == 1

    def invoke(self, question: str) -> dict:
        messages = self.get_prompt(question)
        chat_response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.0,
            tools=TOOLS,
            tool_choice="required",
        )
        message = chat_response.choices[0].message
        try:
            [tool_call] = message.tool_calls
            tool_call_dict = {
                "name": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments),
            }
            return tool_call_dict
        except Exception as e:
            logging.error(f"Single tool call not found in LM response: {chat_response}")
            raise RuntimeError from e


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", type=str, default=DEFAULT_QUESTION, required=False)
    parser.add_argument("--api-key", type=str, default="EMPTY", required=False)
    parser.add_argument("--model", type=str, default="git_tc", required=False)
    parser.add_argument("--port", type=int, default=11434, required=False)
    args = parser.parse_args()

    client = DistilLabsLLM(model_name=args.model, port=args.port)

    print(client.invoke(args.question))
