from pathlib import Path

import typer

import pyflowdroid
from pyflowdroid import apk_sources

app = typer.Typer()


@app.command()
def install():
    pyflowdroid.install_deps()


@app.command()
def analyze(path: str):
    total, leaks, leaky_apps = pyflowdroid.analyze(path)
    typer.echo(pyflowdroid.generate_report(total, leaks, leaky_apps))


@app.command()
def download(amount: int, path: str, provider: str):
    apk_sources.download(provider, amount, Path(path))
    typer.echo(f"Downloaded {amount} apks from {provider}")


if __name__ == "__main__":
    app()
