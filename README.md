# PyFlowDroid

Python wrappers for [FlowDroid](https://github.com/secure-software-engineering/FlowDroid) 
Apk analyzer. This project was built with two goals in mind:

1. Automate the creation of a FlowDroid environment out-of-the-box
2. Allow the usage of FlowDroid from Python code 

## 1. Installation

### 1.1 Prerequisites 

Make sure you have:

1. A working version of [java](https://www.java.com/en/download/help/download_options.html) 
   in the PATH of your environment.
2. A working version of [python](https://www.python.org/downloads/) in the PATH 
   of your environment.
3. A working version of [git](https://git-scm.com/downloads) in the PATH of your 
   environment.

### 1.2 Installing pyFlowDroid

You can get it from pypi using [pip](https://pip.pypa.io/en/stable/installation/):

```
$ pip install pyflowdroid
```

Then, you need to run an additional command to make pyflowdroid download and 
install FlowDroid and the required resources to use it:

```
$ python -m pyflowdroid install
```

## 2. Using pyflowdroid as a Python library

You can use this script as a guide for downloading and analyzing apk files
with pyflowdroid:

```python
import pyflowdroid

# Path to a folder where the apks are stored
apkfolder = "./apks"

# If you need test apks, you can dowload the desired amount
# from a given provider into a destination folder
pyflowdroid.fetch(10, 'cubapk.com', apkfolder)

# Analyze all the apks in a folder
apk_count, leaks_count, leaky_apps = pyflowdroid.analyze(apkfolder)

# Analyze a single apk
flowdroid_logs = pyflowdroid.analyze_apk('./apks/test.apk')
```

## 3. Using pyflowdroid as a command line tool

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


## 4. Contributing to pyflowdroid

If you want to add any features to pyflowdroid you will need to get a 
development enviroment.

### 4.1 Fetching the project source code

You can clone the github repository by executing:

```
$ git clone https://github.com/gvieralopez/pyFlowDroid
$ cd pyFlowDroid
```

### 4.2 Installing pyFlowDroid dependencies

You can install them with [poetry](https://python-poetry.org/docs/#installation)
 by executing:

```
$ poetry shell
$ poetry install
$ poetry build
```
### 4.3 Download FlowDroid and its dependencies

This step will download and install FlowDroid. After doing this you can use 
FlowDroid with or without pyFlowDroid wrappers.
Simply run:

```
$ python -m pyflowdroid install
```

### 4.4 Making your changes appear in the project

Just make a Pull Request.

### 4.5 Quality Assurance:

#### Run tests:

```
$ pytest
```

#### Type checking:

```
$ mypy
```

#### Code style:

```
$ flake8
```

### 4.6 Pending features

- Improve cli interface with hints on the parameters
- Improve cli interface with parameters all supported API functions
- Recognize in runtime when Flowdroid and depencies were not installed
- Add new apk providers
- Write pytest unit tests
- Write documentation