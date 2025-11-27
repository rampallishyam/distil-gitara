import json
import sys

import click

from gitara.model_client import DistilLabsLLM
from gitara.renderer import render_git_command

MODEL = "hf.co/distil-labs/Llama-3_2-gitara-3B"
PORT = 11434


def parse_tool_call(response: str) -> dict | None:
    try:
        tool_call = json.loads(response)
        if not isinstance(tool_call, dict):
            return None

        if "name" not in tool_call:
            return None

        if "arguments" in tool_call and isinstance(tool_call["arguments"], str):
            try:
                tool_call["arguments"] = json.loads(tool_call["arguments"])
            except json.JSONDecodeError:
                pass
        return tool_call

    except json.JSONDecodeError:
        return None


@click.command()
@click.argument("query", type=str)
@click.option("--show-json", is_flag=True, help="Also show tool call JSON")
def main(query, show_json):
    """Git Assistant - Convert natural language to git commands"""
    try:
        client = DistilLabsLLM(model_name=MODEL, port=PORT)
        tool_call = client.invoke(query)

        if tool_call:
            if show_json:
                click.secho(f"# Tool call: {tool_call}", fg="cyan", err=True)
            click.echo(render_git_command(tool_call))
            return
        click.secho(f"Error: Could not parse tool call from '{tool_call}'", fg="red", err=True)
        sys.exit(1)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
