Python bindings to the OpenStack Ceilometer API
==================================================

This is a client for OpenStack Ceilometer API. There's :doc:`a Python API
<api>` (the :mod:`ceilometerclient` module), and a :doc:`command-line script
<shell>` (installed as :program:`ceilometer`). Each implements the entire
OpenStack Ceilometer API.

.. seealso::

    You may want to read the `OpenStack Ceilometer Developer Guide`__  -- the overview, at
    least -- to get an idea of the concepts. By understanding the concepts
    this library should make more sense.

    __ http://docs.openstack.org/developer/ceilometer/

Contents:

.. toctree::
   :maxdepth: 2

   shell
   api
   ref/index
   ref/v2/index

Contributing
============

Code is hosted at `git.openstack.org`_. Submit bugs to the Ceilometer project on
`Launchpad`_. Submit code to the openstack/python-ceilometerclient project using
`Gerrit`_.

.. _git.openstack.org: https://git.openstack.org/cgit/openstack/python-ceilometerclient
.. _Launchpad: https://launchpad.net/ceilometer
.. _Gerrit: http://docs.openstack.org/infra/manual/developers.html#development-workflow

Run tests with ``python setup.py test``.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
