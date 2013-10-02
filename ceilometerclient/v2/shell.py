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

import functools
import json

from ceilometerclient.common import utils
from ceilometerclient import exc
from ceilometerclient.v2 import options


ALARM_STATES = ['ok', 'alarm', 'insufficient_data']
ALARM_OPERATORS = ['lt', 'le', 'eq', 'ne', 'ge', 'gt']
ALARM_COMBINATION_OPERATORS = ['and', 'or']
STATISTICS = ['max', 'min', 'avg', 'sum', 'count']
OPERATORS_STRING = dict(gt='>', ge='>=',
                        lt='<', le="<=",
                        eq='==', ne='!=')


@utils.arg('-q', '--query', metavar='<QUERY>',
           help='key[op]value; list.')
@utils.arg('-m', '--meter', metavar='<NAME>', required=True,
           help='Name of meter to show samples for.')
@utils.arg('-p', '--period', metavar='<PERIOD>',
           help='Period in seconds over which to group samples.')
def do_statistics(cc, args):
    '''List the statistics for this meter.'''
    fields = {'meter_name': args.meter,
              'q': options.cli_to_array(args.query),
              'period': args.period}
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
@utils.arg('-m', '--meter', metavar='<NAME>', required=True,
           help='Name of meter to show samples for.')
def do_sample_list(cc, args):
    '''List the samples for this meters.'''
    fields = {'meter_name': args.meter,
              'q': options.cli_to_array(args.query)}
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


@utils.arg('--project-id', metavar='<PROJECT_ID>',
           help='Tenant to associate with sample '
                '(only settable by admin users)')
@utils.arg('--user-id', metavar='<USER_ID>',
           help='User to associate with sample '
                '(only settable by admin users)')
@utils.arg('-r', '--resource-id', metavar='<RESOURCE_ID>', required=True,
           help='ID of the resource.')
@utils.arg('-m', '--meter-name', metavar='<METER_NAME>',
           help='the meter name')
@utils.arg('--meter-type', metavar='<METER_TYPE>', required=True,
           help='the meter type')
@utils.arg('--meter-unit', metavar='<METER_UNIT>', required=True,
           help='the meter unit')
@utils.arg('--sample-volume', metavar='<SAMPLE_VOLUME>', required=True,
           help='The sample volume')
@utils.arg('--resource-metadata', metavar='<RESOURCE_METADATA>',
           help='resource metadata')
def do_sample_create(cc, args={}):
    '''Create a sample.'''
    arg_to_field_mapping = {'meter_name': 'counter_name',
                            'meter_unit': 'counter_unit',
                            'meter_type': 'counter_type',
                            'sample_volume': 'counter_volume'}
    fields = {}
    for var in vars(args).items():
        k, v = var[0], var[1]
        if v is not None:
            if k == 'resource_metadata':
                fields[k] = json.loads(v)
            else:
                fields[arg_to_field_mapping.get(k, k)] = v
    cc.samples.create(**fields)


@utils.arg('-q', '--query', metavar='<QUERY>',
           help='key[op]value; list.')
def do_meter_list(cc, args={}):
    '''List the user's meters.'''
    meters = cc.meters.list(q=options.cli_to_array(args.query))
    field_labels = ['Name', 'Type', 'Unit', 'Resource ID', 'User ID',
                    'Project ID']
    fields = ['name', 'type', 'unit', 'resource_id', 'user_id',
              'project_id']
    utils.print_list(meters, fields, field_labels,
                     sortby=0)


def _display_rule(type, rule):
    if type == 'threshold':
        return ('%(meter_name)s %(comparison_operator)s '
                '%(threshold)s during %(evaluation_periods)s x %(period)ss' %
                {
                    'meter_name': rule['meter_name'],
                    'threshold': rule['threshold'],
                    'evaluation_periods': rule['evaluation_periods'],
                    'period': rule['period'],
                    'comparison_operator': OPERATORS_STRING.get(
                        rule['comparison_operator'])
                })
    elif type == 'combination':
        return ('combinated states (%(operator)s) of %(alarms)s' % {
            'operator': rule['operator'].upper(),
            'alarms': ", ".join(rule['alarm_ids'])})
    else:
        # just dump all
        return "\n".join(["%s: %s" % (f, v)
                          for f, v in rule.iteritems()])


