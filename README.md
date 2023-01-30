# PyFlowDroid

Python wrappers for [FlowDroid](https://github.com/secure-software-engineering/FlowDroid) 
Apk analyzer. This project was built with two goals in mind:

1. Automate the creation of a FlowDroid environment out-of-the-box
2. Allow the usage of FlowDroid from Python code 

## 1. Installation

### 1.1 Prerequisites 

Make sure you have a working version of [java](https://www.java.com/en/download/help/download_options.html), [python](https://www.python.org/downloads/) and [git](https://git-scm.com/downloads) in the PATH of your environment.

### 1.2 Installing pyFlowDroid

You can get it from pypi using [pip](https://pip.pypa.io/en/stable/installation/):

```bash
$ pip install pyflowdroid
```

You will need to run an additional command to make pyflowdroid download and 
install FlowDroid and other required resources:

```bash
$ python -m pyflowdroid install
```

## 2. Using pyflowdroid as a Python library

You can use this script as a guide for downloading and analyzing apk files
with pyflowdroid:

```python
import pyflowdroid

# Path to a folder where the apks are stored
apkfolder = "./apks"

# If you need test apks, you can download the desired amount
# from a given provider into a destination folder
pyflowdroid.fetch(10, 'cubapk.com', apkfolder)

# Analyze all the apks in a folder
apk_count, leaks_count, leaky_apps = pyflowdroid.analyze(apkfolder)

# Analyze a single apk
flowdroid_logs = pyflowdroid.analyze_apk('./apks/test.apk')
```

## 3. Using pyflowdroid as a command line tool

The main advantage of using pyflowdroid as a command line tool, over using
FlowDroid directly, are the resources automatically bundled into it to 
speed up the flow analysis. pyflowdroid includes all the required 
resources to allow a quick analysis of apk files.

### Analyzing a single .apk file with the default pyflowdroid setup

```bash
$ python -m pyflowdroid analyze path/to/file.apk
```

### Analyzing all the apks inside a folder:

```bash
$ python -m pyflowdroid analyze path/to/folder/
```

This should store raw FlowDroid logs for each analyzed apk and then show a 
general report like this:

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

### Fetching test apks from a provider:

```bash
$ python -m pyflowdroid download amount path/to/store/apks/ provider_name
```

Current available providers are:

- [cubapk.com](https://cubapk.com/)

To fetch apks from a provider, just run:

For instance, to download 10 apk files from cubapk.com, run:

```bash
$ python -m pyflowdroid download 10 ./myapks/ cubapk.com
```


## 4. Contributing to pyflowdroid

If you want to add any features to pyflowdroid you will need to get a 
development enviroment.

### 4.1 Fetching the project source code

You can clone the github repository by executing:

```bash
$ git clone https://github.com/gvieralopez/pyFlowDroid
$ cd pyFlowDroid
```

### 4.2 Installing pyFlowDroid dependencies

You can install them with [poetry](https://python-poetry.org/docs/#installation)
 by executing:

```bash
$ poetry shell
$ poetry install
$ poetry build
```
### 4.3 Download FlowDroid and its dependencies

This step will download and install FlowDroid. After doing this you can use 
FlowDroid with or without pyFlowDroid wrappers.
Simply run:

```bash
$ python -m pyflowdroid install
```

### 4.4 Making your changes appear in the project

Just make a Pull Request.

### 4.5 Quality Assurance:

#### Run tests:

```bash
$ pytest
```

#### Type checking:

```bash
$ mypy
```

#### Code style:

```bash
$ flake8
```

### 4.6 Pending features

- Improve cli interface with hints on the parameters
- Improve cli interface with parameters all supported API functions
- Recognize in runtime when Flowdroid and depencies were not installed
- Add new apk providers
- Write pytest unit tests
- Write documentation
