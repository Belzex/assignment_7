# Python Interpreter Setup
The following steps guide you through the process of the project setup.
It is assumed, that a terminal is used for the setup process and the current directory is the root of the project.

## Install virtual environment

Install the virtual environment tool using pip. Note: one of the following commands is sufficient for this step. If the first command fails, please try the second command. 

* ``$ pip install virtualenv``
* ``$ python -m pip install virtualenv``

### Activate virtual environment

`` $ source venv/bin/activate ``

This step will activate the virtual environment.

### Install the dependencies

The required python libraries are installed with the following command:

``$ pip install -r requirements.txt``

### Add virtual environment to your IDE
As a last step, the virtual environment has to be set in your IDE as the interpreter of this project. After doing so, it might be possible, that a restart of the IDE is necessary to conclude the installation.