def alarm_rule_formatter(alarm):
    return _display_rule(alarm.type, alarm.rule)


def _infer_type(detail):
    if 'type' in detail:
        return detail['type']
    elif 'meter_name' in detail['rule']:
        return 'threshold'
    elif 'alarms' in detail['rule']:
        return 'combination'
    else:
        return 'unknown'


def alarm_change_detail_formatter(change):
    detail = json.loads(change.detail)
    fields = []
    if change.type == 'state transition':
        fields.append('state: %s' % detail['state'])
    elif change.type == 'creation' or change.type == 'deletion':
        for k in ['name', 'description', 'type', 'rule']:
            if k == 'rule':
                fields.append('rule: %s' % _display_rule(detail['type'],
                                                         detail[k]))
            else:
                fields.append('%s: %s' % (k, detail[k]))
    elif change.type == 'rule change':
        for k, v in detail.iteritems():
            if k == 'rule':
                fields.append('rule: %s' % _display_rule(_infer_type(detail),
                                                         v))
            else:
                fields.append('%s: %s' % (k, v))
    return '\n'.join(fields)


@utils.arg('-q', '--query', metavar='<QUERY>',
           help='key[op]value; list.')
def do_alarm_list(cc, args={}):
    '''List the user's alarms.'''
    alarms = cc.alarms.list(q=options.cli_to_array(args.query))
    # omit action initially to keep output width sane
    # (can switch over to vertical formatting when available from CLIFF)
    field_labels = ['Alarm ID', 'Name', 'State', 'Enabled', 'Continuous',
                    'Alarm condition']
    fields = ['alarm_id', 'name', 'state', 'enabled', 'repeat_actions',
              'rule']
    utils.print_list(alarms, fields, field_labels,
                     formatters={'rule': alarm_rule_formatter}, sortby=0)


def alarm_query_formater(alarm):
    qs = []
    for q in alarm.rule['query']:
        qs.append('%s %s %s' % (
            q['field'], OPERATORS_STRING.get(q['op']), q['value']))
    return r' AND\n'.join(qs)


def _display_alarm(alarm):
    fields = ['name', 'description', 'type',
              'state', 'enabled', 'alarm_id', 'user_id', 'project_id',
              'alarm_actions', 'ok_actions', 'insufficient_data_actions',
              'repeat_actions']
    data = dict([(f, getattr(alarm, f, '')) for f in fields])
    data.update(alarm.rule)
    if alarm.type == 'threshold':
        data['query'] = alarm_query_formater(alarm)
    utils.print_dict(data, wrap=72)


@utils.arg('-a', '--alarm_id', metavar='<ALARM_ID>', required=True,
           help='ID of the alarm to show.')
def do_alarm_show(cc, args={}):
    '''Show an alarm.'''
    try:
        alarm = cc.alarms.get(args.alarm_id)
    except exc.HTTPNotFound:
        raise exc.CommandError('Alarm not found: %s' % args.alarm_id)
    else:
        _display_alarm(alarm)


def common_alarm_arguments(create=False):
    def _wrapper(func):
        @utils.arg('--name', metavar='<NAME>', required=create,
                   help='Name of the alarm (must be unique per tenant)')
        @utils.arg('--project-id', metavar='<PROJECT_ID>',
                   help='Tenant to associate with alarm '
                   '(only settable by admin users)')
        @utils.arg('--user-id', metavar='<USER_ID>',
                   help='User to associate with alarm '
                   '(only settable by admin users)')
        @utils.arg('--description', metavar='<DESCRIPTION>',
                   help='Free text description of the alarm')
        @utils.arg('--state', metavar='<STATE>',
                   help='State of the alarm, one of: ' + str(ALARM_STATES))
        @utils.arg('--enabled', type=utils.string_to_bool,
                   metavar='{True|False}',
                   help='True if alarm evaluation/actioning is enabled')
        @utils.arg('--alarm-action', dest='alarm_actions',
                   metavar='<Webhook URL>', action='append', default=None,
                   help=('URL to invoke when state transitions to alarm. '
                         'May be used multiple times.'))
        @utils.arg('--ok-action', dest='ok_actions',
                   metavar='<Webhook URL>', action='append', default=None,
                   help=('URL to invoke when state transitions to OK. '
                         'May be used multiple times.'))
        @utils.arg('--insufficient-data-action',
                   dest='insufficient_data_actions',
                   metavar='<Webhook URL>', action='append', default=None,
                   help=('URL to invoke when state transitions to unkown. '
                         'May be used multiple times.'))
        @utils.arg('--repeat-actions', dest='repeat_actions',
                   metavar='{True|False}', type=utils.string_to_bool,
                   default=False,
                   help=('True if actions should be repeatedly notified '
                         'while alarm remains in target state'))
        @functools.wraps(func)
        def _wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        return _wrapped
    return _wrapper


