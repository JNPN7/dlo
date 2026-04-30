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
    manifest = ctx.obj.get("cached_manifest")

    runtime = Runtime(project=project, profile=profile, manifest=manifest)
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
    manifest = ctx.obj.get("cached_manifest")

    runtime = Runtime(project=project, profile=profile, manifest=manifest)
    runtime.schedule()


@cli.command("query")
@click.pass_context
@d.project
@d.profile
@d.lifespan
@d.cached_manifest
@click.argument("query")
def execute_query(ctx: click.Context, *args, **kwargs):
    """Run query."""
    click.echo("Running the query")
    project = ctx.obj.get("project")
    profile = ctx.obj.get("profile")
    manifest = ctx.obj.get("cached_manifest")

    query = kwargs.get("query")

    runtime = Runtime(project=project, profile=profile, manifest=manifest)

    # Compile if not cached
    if manifest is None:
        runtime.compile()

    result = runtime.execute_query(query)
    click.echo(result)


@cli.command("mcp")
@click.pass_context
@d.project
@d.profile
@d.lifespan
@d.cached_manifest
@d.server
def mcp(ctx: click.Context, *args, **kwargs):
    """Starting MCP server."""
    click.echo("Starting MCP server...")
    project = ctx.obj.get("project")
    profile = ctx.obj.get("profile")
    manifest = ctx.obj.get("cached_manifest")

    runtime = Runtime(project=project, profile=profile, manifest=manifest)
    runtime.compile()

    import uvicorn

    from dlo.mcp.server import mcp

    host = ctx.obj.get("host")
    port = ctx.obj.get("port")
    reload = ctx.obj.get("reload")
    workers = ctx.obj.get("workers")

    uvicorn.run(
        mcp,
        host=host,
        port=port,
        reload=reload,
        workers=workers,
    )


@cli.command("serve")
@click.pass_context
@d.project
@d.lifespan
@d.server
@click.option(
    "--dev", "-d", is_flag=True, help="Development mode (enables CORS for frontend dev server)"
)
def serve(ctx: click.Context, *args, **kwargs):
    """Start the DLO UI server.

    Serves the manifest data through a REST API and the React UI.

    In development mode (--dev), CORS is enabled for the frontend dev server.
    In production mode, the API serves the built React static files.
    """
    import uvicorn

    dev_mode = kwargs.get("dev", False)

    project = ctx.obj.get("project")
    log_level = ctx.obj.get("log_level", "error")
    log_file = ctx.obj.get("log_file")
    host = ctx.obj.get("host")
    port = ctx.obj.get("port")
    reload = ctx.obj.get("reload")
    workers = ctx.obj.get("workers")

    # TODO: Next JS will not work as React and runtime cannot be attach to Fastapi
    # For prod mode make necessary changes
    if dev_mode:
        click.echo("Starting DLO UI server in development mode...")
        click.echo(f"  API Server: http://{host}:{port}")
        click.echo(f"  API Docs:   http://{host}:{port}/api/docs")
        click.echo("")
        click.echo("Run 'npm run dev' in src/dlo/ui/ to start the Next.js dev server.")
        click.echo("The Next.js app will proxy API requests to this server.")
    else:
        click.echo("Starting DLO UI server...")
        click.echo(f"  UI:       http://{host}:{port}")
        click.echo(f"  API Docs: http://{host}:{port}/api/docs")

    # Create app with appropriate mode
    from dlo.api import RegisterApp

    app = RegisterApp(
        project=project,
        log_level=log_level,
        log_file=log_file,
        dev_mode=dev_mode,
    )

    uvicorn.run(
        app.app,
        host=host,
        port=port,
        reload=reload,
        workers=workers,
    )


@cli.group("search")
def search():
    """
    An Search tool for your semantic layer containing vector search
    """


@search.command("init")
@click.pass_context
@d.project
@d.profile
@d.lifespan
@d.cached_manifest
def search_init(ctx: click.Context, *args, **kwargs):
    """Initializing vector store."""
    click.echo("Initializing vector store...")

    project = ctx.obj.get("project")
    profile = ctx.obj.get("profile")
    manifest = ctx.obj.get("cached_manifest")

    runtime = Runtime(project=project, profile=profile, manifest=manifest)
    runtime.vector_search_init()


@search.command("run")
@click.pass_context
@d.project
@d.profile
@d.lifespan
@d.cached_manifest
@click.argument("query")
def search_run(ctx: click.Context, *args, **kwargs):
    """Run vector search."""
    click.echo("Running vector search...")

    project = ctx.obj.get("project")
    profile = ctx.obj.get("profile")
    manifest = ctx.obj.get("cached_manifest")

    query = kwargs.get("query")

    runtime = Runtime(project=project, profile=profile, manifest=manifest)
    result = runtime.vector_search_run(query=query)

    click.echo(result)


if __name__ == "__main__":
    cli()
