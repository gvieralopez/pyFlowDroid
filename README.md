# PyFlowDroid

Python wrappers for FlowDroid Apk analyzer. This project was built with two goals in mind:

1. Automate the creation of a FlowDroid environment out-of-the-box
2. Allow the usage of FlowDroid from Python code 

## Installation

### Prerequisites 

Make sure you have:

1. A working version of [java](https://www.java.com/en/download/help/download_options.html) in the PATH of your environment.
2. A working version of [python](https://www.python.org/downloads/) in the PATH of your environment.
3. A working version of [git](https://git-scm.com/downloads) in the PATH of your environment.

### Fetching the project source code

You can clone the github repository by executing:

```
git clone https://github.com/gvieralopez/pyFlowDroid
cd pyFlowDroid
```

### Installing pyFlowDroid dependencies

You can install all of them with [pip](https://pip.pypa.io/en/stable/installation/) by:

```
pip install -r requirements.txt
```
### Download FlowDroid and its dependencies

This step will download and install FlowDroid. After doing this you can use FlowDroid with or without pyFlowDroid wrappers.
Simply run:

```
python -m pyflowdroid install
```

## Usage

1. Copy the *.apk* file you want to analyze in the folder called 'apk' created after installing
2. Run *analyze.py* in order to perform a Flow analysis over all the *.apk* files in the 'apk' directory.
3. You can inspect raw FlowDroid output for each *.apk* file in the 'log' directory and get a brief summary of the overall results in the terminal output.

## Extra Tools

The script *download_apk.py* is an *.apk* downloader that stores a local copy of all the applications of the website [Cubapk](https://cubapk.com/). It can be further extended to download files from other websites.

In order to use it, you should install BeautifulSoup 
```
pip3 install beautifulsoup4
```