@common_alarm_arguments(create=True)
@utils.arg('--period', type=int, metavar='<PERIOD>',
           help='Length of each period (seconds) to evaluate over')
@utils.arg('--evaluation-periods', type=int, metavar='<COUNT>',
           help='Number of periods to evaluate over')
@utils.arg('--meter-name', metavar='<METRIC>', required=True,
           help='Metric to evaluate against')
@utils.arg('--statistic', metavar='<STATISTIC>',
           help='Statistic to evaluate, one of: ' + str(STATISTICS))
@utils.arg('--comparison-operator', metavar='<OPERATOR>',
           help='Operator to compare with, one of: ' + str(ALARM_OPERATORS))
@utils.arg('--threshold', type=float, metavar='<THRESHOLD>', required=True,
           help='Threshold to evaluate against')
@utils.arg('--matching-metadata', dest='matching_metadata',
           metavar='<Matching Metadata>', action='append', default=None,
           help=('A meter should match this resource metadata (key=value) '
                 'additionally to the meter_name'))
def do_alarm_create(cc, args={}):
    '''Create a new alarm (Deprecated).'''
    fields = dict(filter(lambda x: not (x[1] is None), vars(args).items()))
    fields = utils.args_array_to_dict(fields, "matching_metadata")
    alarm = cc.alarms.create(**fields)
    _display_alarm(alarm)


@common_alarm_arguments(create=True)
@utils.arg('--meter-name', metavar='<METRIC>', required=True,
           dest='threshold_rule/meter_name',
           help='Metric to evaluate against')
@utils.arg('--period', type=int, metavar='<PERIOD>',
           dest='threshold_rule/period',
           help='Length of each period (seconds) to evaluate over')
@utils.arg('--evaluation-periods', type=int, metavar='<COUNT>',
           dest='threshold_rule/evaluation_periods',
           help='Number of periods to evaluate over')
@utils.arg('--statistic', metavar='<STATISTIC>',
           dest='threshold_rule/statistic',
           help='Statistic to evaluate, one of: ' + str(STATISTICS))
@utils.arg('--comparison-operator', metavar='<OPERATOR>',
           dest='threshold_rule/comparison_operator',
           help='Operator to compare with, one of: ' + str(ALARM_OPERATORS))
@utils.arg('--threshold', type=float, metavar='<THRESHOLD>', required=True,
           dest='threshold_rule/threshold',
           help='Threshold to evaluate against')
@utils.arg('-q', '--query', metavar='<QUERY>',
           dest='threshold_rule/query',
           help='The query to find the data for computing statistics '
           '(key[op]value; list.)')
def do_alarm_threshold_create(cc, args={}):
    '''Create a new alarm based on computed statistics.'''
    fields = dict(filter(lambda x: not (x[1] is None), vars(args).items()))
    fields = utils.key_with_slash_to_nested_dict(fields)
    fields['type'] = 'threshold'
    if 'query' in fields['threshold_rule']:
        fields['threshold_rule']['query'] = options.cli_to_array(
            fields['threshold_rule']['query'])
    alarm = cc.alarms.create(**fields)
    _display_alarm(alarm)


@common_alarm_arguments(create=True)
@utils.arg('--alarm_ids', action='append', metavar='<ALARM IDS>',
           required=True, dest='combination_rule/alarm_ids',
           help='List of alarm id')
@utils.arg('--operator', metavar='<OPERATOR>',
           dest='combination_rule/operator',
           help='Operator to compare with, one of: ' + str(
               ALARM_COMBINATION_OPERATORS))
