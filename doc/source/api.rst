The :mod:`ceilometerclient` Python API
======================================

.. module:: ceilometerclient
   :synopsis: A client for the OpenStack Ceilometer API.

.. currentmodule:: ceilometerclient

Usage
-----

First create a client instance with your credentials::

    >>> import ceilometerclient.client
    >>> cclient = ceilometerclient.client.get_client(VERSION, os_username=USERNAME, os_password=PASSWORD, os_tenant_name=PROJECT_NAME, os_auth_url=AUTH_URL)

Here ``VERSION`` should be: ``2``.

Then call methods on its managers::

    >>> cclient.meters.list()
    [<Meter ...>, ...]

    >>> cclient.new_samples.list()
    [<Sample ...>, ...]

V2 client tips
++++++++++++++

Use queries to narrow your search (more info at `Ceilometer V2 API reference`__)::

    >>> query = [dict(field='resource_id', op='eq', value='5a301761-f78b-46e2-8900-8b4f6fe6675a'), dict(field='meter',op='eq',value='cpu_util')]
    >>> cclient.new_samples.list(q=query, limit=10)
    [<Sample ...>, ...]

__  http://docs.openstack.org/developer/ceilometer/webapi/v2.html#Query

Reference
---------

For more information, see the reference:

.. toctree::
   :maxdepth: 2

   ref/index
   ref/v2/index
