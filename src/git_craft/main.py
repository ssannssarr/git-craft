import click
from rich.console import Console

from git_craft.git import Git
from git_craft.llm import LLM

console = Console()

@click.group()
def cli():
    """Run Git Craft commands."""


@cli.command("commit-msg")
@click.option("--debug", is_flag=True, help="Print model request settings, including the API key.")
def commit_msg(debug: bool):
    """Generate a commit message from the current changes."""
    git = Git()
    try:
        diff = git.get_diff()
        if not diff:
            raise click.ClickException("No staged or unstaged changes found.")
        log = git.get_log()
        llm = LLM()
        prompt = "Write one concise git commit message. Return only the message, with no quotes or markdown."
        context = f"Git diff:\n{diff}\n\nRecent commit subjects:\n{log}"
        with console.status("[cyan]Generating commit message…", spinner="dots"):
            message = llm.generate(prompt, context=context, debug=debug)
    except (RuntimeError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(message)


def main():
    """Run the command line interface."""
    cli()


if __name__ == "__main__":
    main()
