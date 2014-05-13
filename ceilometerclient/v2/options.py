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

from six.moves.urllib import parse


def build_url(path, q, params=None):
    '''This converts from a list of dicts and a list of params to
       what the rest api needs, so from:
    "[{field=this,op=le,value=34},
      {field=that,op=eq,value=foo,type=string}],
     ['foo=bar','sna=fu']"
    to:
    "?q.field=this&q.field=that&
      q.op=le&q.op=eq&
      q.type=&q.type=string&
      q.value=34&q.value=foo&
      foo=bar&sna=fu"
    '''
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
        path += "?" + parse.urlencode(new_qparams, doseq=True)

        if params:
            for p in params:
                path += '&%s' % p
    elif params:
        path += '?%s' % params[0]
        for p in params[1:]:
            path += '&%s' % p
    return path


def cli_to_array(cli_query):
    """This converts from the cli list of queries to what is required
    by the python api.
    so from:
    "this<=34;that=string::foo"
    to
    "[{field=this,op=le,value=34,type=''},
      {field=that,op=eq,value=foo,type=string}]"

    """

    if cli_query is None:
        return None

    op_lookup = {'!=': 'ne',
                 '>=': 'ge',
                 '<=': 'le',
                 '>': 'gt',
                 '<': 'lt',
                 '=': 'eq'}

    def split_by_op(string):
        # two character split (<=,!=)
        frags = re.findall(r'([[a-zA-Z0-9_.]+)([><!]=)([^ -,\t\n\r\f\v]+)',
                           string)
        if len(frags) == 0:
            # single char split (<,=)
            frags = re.findall(r'([a-zA-Z0-9_.]+)([><=])([^ -,\t\n\r\f\v]+)',
                               string)
        return frags

    def split_by_data_type(string):
        frags = re.findall(r'^(string|integer|float|datetime|boolean)(::)'
                           r'([^ -,\t\n\r\f\v]+)$', string)

        # frags[1] is the separator. Return a list without it if the type
        # identifier was found.
        return [frags[0][0], frags[0][2]] if frags else None

    opts = []
    queries = cli_query.split(';')
    for q in queries:
        frag = split_by_op(q)
        if len(frag) > 1:
            raise ValueError('incorrect separator %s in query "%s"' %
                             ('(should be ";")', q))
        if len(frag) == 0:
            raise ValueError('invalid query %s' % q)
        query = frag[0]
        opt = {}
        opt['field'] = query[0]
        opt['op'] = op_lookup[query[1]]

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
