import typer
import pyflowdroid


app = typer.Typer()


@app.command()
def install():
    pyflowdroid.install_deps()

@app.command()
def analyze(path: str):
    total, leaks, leaky_apps = pyflowdroid.analyze(path)
    typer.echo(pyflowdroid.generate_report(total, leaks, leaky_apps))

@app.command()
def download(amount:int, path: str, provider: str):
    pyflowdroid.fetch(amount, provider, path)
    typer.echo(f"Downloaded {amount} apks from {provider}")
    
app()