def do_alarm_combination_create(cc, args={}):
    '''Create a new alarm based on state of other alarms.'''
    fields = dict(filter(lambda x: not (x[1] is None), vars(args).items()))
    fields = utils.key_with_slash_to_nested_dict(fields)
    fields['type'] = 'combination'
    alarm = cc.alarms.create(**fields)
    _display_alarm(alarm)


@utils.arg('-a', '--alarm_id', metavar='<ALARM_ID>', required=True,
           help='ID of the alarm to update.')
@common_alarm_arguments()
@utils.arg('--period', type=int, metavar='<PERIOD>',
           help='Length of each period (seconds) to evaluate over')
@utils.arg('--evaluation-periods', type=int, metavar='<COUNT>',
           help='Number of periods to evaluate over')
@utils.arg('--meter-name', metavar='<METRIC>',
           help='Metric to evaluate against')
@utils.arg('--statistic', metavar='<STATISTIC>',
           help='Statistic to evaluate, one of: ' + str(STATISTICS))
@utils.arg('--comparison-operator', metavar='<OPERATOR>',
           help='Operator to compare with, one of: ' + str(ALARM_OPERATORS))
@utils.arg('--threshold', type=float, metavar='<THRESHOLD>',
           help='Threshold to evaluate against')
@utils.arg('--matching-metadata', dest='matching_metadata',
           metavar='<Matching Metadata>', action='append', default=None,
           help=('A meter should match this resource metadata (key=value) '
                 'additionally to the meter_name'))
def do_alarm_update(cc, args={}):
    '''Update an existing alarm.'''
    fields = dict(filter(lambda x: not (x[1] is None), vars(args).items()))
    fields = utils.args_array_to_dict(fields, "matching_metadata")
    fields.pop('alarm_id')
    try:
        alarm = cc.alarms.update(args.alarm_id, **fields)
    except exc.HTTPNotFound:
        raise exc.CommandError('Alarm not found: %s' % args.alarm_id)
    _display_alarm(alarm)


@utils.arg('-a', '--alarm_id', metavar='<ALARM_ID>', required=True,
           help='ID of the alarm to update.')
@common_alarm_arguments()
@utils.arg('--meter-name', metavar='<METRIC>',
           dest='threshold_rule/meter_name',
           help='Metric to evaluate against')
@utils.arg('--period', type=int, metavar='<PERIOD>',
           dest='threshold_rule/period',
           help='Length of each period (seconds) to evaluate over')
@utils.arg('--evaluation-periods', type=int, metavar='<COUNT>',
           dest='threshold_rule/evaluation_periods',
           help='Number of periods to evaluate over')
@utils.arg('--statistic', metavar='<STATISTIC>',
           dest='threshold_rule/statistic',
           help='Statistic to evaluate, one of: ' + str(STATISTICS))
@utils.arg('--comparison-operator', metavar='<OPERATOR>',
           dest='threshold_rule/comparison_operator',
           help='Operator to compare with, one of: ' + str(ALARM_OPERATORS))
@utils.arg('--threshold', type=float, metavar='<THRESHOLD>',
           dest='threshold_rule/threshold',
           help='Threshold to evaluate against')
@utils.arg('-q', '--query', metavar='<QUERY>',
           dest='threshold_rule/query',
           help='The query to find the data for computing statistics '
           '(key[op]value; list.)')
def do_alarm_threshold_update(cc, args={}):
    '''Update an existing alarm based on computed statistics.'''
    fields = dict(filter(lambda x: not (x[1] is None), vars(args).items()))
    fields = utils.key_with_slash_to_nested_dict(fields)
    fields.pop('alarm_id')
    fields['type'] = 'threshold'
    if 'query' in fields['threshold_rule']:
        fields['threshold_rule']['query'] = options.cli_to_array(
            fields['threshold_rule']['query'])
    try:
        alarm = cc.alarms.update(args.alarm_id, **fields)
    except exc.HTTPNotFound:
        raise exc.CommandError('Alarm not found: %s' % args.alarm_id)
    _display_alarm(alarm)


@utils.arg('-a', '--alarm_id', metavar='<ALARM_ID>', required=True,
           help='ID of the alarm to update.')
