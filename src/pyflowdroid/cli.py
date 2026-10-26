import json
import logging
import re
from collections.abc import Callable
from dataclasses import asdict
from functools import partial
from pathlib import Path
from typing import Annotated, Any, TypeVar

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import BarColumn, DownloadColumn, Progress, TaskID, TextColumn
from rich.table import Table

import pyflowdroid
from pyflowdroid.analysis import analyze_with, find_apks
from pyflowdroid.apk_sources import download, get_source, source_names
from pyflowdroid.discovery import environment, find_java, home, load_installation
from pyflowdroid.errors import PyFlowDroidError
from pyflowdroid.installer import install_with_progress
from pyflowdroid.models import AnalysisResult, Statement
from pyflowdroid.net import new_client

app = typer.Typer(no_args_is_help=True, help="Run FlowDroid on Android APKs.")
console = Console(soft_wrap=True)
errors = Console(stderr=True, soft_wrap=True)

T = TypeVar("T")

_SIGNATURE = re.compile(r"<(?P<owner>[\w.$]+): [\w.$\[\]]+ (?P<name>[\w$<>]+)\(")


@app.callback(invoke_without_command=True)
def main(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show what happens.")] = False,
    version: Annotated[
        bool, typer.Option("--version", help="Show the version and exit.", is_eager=True)
    ] = False,
) -> None:
    if version:
        console.print(f"pyflowdroid {pyflowdroid.__version__}")
        raise typer.Exit
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(message)s",
        handlers=[RichHandler(console=errors, show_path=False)],
    )


@app.command(
    "install", help="Download FlowDroid, its sources and sinks list and an Android platform."
)
def install_command() -> None:
    with Progress(TextColumn("{task.description}"), BarColumn(), DownloadColumn()) as progress:
        tasks: dict[str, TaskID] = {}

        def report(label: str, done: int, total: int | None) -> None:
            if label not in tasks:
                tasks[label] = progress.add_task(label, total=total)
            progress.update(tasks[label], completed=done)

        installation = _run(lambda: install_with_progress(report))
    console.print(f"FlowDroid {installation.flowdroid_version} is ready in {home()}")


@app.command("analyze", help="Look for leaks in APK files.")
def analyze_command(
    paths: Annotated[list[Path], typer.Argument(help="APK files or folders with APKs.")],
    as_json: Annotated[bool, typer.Option("--json", help="Print the results as JSON.")] = False,
) -> None:
    java = _run(find_java)
    installation = _run(lambda: load_installation(home()))
    apks = _collect_apks(paths)
    results: list[AnalysisResult] = []
    failed = 0
    for apk in apks:
        try:
            results.append(analyze_with(java, installation, apk))
        except PyFlowDroidError as error:
            failed += 1
            errors.print(f"[red]{error}[/red]")
    if as_json:
        console.print_json(json.dumps([_result_json(result) for result in results], indent=2))
    else:
        _print_report(results)
    if failed:
        raise typer.Exit(code=1)


@app.command("download", help="Download sample APKs.")
def download_command(
    folder: Annotated[Path, typer.Argument(help="Where to save the APKs.")],
    source: Annotated[str, typer.Option(help="Where the APKs come from.")] = "droidbench",
    count: Annotated[int, typer.Option(min=1, help="How many APKs.")] = 10,
) -> None:
    paths = _run(lambda: download(source, count, folder))
    console.print(f"{len(paths)} APKs from {source} in {folder}")


@app.command("sources", help="List where sample APKs can come from.")
def sources_command() -> None:
    table = Table("Source", "Description")
    with new_client() as client:
        for name in source_names():
            table.add_row(name, get_source(name, client).description)
    console.print(table)


@app.command("doctor", help="Check that Java and FlowDroid are ready.")
def doctor_command() -> None:
    found = environment()
    console.print(f"Home: {found.home}")
    try:
        java = find_java()
        console.print(f"[green]Java {java.version}[/green] at {java.executable}")
    except PyFlowDroidError as error:
        console.print(f"[red]{error}[/red]")
    try:
        installation = load_installation(found.home)
        console.print(
            f"[green]FlowDroid {installation.flowdroid_version}[/green] with the Android "
            f"{installation.android_platform} platform"
        )
    except PyFlowDroidError as error:
        console.print(f"[red]{error}[/red]")
    if not found.ready:
        raise typer.Exit(code=1)


def _collect_apks(paths: list[Path]) -> list[Path]:
    apks: list[Path] = []
    for path in paths:
        if path.is_dir():
            apks.extend(_run(partial(find_apks, path)))
        else:
            apks.append(path)
    return apks


def _print_report(results: list[AnalysisResult]) -> None:
    table = Table()
    table.add_column("APK", overflow="fold")
    table.add_column("Leaks")
    table.add_column("Seconds")
    for result in results:
        leaks = f"[red]{len(result.leaks)}[/red]" if result.leaky else "0"
        table.add_row(_shown(result.apk), leaks, f"{result.seconds:.1f}")
    console.print(table)
    for result in results:
        for leak in result.leaks:
            console.print(f"[bold]{_shown(result.apk)}[/bold]")
            console.print(f"  from {_describe(leak.source)}")
            console.print(f"  to   {_describe(leak.sink)}")


def _shown(apk: Path) -> str:
    try:
        return str(apk.resolve().relative_to(Path.cwd()))
    except ValueError:
        return str(apk)


def _describe(statement: Statement) -> str:
    called = _short(statement.definition or statement.statement)
    where = _short(statement.method)
    line = f", line {statement.line}" if statement.line is not None else ""
    return f"{called} in {where}{line}"


def _short(signature: str) -> str:
    match = _SIGNATURE.search(signature)
    if match is None:
        return signature
    return f"{match['owner'].rsplit('.', 1)[-1]}.{match['name']}()"


def _result_json(result: AnalysisResult) -> dict[str, Any]:
    data = asdict(result)
    del data["log"]
    data["apk"] = str(result.apk)
    data["seconds"] = round(result.seconds, 3)
    data["leaky"] = result.leaky
    return data


def _run(action: Callable[[], T]) -> T:
    try:
        return action()
    except (PyFlowDroidError, OSError) as error:
        errors.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error
