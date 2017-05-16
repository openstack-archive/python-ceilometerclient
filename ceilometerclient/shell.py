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
import warnings

from oslo_utils import encodeutils
from oslo_utils import importutils
import six

import ceilometerclient
from ceilometerclient import client as ceiloclient
from ceilometerclient.common import utils
from ceilometerclient import exc


def _positive_non_zero_int(argument_value):
    if argument_value is None:
        return None
    try:
        value = int(argument_value)
    except ValueError:
        msg = "%s must be an integer" % argument_value
        raise argparse.ArgumentTypeError(msg)
    if value <= 0:
        msg = "%s must be greater than 0" % argument_value
        raise argparse.ArgumentTypeError(msg)
    return value


class CeilometerShell(object):

    def __init__(self):
        self.auth_plugin = ceiloclient.AuthPlugin()

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
                            default=bool(utils.env('CEILOMETERCLIENT_DEBUG')
                                         ),
                            action='store_true',
                            help='Defaults to env[CEILOMETERCLIENT_DEBUG].')

        parser.add_argument('-v', '--verbose',
                            default=False, action="store_true",
                            help="Print more verbose output.")

        parser.add_argument('--timeout',
                            default=600,
                            type=_positive_non_zero_int,
                            help='Number of seconds to wait for a response.')

        parser.add_argument('--ceilometer-url', metavar='<CEILOMETER_URL>',
                            dest='os_endpoint',
                            default=utils.env('CEILOMETER_URL'),
                            help=("DEPRECATED, use --os-endpoint instead. "
                                  "Defaults to env[CEILOMETER_URL]."))

        parser.add_argument('--ceilometer_url',
                            dest='os_endpoint',
                            help=argparse.SUPPRESS)

        parser.add_argument('--ceilometer-api-version',
                            default=utils.env(
                                'CEILOMETER_API_VERSION', default='2'),
                            help='Defaults to env[CEILOMETER_API_VERSION] '
                            'or 2.')

        parser.add_argument('--ceilometer_api_version',
                            help=argparse.SUPPRESS)

        self.auth_plugin.add_opts(parser)
        self.auth_plugin.add_common_opts(parser)

        return parser

    def get_subcommand_parser(self, version):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')
        submodule = importutils.import_versioned_module('ceilometerclient',
                                                        version, 'shell')
        self._find_actions(subparsers, submodule)
        self._find_actions(subparsers, self)

        return parser

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

    @staticmethod
    def _setup_logging(debug):
        format = '%(levelname)s (%(module)s) %(message)s'
        if debug:
            logging.basicConfig(format=format, level=logging.DEBUG)
        else:
            logging.basicConfig(format=format, level=logging.WARN)
        logging.getLogger('iso8601').setLevel(logging.WARNING)
        logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

    def parse_args(self, argv):
        # Parse args once to find version
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
        warnings.warn(
            "ceilometerclient is now deprecated as the Ceilometer API has "
            "been deprecated. Please use either aodhclient, pankoclient or "
            "gnocchiclient.")
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

        if not ((self.auth_plugin.opts.get('token')
                 or self.auth_plugin.opts.get('auth_token'))
                and self.auth_plugin.opts['endpoint']):
            if not self.auth_plugin.opts['username']:
                raise exc.CommandError("You must provide a username via "
                                       "either --os-username or via "
                                       "env[OS_USERNAME]")

            if not self.auth_plugin.opts['password']:
                raise exc.CommandError("You must provide a password via "
                                       "either --os-password or via "
                                       "env[OS_PASSWORD]")

            if not (args.os_project_id or args.os_project_name
                    or args.os_tenant_id or args.os_tenant_name):
                # steer users towards Keystone V3 API
                raise exc.CommandError("You must provide a project_id "
                                       "(or name) via either --os-project-id "
                                       "or via env[OS_PROJECT_ID]")

            if not self.auth_plugin.opts['auth_url']:
                raise exc.CommandError("You must provide an auth url via "
                                       "either --os-auth-url or via "
                                       "env[OS_AUTH_URL]")

        client_kwargs = vars(args)
        client_kwargs.update(self.auth_plugin.opts)
        client_kwargs['auth_plugin'] = self.auth_plugin
        client = ceiloclient.get_client(api_version, **client_kwargs)
        # call whatever callback was selected
        try:
            args.func(client, args)
        except exc.HTTPUnauthorized:
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
    def __init__(self, prog, indent_increment=2, max_help_position=32,
                 width=None):
        super(HelpFormatter, self).__init__(prog, indent_increment,
                                            max_help_position, width)

    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)


def main(args=None):
    try:
        if args is None:
            args = sys.argv[1:]

        CeilometerShell().main(args)

    except Exception as e:
        if '--debug' in args or '-d' in args:
            raise
        else:
            print(encodeutils.safe_encode(six.text_type(e)), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Stopping Ceilometer Client", file=sys.stderr)
        sys.exit(130)

if __name__ == "__main__":
    main()