@common_alarm_arguments()
@utils.arg('--alarm_ids', action='append', metavar='<ALARM IDS>',
           dest='combination_rule/alarm_ids',
           help='List of alarm id')
@utils.arg('---operator', metavar='<OPERATOR>',
           dest='combination_rule/operator',
           help='Operator to compare with, one of: ' + str(
               ALARM_COMBINATION_OPERATORS))
def do_alarm_combination_update(cc, args={}):
    '''Update an existing alarm based on state of other alarms.'''
    fields = dict(filter(lambda x: not (x[1] is None), vars(args).items()))
    fields = utils.key_with_slash_to_nested_dict(fields)
    fields.pop('alarm_id')
    fields['type'] = 'combination'
    try:
        alarm = cc.alarms.update(args.alarm_id, **fields)
    except exc.HTTPNotFound:
        raise exc.CommandError('Alarm not found: %s' % args.alarm_id)
    _display_alarm(alarm)


@utils.arg('-a', '--alarm_id', metavar='<ALARM_ID>', required=True,
           help='ID of the alarm to delete.')
def do_alarm_delete(cc, args={}):
    '''Delete an alarm.'''
    try:
        cc.alarms.delete(args.alarm_id)
    except exc.HTTPNotFound:
        raise exc.CommandError('Alarm not found: %s' % args.alarm_id)


@utils.arg('-a', '--alarm_id', metavar='<ALARM_ID>', required=True,
           help='ID of the alarm state to set.')
@utils.arg('--state', metavar='<STATE>', required=True,
           help='State of the alarm, one of: ' + str(ALARM_STATES))
def do_alarm_state_set(cc, args={}):
    '''Set the state of an alarm.'''
    try:
        state = cc.alarms.set_state(args.alarm_id, args.state)
    except exc.HTTPNotFound:
        raise exc.CommandError('Alarm not found: %s' % args.alarm_id)
    utils.print_dict({'state': state}, wrap=72)


@utils.arg('-a', '--alarm_id', metavar='<ALARM_ID>', required=True,
           help='ID of the alarm state to show.')
def do_alarm_state_get(cc, args={}):
    '''Get the state of an alarm.'''
    try:
        state = cc.alarms.get_state(args.alarm_id)
    except exc.HTTPNotFound:
        raise exc.CommandError('Alarm not found: %s' % args.alarm_id)
    utils.print_dict({'state': state}, wrap=72)


@utils.arg('-a', '--alarm_id', metavar='<ALARM_ID>', required=True,
           help='ID of the alarm for which history is shown.')
@utils.arg('-q', '--query', metavar='<QUERY>',
           help='key[op]value; list.')
def do_alarm_history(cc, args={}):
    '''Display the change history of an alarm.'''
    kwargs = dict(alarm_id=args.alarm_id,
                  q=options.cli_to_array(args.query))
    try:
        history = cc.alarms.get_history(**kwargs)
    except exc.HTTPNotFound:
        raise exc.CommandError('Alarm not found: %s' % args.alarm_id)
    field_labels = ['Type', 'Timestamp', 'Detail']
    fields = ['type', 'timestamp', 'detail']
    utils.print_list(history, fields, field_labels,
                     formatters={'detail': alarm_change_detail_formatter},
                     sortby=1)


@utils.arg('-q', '--query', metavar='<QUERY>',
           help='key[op]value; list.')
def do_resource_list(cc, args={}):
    '''List the resources.'''
    resources = cc.resources.list(q=options.cli_to_array(args.query))

    field_labels = ['Resource ID', 'Source', 'User ID', 'Project ID']
    fields = ['resource_id', 'source', 'user_id', 'project_id']
    utils.print_list(resources, fields, field_labels,
                     sortby=1)


@utils.arg('-r', '--resource_id', metavar='<RESOURCE_ID>', required=True,
           help='ID of the resource to show.')
def do_resource_show(cc, args={}):
    '''Show the resource.'''
    try:
        resource = cc.resources.get(args.resource_id)
    except exc.HTTPNotFound:
        raise exc.CommandError('Resource not found: %s' % args.resource_id)
    else:
        fields = ['resource_id', 'source', 'user_id',
                  'project_id', 'metadata']
        data = dict([(f, getattr(resource, f, '')) for f in fields])
        utils.print_dict(data, wrap=72)
