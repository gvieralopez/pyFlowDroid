# PyFlowDroid

This project allows you to get a ready-to-use environment of FlowDroid out-of-the-box, by running a single installation script. Additionally, it includes a Python wrapper to use FlowDroid APK analyzer in a more pythonic way. 


## Installation

1. You have to install *java* and *python* and add them to the path of your environment.
2. Run *install.py* in order to download Flowdroid and its requirements.

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

