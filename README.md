# PyFlowDroid

Python wrappers for FlowDroid Apk analyzer. This project was built with two 
goals in mind:

1. Automate the creation of a FlowDroid environment out-of-the-box
2. Allow the usage of FlowDroid from Python code 

## Installation

### Prerequisites 

Make sure you have:

1. A working version of [java](https://www.java.com/en/download/help/download_options.html) 
   in the PATH of your environment.
2. A working version of [python](https://www.python.org/downloads/) in the PATH 
   of your environment.
3. A working version of [git](https://git-scm.com/downloads) in the PATH of your 
   environment.

### Installing pyFlowDroid dependencies

You can install it with [pip](https://pip.pypa.io/en/stable/installation/) by:

```
$ pip install pyflowdroid
```
### Download FlowDroid and its dependencies

This step will download and install FlowDroid and the required resources to use
it:

```
$ python -m pyflowdroid install
```

## Usage

There are two ways in which you can use pyflowdroid: As a command line tool
or as a Python library.

### Using pyflowdroid from the command line

The main advantage of using pyflowdroid as a command line tool over using
FlowDroid directly is the automatic gathering of resources required to 
execute the flow analysis. pyflowdroid comes bundled with all the required 
resources to allow a quick analysis of apk files.

To analyze an .apk file with the default pyflowdroid setup, just run:

```
$ python -m pyflowdroid analyze path/to/file.apk
```

Similarly, you can perform a flow analysis on all the apks inside a folder:

```
$ python -m pyflowdroid analyze path/to/folder/
```

This should store raw FlowDroid logs for each analyzed apk and then show a 
general report like the following:

```
################################################################################
#                              PYFLOWDROID REPORT                              #
################################################################################
Analized: 5
Leaks found: 2

Leaky apps:
 - 'path/to/folder/app1.apk'
 - 'path/to/folder/app3.apk'
```

If you want to get some test apks, pyflowdroid includes a download function
to fetch apks from a given provider. Current available providers are:

- [cubapk.com](https://cubapk.com/)

To fetch apks from a provider, just run:

```
$ python -m pyflowdroid download amount path/to/store/apks/ provider_name
```

For instance, to download 10 apk files from cubapk.com, run:

```
$ python -m pyflowdroid download 10 ./myapks/ cubapk.com
```

### Using pyflowdroid as a Python library

[Comming Soon]

## Contributing to pyflowdroid

If you want to add any features to pyflowdroid you will need to get a 
development enviroment.

### Fetching the project source code

You can clone the github repository by executing:

```
$ git clone https://github.com/gvieralopez/pyFlowDroid
$ cd pyFlowDroid
```

### Installing pyFlowDroid dependencies

You can install them with [poetry](https://python-poetry.org/docs/#installation)
 by executing:

```
$ poetry shell
$ poetry install
$ poetry build
```
### Download FlowDroid and its dependencies

This step will download and install FlowDroid. After doing this you can use 
FlowDroid with or without pyFlowDroid wrappers.
Simply run:

```
$ python -m pyflowdroid install
```

### Making your changes appear in the project

Just make a Pull Request.

### Run tests:

```
$ pytest
```

### Type checking:

```
$ mypy
```

### Code style:

```
$ flake8
```