import click

from dlo.core.cli.decorators import project
from dlo.core.parser.manifest import ManifestLoader


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
    no_args_is_help=True,
    epilog="Specify one of these sub-commands and you can find more help from there.",
)
@click.pass_context
def cli(ctx, **kwargs):
    """
    An ELT tool for managing your SQL transformations and data models with AI.
    """


@cli.command("version")
def version():
    """Show the version of DLO."""
    from dlo import __version__
    click.echo(f"DLO version: {__version__.version}")


@cli.command("run")
@click.pass_context
@project
def run(ctx: click.Context, *args, **kwargs):
    """Run the DLO pipeline."""
    click.echo("Running DLO pipeline...")
    project = ctx.obj.get("project")
    manifest = ManifestLoader(project).load()
    print(manifest)


if __name__ == "__main__":
    cli()