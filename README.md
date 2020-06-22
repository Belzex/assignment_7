# Python Interpreter Setup
The following steps guide you through the process of the project setup.
It is assumed, that a terminal is used for the setup process and the current directory is the root directory of the project.

## Install virtual environment

Install the virtual environment tool using pip. Note: one of the following commands is sufficient for this step. If the first command fails, please try the second command. 

* ``$ pip install virtualenv`` or
* ``$ python -m pip install virtualenv``

## Initialize virtual environment
This step will install python, pip and some other basic libraries.

* ```$ virtualenv venv``` or
* ```$ python3 -m venv venv``` or
* ```$ python3 -m virtualenv venv```


After this step, the virtual environment must be activated to start working on the project.
## Activate virtual environment

`` $ source venv/bin/activate ``

This step will activate the virtual environment.

## Install the dependencies

The required python libraries are installed with the following command:

``$ pip install -r requirements.txt``

## Add virtual environment to your IDE
As a last step, the virtual environment has to be set in your IDE as the interpreter of this project. After doing so, it might be possible, that a restart of the IDE is necessary to conclude the installation.
For example: ```venv/bin/python3```

# Starting the project
This step is done in the root folder of the project. 
After the successful setup of the python virtual environment run the command: 

```$ python manage.py runserver``` 


The Django server should start and a message containing the address of where to find the web server in the browser should be printed to the command line.
Simply follow this address and test the recommendation system.