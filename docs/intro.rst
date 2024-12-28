.. _intro_toplevel:

======================
Introduction & Setup
======================

GitAnalyzer is a powerful Python-based tool designed for repository analysis and mining. It enables researchers and developers to extract comprehensive data from Git repositories, including commit information, developer details, code changes, and differential analysis. The framework supports easy data export to CSV format for further analysis.

.. image:: mygif.*

System Prerequisites
==================

* `Python`_ 3.4+
* `Git`_ (version control system)

.. _Python: https://www.python.org
.. _Git: https://git-scm.com/

Getting Started with GitAnalyzer
==============================

The simplest way to install GitAnalyzer is through `pip`_, the Python package manager. If you have pip installed, execute this command:

.. _pip: https://pip.pypa.io/en/latest/installing.html

.. sourcecode:: none

    # pip install gitanalyzer


This installation process will automatically fetch the most recent version of GitAnalyzer from the
`Python Package Index <http://pypi.python.org/pypi/GitAnalyzer>`_ and handle all dependency installations.


Repository Access
===============

The complete GitAnalyzer source code is hosted on GitHub and can be accessed at:

 * https://github.com/codingwithshawnyt/GitAnalyzer

To obtain a local copy, use the following commands::

    $ git clone https://github.com/codingwithshawnyt/GitAnalyzer
    $ cd GitAnalyzer

For optimal development setup, we recommend using a virtual environment::
    
    $ virtualenv -p python3 venv
    $ source venv/bin/activate

Install required packages::
    
    $ pip install -r requirements.txt
    $ pip install -r test-requirements.txt
    $ unzip test-repos.zip

To verify the installation, run the test suite::

    $ pytest

