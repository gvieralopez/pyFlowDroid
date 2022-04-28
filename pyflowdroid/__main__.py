import typer


app = typer.Typer()


@app.command()
def install():
    from pyflowdroid.install import install_all
    install_all()

@app.command()
def analyze(path: str):
    from pyflowdroid.analyze import analyze    
    typer.echo(analyze(path))

@app.command()
def download(amount:int, path: str, provider: str):
    from pyflowdroid.download import get_provider
    prv = get_provider(provider)
    prv.download_apks(amount, path)
    typer.echo(f"Downloaded {amount} apks from {provider}")
    
app()