Uplink
======

Uplink is a test framework for `Red Hat Satellite 6`_. It lets you execute a workflow like
this:

.. code-block:: sh

    pip install uplink
    uplink settings create  # generate the settings file
    python3 -m unittest discover uplink.tests  # run the tests

Uplink is a GPL-licensed Python library, but no knowledge of Python is
required to execute the tests. Just install the application, run it, and follow
the prompts.

Uplink has a presence on the following websites:

* `Documentation`_ is available on ReadTheDocs.
* A `Python package`_ is available on PyPi.
* `Source code`_ and the issue tracker are available on GitHub.

.. _Documentation: http://uplink.readthedocs.io
.. _Red Hat Satellite 6: http://www.redhat.com/en/technologies/management/satellite
.. _Python package: https://pypi.python.org/pypi/uplink
.. _Source code: https://github.com/omaciel/uplink/

.. All text above this comment should also be in docs/index.rst, word for word.
