import click

import dlo.core.cli.decorators as d

from dlo.core.compiler.runtime import Runtime


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


@cli.command("compile")
@click.pass_context
@d.project
@d.profile
@d.lifespan
def compile(ctx: click.Context, *args, **kwargs):
    """Compile the DLO pipeline."""
    click.echo("Compiling DLO pipeline...")
    project = ctx.obj.get("project")
    profile = ctx.obj.get("profile")

    runtime = Runtime(project=project, profile=profile)
    runtime.compile()


@cli.command("run")
@click.pass_context
@d.project
@d.profile
@d.lifespan
@d.cached_manifest
def run(ctx: click.Context, *args, **kwargs):
    """Run the DLO pipeline."""
    click.echo("Running DLO pipeline...")
    project = ctx.obj.get("project")
    profile = ctx.obj.get("profile")

    # TODO: Use in very near future added to remember
    _ = ctx.obj.get("cached_manifest")

    runtime = Runtime(project=project, profile=profile)
    runtime.run()


@cli.command("schedule")
@click.pass_context
@d.project
@d.profile
@d.lifespan
@d.cached_manifest
def schedule(ctx: click.Context, *args, **kwargs):
    """Schedule the DLO pipeline."""
    click.echo("Scheduling DLO pipeline...")
    project = ctx.obj.get("project")
    profile = ctx.obj.get("profile")

    # TODO: Use in very near future added to remember
    _ = ctx.obj.get("cached_manifest")

    runtime = Runtime(project=project, profile=profile)
    runtime.schedule()


if __name__ == "__main__":
    cli()
