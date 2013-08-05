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
import urllib


def build_url(path, q, params=None):
    '''This converts from a list of dicts and a list of params to
       what the rest api needs, so from:
    "[{field=this,op=le,value=34},{field=that,op=eq,value=foo}],
     ['foo=bar','sna=fu']"
    to:
    "?q.field=this&q.op=le&q.value=34&
      q.field=that&q.op=eq&q.value=foo&
      foo=bar&sna=fu"
    '''
    if q:
        query_params = {'q.field': [],
                        'q.value': [],
                        'q.op': []}

        for query in q:
            for name in ['field', 'op', 'value']:
                query_params['q.%s' % name].append(query.get(name, ''))

        path += "?" + urllib.urlencode(query_params, doseq=True)

        if params:
            for p in params:
                path += '&%s' % p
    elif params:
        path += '?%s' % params[0]
        for p in params[1:]:
            path += '&%s' % p
    return path


def cli_to_array(cli_query):
    '''This converts from the cli list of queries to what is required
    by the python api.
    so from:
    "this<=34;that=foo"
    to
    "[{field=this,op=le,value=34},{field=that,op=eq,value=foo}]"
    '''
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
            #single char split (<,=)
            frags = re.findall(r'([a-zA-Z0-9_.]+)([><=])([^ -,\t\n\r\f\v]+)',
                               string)
        return frags

    opts = []
    queries = cli_query.split(';')
    for q in queries:
        frag = split_by_op(q)
        if len(frag) > 1:
            raise ValueError('incorrect seperator %s in query "%s"' %
                             ('(should be ";")', q))
        if len(frag) == 0:
            raise ValueError('invalid query %s' % q)
        query = frag[0]
        opt = {}
        opt['field'] = query[0]
        opt['op'] = op_lookup[query[1]]
        opt['value'] = query[2]
        opts.append(opt)
    return opts
