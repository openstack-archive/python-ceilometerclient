#
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

import re

from six.moves import urllib

OP_LOOKUP = {'!=': 'ne',
             '>=': 'ge',
             '<=': 'le',
             '>': 'gt',
             '<': 'lt',
             '=': 'eq'}

OP_LOOKUP_KEYS = '|'.join(sorted(OP_LOOKUP.keys(), key=len, reverse=True))
OP_SPLIT_RE = re.compile(r'(%s)' % OP_LOOKUP_KEYS)

DATA_TYPE_RE = re.compile(r'^(string|integer|float|datetime|boolean)(::)(.+)$')


def build_url(path, q, params=None):
    """Convert list of dicts and a list of params to query url format.

    This will convert the following:
        "[{field=this,op=le,value=34},
          {field=that,op=eq,value=foo,type=string}],
         ['foo=bar','sna=fu']"
    to:
        "?q.field=this&q.field=that&
          q.op=le&q.op=eq&
          q.type=&q.type=string&
          q.value=34&q.value=foo&
          foo=bar&sna=fu"
    """
    if q:
        query_params = {'q.field': [],
                        'q.value': [],
                        'q.op': [],
                        'q.type': []}

        for query in q:
            for name in ['field', 'op', 'value', 'type']:
                query_params['q.%s' % name].append(query.get(name, ''))

        # Transform the dict to a sequence of two-element tuples in fixed
        # order, then the encoded string will be consistent in Python 2&3.
        new_qparams = sorted(query_params.items(), key=lambda x: x[0])
        path += "?" + urllib.parse.urlencode(new_qparams, doseq=True)

        if params:
            for p in params:
                path += '&%s' % p
    elif params:
        path += '?%s' % params[0]
        for p in params[1:]:
            path += '&%s' % p
    return path


def cli_to_array(cli_query):
    """Convert CLI list of queries to the Python API format.

    This will convert the following:
        "this<=34;that=string::foo"
    to
        "[{field=this,op=le,value=34,type=''},
          {field=that,op=eq,value=foo,type=string}]"

    """

    if cli_query is None:
        return None

    def split_by_op(query):
        """Split a single query string to field, operator, value."""

        def _value_error(message):
            raise ValueError('invalid query %(query)s: missing %(message)s' %
                             {'query': query, 'message': message})

        try:
            field, operator, value = OP_SPLIT_RE.split(query, maxsplit=1)
        except ValueError:
            _value_error('operator')

        if not len(field):
            _value_error('field')

        if not len(value):
            _value_error('value')

        return field.strip(), operator, value.strip()

    def split_by_data_type(query_value):
        frags = DATA_TYPE_RE.match(query_value)

        # The second match is the separator. Return a list without it if
        # a type identifier was found.
        return frags.group(1, 3) if frags else None

    opts = []
    queries = cli_query.split(';')
    for q in queries:
        query = split_by_op(q)
        opt = {}
        opt['field'] = query[0]
        opt['op'] = OP_LOOKUP[query[1]]

        # Allow the data type of the value to be specified via <type>::<value>,
        # where type can be one of integer, string, float, datetime, boolean
        value_frags = split_by_data_type(query[2])
        if not value_frags:
            opt['value'] = query[2]
            opt['type'] = ''
        else:
            opt['type'] = value_frags[0]
            opt['value'] = value_frags[1]
        opts.append(opt)
    return opts
