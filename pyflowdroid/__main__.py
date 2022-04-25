import typer

app = typer.Typer()


@app.command()
def install():
    from pyflowdroid.install import install_all
    install_all()

@app.command()
def analyze():
    typer.echo("Analyzing")

app()