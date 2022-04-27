import typer


app = typer.Typer()


@app.command()
def install():
    from pyflowdroid.install import install_all
    install_all()

@app.command()
def analyze(path: str):
    from pyflowdroid.analyze import analyze_apk    
    typer.echo(analyze_apk(path))

app()