# -*- encoding: utf-8 -*-
#
# Copyright © 2013 Red Hat, Inc
#
# Author:  Angus Salkeld <asalkeld@redhat.com>
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

from ceilometerclient.common import utils
from ceilometerclient.v2 import options
import ceilometerclient.exc as exc


@utils.arg('-q', '--query', metavar='<QUERY>',
           help='key[op]value; list.')
@utils.arg('-m', '--meter', metavar='<NAME>',
           help='Name of meter to show samples for.')
def do_statistics(cc, args):
    '''List the statistics for this meters'''
    fields = {'meter_name': args.meter,
              'q': options.cli_to_array(args.query)}
    if args.meter is None:
        raise exc.CommandError('Meter name not provided (-m <meter name>)')
    try:
        statistics = cc.statistics.list(**fields)
    except exc.HTTPNotFound:
        raise exc.CommandError('Samples not found: %s' % args.meter)
    else:
        field_labels = ['Period', 'Period Start', 'Period End',
                        'Count', 'Min', 'Max', 'Sum', 'Avg',
                        'Duration', 'Duration Start', 'Duration End']
        fields = ['period', 'period_start', 'period_end',
                  'count', 'min', 'max', 'sum', 'avg',
                  'duration', 'duration_start', 'duration_end']
        utils.print_list(statistics, fields, field_labels)


@utils.arg('-q', '--query', metavar='<QUERY>',
           help='key[op]value; list.')
@utils.arg('-m', '--meter', metavar='<NAME>',
           help='Name of meter to show samples for.')
def do_sample_list(cc, args):
    '''List the samples for this meters'''
    fields = {'meter_name': args.meter,
              'q': options.cli_to_array(args.query)}
    if args.meter is None:
        raise exc.CommandError('Meter name not provided (-m <meter name>)')
    try:
        samples = cc.samples.list(**fields)
    except exc.HTTPNotFound:
        raise exc.CommandError('Samples not found: %s' % args.meter)
    else:
        field_labels = ['Resource ID', 'Name', 'Type', 'Volume', 'Unit',
                        'Timestamp']
        fields = ['resource_id', 'counter_name', 'counter_type',
                  'counter_volume', 'counter_unit', 'timestamp']
        utils.print_list(samples, fields, field_labels,
                         sortby=0)


@utils.arg('-q', '--query', metavar='<QUERY>',
           help='key[op]value; list.')
def do_meter_list(cc, args={}):
    '''List the user's meter'''
    meters = cc.meters.list(q=options.cli_to_array(args.query))
    field_labels = ['Name', 'Type', 'Unit', 'Resource ID', 'User ID',
                    'Project ID']
    fields = ['name', 'type', 'unit', 'resource_id', 'user_id',
              'project_id']
    utils.print_list(meters, fields, field_labels,
                     sortby=0)


@utils.arg('-q', '--query', metavar='<QUERY>',
           help='key[op]value; list.')
def do_resource_list(cc, args={}):
    '''List the resources'''
    resources = cc.resources.list(q=options.cli_to_array(args.query))

    field_labels = ['Resource ID', 'Source', 'User ID', 'Project ID']
    fields = ['resource_id', 'source', 'user_id', 'project_id']
    utils.print_list(resources, fields, field_labels,
                     sortby=1)
