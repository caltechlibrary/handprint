# Installation

This page describes how you can install Handprint on your computer. After installation, you will also need to perform some [configuration steps described elsewhere](configuration.md).


## Preliminary requirements

The instructions below assume you have a Python interpreter version 3.8 or higher installed on your computer; if that's not the case, please first install Python and familiarize yourself with running Python programs on your system. If you are unsure of which version of Python you have, you can find out by running the following command in a terminal and inspecting the results:
```sh
# Note: on Windows, you may have to use "python" instead of "python3"
python3 --version
```

Note for Mac users: if you are using macOS Catalina (10.15) or later and have never run `python3`, then the first time you do, macOS will ask you if you want to install the macOS command-line developer tools.  Go ahead and do so, as this is the easiest way to get a recent-enough Python&nbsp;3 on those systems.

Handprint includes several adapters for working with cloud-based HTR services from Amazon, Google, and Microsoft, but does not include credentials for using the services.  To be able to use Handprint, you must **both** install a copy of Handprint on your computer **and** supply your copy with credentials for accessing the cloud services you want to use.  See below for more.


## Installation instructions

There are multiple ways of installing Handprint, ranging from downloading a self-contained, single-file, ready-to-run program, to installing it as a typical Python program using `pip`.  Please choose the alternative that suits you.

### Approach 1: using the standalone Handprint executables

Beginning with version 1.5.1, runnable self-contained single-file executables are available for select operating system and Python version combinations &ndash; to use them, you **only** need a Python&nbsp;3 interpreter and a copy of Handprint, but **do not** need to run `pip install` or other steps. Please click on the relevant heading below to learn more.

<details><summary><img alt="macOS" align="bottom" height="26px" src="https://github.com/caltechlibrary/handprint/raw/main/.graphics/mac-os-32.png">&nbsp;<strong>macOS</strong></summary>

Visit the [Handprint releases page](https://github.com/caltechlibrary/handprint/releases) and look for the ZIP files with names such as (e.g.) `handprint-1.5.4-macos-python3.8.zip`. Then:
1. Download the one matching your version of Python
2. Unzip the file (if your browser did not automatically unzip it for you)
3. Open the folder thus created (it will have a name like `handprint-1.5.4-macos-python3.8`)
4. Look inside for `handprint` and move it to a location where you put other command-line programs (e.g., `/usr/local/bin`)

</details><details><summary><img alt="Linux" align="bottom" height="26px" src="https://github.com/caltechlibrary/handprint/raw/main/.graphics/linux-32.png">&nbsp;<strong>Linux</strong></summary>

Visit the [Handprint releases page](https://github.com/caltechlibrary/handprint/releases) and look for the ZIP files with names such as (e.g.) `handprint-1.5.4-linux-python3.8.zip`. Then:
1. Download the one matching your version of Python
2. Unzip the file (if your browser did not automatically unzip it for you)
3. Open the folder thus created (it will have a name like `handprint-1.5.4-linux-python3.8`)
4. Look inside for `handprint` and move it to a location where you put other command-line programs (e.g., `/usr/local/bin`)

</details><details><summary><img alt="Windows" align="bottom" height="26px" src="https://github.com/caltechlibrary/handprint/raw/main/.graphics/os-windows-32.png">&nbsp;<strong>Windows</strong></summary>

Standalone executables for Windows are not available at this time. If you are running Windows, please use one of the other methods described below.

</details>


### Approach 2: using `pipx`

You can use [pipx](https://pypa.github.io/pipx/) to install Handprint. Pipx will install it into a separate Python environment that isolates the dependencies needed by Handprint from other Python programs on your system, and yet the resulting `handprint` command wil be executable from any shell &ndash; like any normal application on your computer. If you do not already have `pipx` on your system, it can be installed in a variety of easy ways and it is best to consult [Pipx's installation guide](https://pypa.github.io/pipx/installation/) for instructions. Once you have pipx on your system, you can install Handprint with the following command:
```sh
pipx install handprint
```

Pipx can also let you run Handprint directly using `pipx run handprint`, although in that case, you must always prefix every Handprint command with `pipx run`.  Consult the [documentation for `pipx run`](https://github.com/pypa/pipx#walkthrough-running-an-application-in-a-temporary-virtual-environment) for more information.


### Approach 3: using `pip`

If you prefer, you can install Handprint with [pip](https://pip.pypa.io/en/stable/installing/).  If you don't have `pip` package or are uncertain if you do, please consult the [pip installation instructions](https://pip.pypa.io/en/stable/installation/). Then, to install or upgrade Handprint from the Python package repository, run the following command:
```sh
python3 -m pip install handprint --upgrade
```
