#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Command-line interface to the OpenStack Telemetry API.
"""

from __future__ import print_function

import argparse
import logging
import sys

import six

import ceilometerclient
from ceilometerclient import client as ceiloclient
from ceilometerclient.common import utils
from ceilometerclient import exc
from ceilometerclient.openstack.common.apiclient import auth
from ceilometerclient.openstack.common import cliutils
from ceilometerclient.openstack.common.apiclient import exceptions
from ceilometerclient.openstack.common import strutils


class CeilometerShell(object):

    def get_base_parser(self):
        parser = argparse.ArgumentParser(
            prog='ceilometer',
            description=__doc__.strip(),
            epilog='See "ceilometer help COMMAND" '
                   'for help on a specific command.',
            add_help=False,
            formatter_class=HelpFormatter,
        )

        # Global arguments
        parser.add_argument('-h', '--help',
                            action='store_true',
                            help=argparse.SUPPRESS,
                            )

        parser.add_argument('--version',
                            action='version',
                            version=ceilometerclient.__version__)

        parser.add_argument('-d', '--debug',
                            default=bool(cliutils.env('CEILOMETERCLIENT_DEBUG')
                                         ),
                            action='store_true',
                            help='Defaults to env[CEILOMETERCLIENT_DEBUG]')

        parser.add_argument('-v', '--verbose',
                            default=False, action="store_true",
                            help="Print more verbose output")

        parser.add_argument('-k', '--insecure',
                            default=False,
                            action='store_true',
                            help="Explicitly allow ceilometerclient to "
                            "perform \"insecure\" SSL (https) requests. "
                            "The server's certificate will "
                            "not be verified against any certificate "
                            "authorities. This option should be used with "
                            "caution.")

        parser.add_argument('--cert-file',
                            help='Path of certificate file to use in SSL '
                            'connection. This file can optionally be prepended'
                            ' with the private key.')

        parser.add_argument('--key-file',
                            help='Path of client key to use in SSL connection.'
                            ' This option is not necessary if your key is '
                            'prepended to your cert file.')

        parser.add_argument('--timeout',
                            default=600,
                            help='Number of seconds to wait for a response')

        parser.add_argument('--ceilometer-url',
                            default=cliutils.env('CEILOMETER_URL'),
                            help='Defaults to env[CEILOMETER_URL]')

        parser.add_argument('--ceilometer_url',
                            help=argparse.SUPPRESS)

        parser.add_argument('--ceilometer-api-version',
                            default=cliutils.env(
                            'CEILOMETER_API_VERSION', default='2'),
                            help='Defaults to env[CEILOMETER_API_VERSION] '
                            'or 2')

        parser.add_argument('--ceilometer_api_version',
                            help=argparse.SUPPRESS)

        self.auth_plugin.add_opts(parser)
        self.auth_plugin.add_common_opts(parser)


        return parser

    def get_subcommand_parser(self, version):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')
        submodule = utils.import_versioned_module(version, 'shell')
        self._find_actions(subparsers, submodule)
        self._find_actions(subparsers, self)
        self._add_bash_completion_subparser(subparsers)

        return parser

    def _add_bash_completion_subparser(self, subparsers):
        subparser = subparsers.add_parser(
            'bash_completion',
            add_help=False,
            formatter_class=HelpFormatter
        )
        self.subcommands['bash_completion'] = subparser
        subparser.set_defaults(func=self.do_bash_completion)

    def _find_actions(self, subparsers, actions_module):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            # I prefer to be hypen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(command, help=help,
                                              description=desc,
                                              add_help=False,
                                              formatter_class=HelpFormatter)
            subparser.add_argument('-h', '--help', action='help',
                                   help=argparse.SUPPRESS)
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def _setup_logging(self, debug):
        format = '%(levelname)s (%(module)s:%(lineno)d) %(message)s'
        if debug:
            logging.basicConfig(format=format, level=logging.DEBUG)
        else:
            logging.basicConfig(format=format, level=logging.WARN)

    def parse_args(self, argv):
        # Parse args once to find version
        self.auth_plugin = AuthPlugin(argv)
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        self.auth_plugin.parse_opts(options)
        self._setup_logging(options.debug)

        # build available subcommands based on version
        api_version = options.ceilometer_api_version
        subcommand_parser = self.get_subcommand_parser(api_version)
        self.parser = subcommand_parser

        # Handle top-level --help/-h before attempting to parse
        # a command off the command line
        if options.help or not argv:
            self.do_help(options)
            return 0

        # Return parsed args
        return api_version, subcommand_parser.parse_args(argv)

    def main(self, argv):
        parsed = self.parse_args(argv)
        if parsed == 0:
            return 0
        api_version, args = parsed

        # Short-circuit and deal with help command right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0
        elif args.func == self.do_bash_completion:
            self.do_bash_completion(args)
            return 0

        if not (self.auth_plugin.opts['token'] and args.ceilometer_url):
            if not self.auth_plugin.opts['username']:
                raise exc.CommandError("You must provide a username via "
                                       "either --os-username or via "
                                       "env[OS_USERNAME]")

            if not self.auth_plugin.opts['password']:
                raise exc.CommandError("You must provide a password via "
                                       "either --os-password or via "
                                       "env[OS_PASSWORD]")

            if not (self.auth_plugin.opts['tenant_id']
                    or self.auth_plugin.opts['tenant_name']):
                raise exc.CommandError("You must provide a tenant_id via "
                                       "either --os-tenant-id or via "
                                       "env[OS_TENANT_ID]")

            if not self.auth_plugin.opts['auth_url']:
                raise exc.CommandError("You must provide an auth url via "
                                       "either --os-auth-url or via "
                                       "env[OS_AUTH_URL]")

        args.__dict__.update(self.auth_plugin.opts)
        client = ceiloclient.Client(api_version,
                                    self.auth_plugin, **args.__dict__)

        # call whatever callback was selected
        try:
            args.func(client, args)
        except exc.Unauthorized:
            raise exc.CommandError("Invalid OpenStack Identity credentials.")

    def do_bash_completion(self, args):
        """Prints all of the commands and options to stdout.

        The ceilometer.bash_completion script doesn't have to hard code them.
        """
        commands = set()
        options = set()
        for sc_str, sc in self.subcommands.items():
            commands.add(sc_str)
            for option in list(sc._optionals._option_string_actions):
                options.add(option)

        commands.remove('bash-completion')
        commands.remove('bash_completion')
        print(' '.join(commands | options))

    @utils.arg('command', metavar='<subcommand>', nargs='?',
               help='Display help for <subcommand>')
    def do_help(self, args):
        """Display help about this program or one of its subcommands."""
        if getattr(args, 'command', None):
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError("'%s' is not a valid subcommand" %
                                       args.command)
        else:
            self.parser.print_help()


class HelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)


class AuthPlugin(auth.BaseAuthPlugin):
    opt_names = ['tenant_id', 'region_name', 'token',
                 'service_type', 'endpoint_type', 'cacert']

    def __init__(self, auth_system=None, **kwargs):
        self.opt_names.extend(self.common_opt_names)
        super(AuthPlugin, self).__init__(auth_system=None, **kwargs)

    def _do_authenticate(self, http_client):
        if self.opts.get('token') and self.opts.get('ceilometer_url'):
            token = self.opts.get('token')
            endpoint = self.opts.get('ceilometer_url')
        elif (self.opts.get('username') and
              self.opts.get('password') and
              self.opts.get('auth_url') and
              (self.opts.get('tenant_id') or self.opts.get('tenant_name'))):

            ks_kwargs = {
                'username': self.opts.get('username'),
                'password': self.opts.get('password'),
                'tenant_id': self.opts.get('tenant_id'),
                'tenant_name': self.opts.get('tenant_name'),
                'auth_url': self.opts.get('auth_url'),
                'region_name': self.opts.get('region_name'),
                'service_type': self.opts.get('service_type'),
                'endpoint_type': self.opts.get('endpoint_type'),
                'cacert': self.opts.get('cacert'),
                'insecure': self.opts.get('insecure'),
            }
            _ksclient = ceiloclient._get_ksclient(**ks_kwargs)
            token = ((lambda: self.opts.get('auth_token'))
                     if self.opts.get('auth_token')
                     else (lambda: _ksclient.auth_token))

            endpoint = self.opts.get('ceilometer_url') or \
                ceiloclient._get_endpoint(_ksclient, **ks_kwargs)
        self.opts['token'] = token()
        self.opts['endpoint'] = endpoint

    def token_and_endpoint(self, endpoint_type, service_type):
        return self.opts.get('token'), self.opts.get('endpoint')

    def sufficient_options(self):
        """Check if all required options are present.

        :raises: AuthPluginOptionsMissing
        """
        missing = [opt
                   for opt in self.opt_names
                   if self.opts.get(opt) is None]
        if missing:
            raise exceptions.AuthPluginOptionsMissing(missing)


def main(args=None):
    try:
        if args is None:
            args = sys.argv[1:]

        CeilometerShell().main(args)

    except Exception as e:
        if '--debug' in args or '-d' in args:
            raise
        else:
            print(strutils.safe_encode(six.text_type(e)), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
