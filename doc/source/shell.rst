The :program:`ceilometer` shell utility
=========================================

.. program:: ceilometer
.. highlight:: bash

The :program:`ceilometer` shell utility interacts with OpenStack Ceilometer API
from the command line. It supports the entirety of the OpenStack Ceilometer API.

You'll need to provide :program:`ceilometer` with your OpenStack credentials.
You can do this with the :option:`--os-username`, :option:`--os-password`,
:option:`--os-tenant-name` and :option:`--os-auth-url` options, but it's easier to
just set them as environment variables:

.. envvar:: OS_USERNAME

    Your OpenStack username.

.. envvar:: OS_PASSWORD

    Your password.

.. envvar:: OS_TENANT_NAME

    Project to work on.

.. envvar:: OS_AUTH_URL

    The OpenStack auth server URL (keystone).

For example, in Bash you would use::

    export OS_USERNAME=user
    export OS_PASSWORD=pass
    export OS_TENANT_NAME=myproject
    export OS_AUTH_URL=http://auth.example.com:5000/v2.0

.. note::

    You can use --os-tenant-id or export OS_TENANT_ID to specify the project.

The command line tool will attempt to reauthenticate using your provided credentials
for every request. You can override this behavior by manually supplying an auth
token using :option:`--os-ceilometer-url` and :option:`--os-auth-token`. You can alternatively
set these environment variables::

    export OS_CEILOMETER_URL=http://ceilometer.example.org:8777
    export OS_AUTH_TOKEN=3bcc3d3a03f44e3d8377f9247b0ad155

From there, all shell commands take the form::

    ceilometer <command> [arguments...]

Run :program:`ceilometer help` to get a full list of all possible commands,
and run :program:`ceilometer help <command>` to get detailed help for that
command.

Keystone API v3 support
-----------------------

Keystone API v3 has introduced a concept named domain, which allows you to
create projects and users with duplicate names in different domains. When
request to Keystone API v3, you should provide the specific UUIDs of project
and user, or the names but with corresponding domain information.

For example, in Bash you could use::

    export OS_USER_ID=791217dd9edf4aa8b64d10e48d2c66cb
    export OS_PASSWORD=pass
    export OS_PROJECT_ID=5ee5c3cee2ef4e3690f2f17ec3049a84
    export OS_AUTH_URL=http://auth.example.com:5000/v3

You can provide user name and domain information instead of single OS_USER_ID::

    export OS_USERNAME=admin
    export OS_USER_DOMAIN_NAME=default

or::

    export OS_USERNAME=admin
    export OS_USER_DOMAIN_ID=default

.. note::

    Keystone uses string default as UUID of default domain to be compatiable
    with API v2.

You can provide project name and domain information instead of single
OS_PROJECT_ID::

    export OS_PROJECT_NAME=admin
    export OS_PROJECT_DOMAIN_NAME=default

or::

    export OS_PROJECT_NAME=admin
    export OS_PROJECT_DOMAIN_ID=default

V2 client tips
--------------

Use queries to narrow your search (more info at `Ceilometer V2 API reference`__)::

    ceilometer sample-list --meter cpu_util --query 'resource_id=5a301761-f78b-46e2-8900-8b4f6fe6675a' --limit 10

__  http://docs.openstack.org/developer/ceilometer/webapi/v2.html#Query
