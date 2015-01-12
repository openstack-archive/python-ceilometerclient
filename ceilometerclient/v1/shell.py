# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
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
import ceilometerclient.exc as exc


@utils.arg('-m', '--metaquery', metavar='<METAQUERY>',
           help='Query into the metadata metadata.key=value:..')
@utils.arg('-s', '--source', metavar='<SOURCE>',
           help='ID of the resource to show samples for.')
@utils.arg('-r', '--resource_id', metavar='<RESOURCE_ID>',
           help='ID of the resource to show samples for.')
@utils.arg('-u', '--user_id', metavar='<USER_ID>',
           help='ID of the user to show samples for.')
@utils.arg('-p', '--project_id', metavar='<PROJECT_ID>',
           help='ID of the project to show samples for.')
@utils.arg('-c', '--counter_name', metavar='<NAME>',
           help='Name of meter to show samples for.')
@utils.arg('--start', metavar='<START_TIMESTAMP>',
           help='ISO date in UTC which limits events by '
           'timestamp >= this value')
@utils.arg('--end', metavar='<END_TIMESTAMP>',
           help='ISO date in UTC which limits events by '
           'timestamp <= this value')
def do_sample_list(cc, args):
    '''List the samples for this meters.'''
    fields = {'counter_name': args.counter_name,
              'resource_id': args.resource_id,
              'user_id': args.user_id,
              'project_id': args.project_id,
              'source': args.source,
              'start_timestamp': args.start,
              'end_timestamp': args.end,
              'metaquery': args.metaquery}
    try:
        samples = cc.samples.list(**fields)
    except exc.HTTPNotFound:
        raise exc.CommandError('Samples not found: %s' % args.counter_name)
    else:
        field_labels = ['Resource ID', 'Name', 'Type', 'Volume', 'Timestamp']
        fields = ['resource_id', 'counter_name', 'counter_type',
                  'counter_volume', 'timestamp']
        utils.print_list(samples, fields, field_labels,
                         sortby=0)


@utils.arg('-m', '--metaquery', metavar='<METAQUERY>',
           help='Query into the metadata metadata.key=value:..')
@utils.arg('-s', '--source', metavar='<SOURCE>',
           help='ID of the resource to show samples for.')
@utils.arg('-r', '--resource_id', metavar='<RESOURCE_ID>',
           help='ID of the resource to show samples for.')
@utils.arg('-u', '--user_id', metavar='<USER_ID>',
           help='ID of the user to show samples for.')
@utils.arg('-p', '--project_id', metavar='<PROJECT_ID>',
           help='ID of the project to show samples for.')
def do_meter_list(cc, args={}):
    '''List the user's meter.'''
    fields = {'resource_id': args.resource_id,
              'user_id': args.user_id,
              'project_id': args.project_id,
              'source': args.source}
    meters = cc.meters.list(**fields)
    field_labels = ['Name', 'Type', 'Resource ID', 'User ID', 'Project ID']
    fields = ['name', 'type', 'resource_id',
              'user_id', 'project_id']
    utils.print_list(meters, fields, field_labels,
                     sortby=0)


@utils.arg('-s', '--source', metavar='<SOURCE>',
           help='ID of the resource to show projects for.')
def do_user_list(cc, args={}):
    '''List the users.'''
    kwargs = {'source': args.source}
    users = cc.users.list(**kwargs)
    field_labels = ['User ID']
    fields = ['user_id']
    utils.print_list(users, fields, field_labels,
                     sortby=0)


@utils.arg('-s', '--source', metavar='<SOURCE>',
           help='ID of the resource to show for.')
@utils.arg('-u', '--user_id', metavar='<USER_ID>',
           help='ID of the user to show resources for.')
@utils.arg('-p', '--project_id', metavar='<PROJECT_ID>',
           help='ID of the project to show samples for.')
@utils.arg('-m', '--metaquery', metavar='<METAQUERY>',
           help='Query into the metadata metadata.key=value:..')
@utils.arg('--start', metavar='<START_TIMESTAMP>',
           help='ISO date in UTC which limits resouces by '
           'last update time >= this value')
@utils.arg('--end', metavar='<END_TIMESTAMP>',
           help='ISO date in UTC which limits resouces by '
           'last update time <= this value')
def do_resource_list(cc, args={}):
    """List the resources."""
    kwargs = {'source': args.source,
              'user_id': args.user_id,
              'project_id': args.project_id,
              'start_timestamp': args.start,
              'end_timestamp': args.end,
              'metaquery': args.metaquery}
    resources = cc.resources.list(**kwargs)

    field_labels = ['Resource ID', 'Source', 'User ID', 'Project ID']
    fields = ['resource_id', 'source', 'user_id', 'project_id']
    utils.print_list(resources, fields, field_labels,
                     sortby=1)


@utils.arg('-s', '--source', metavar='<SOURCE>',
           help='ID of the resource to show projects for.')
def do_project_list(cc, args={}):
    """List the projects."""
    kwargs = {'source': args.source}
    projects = cc.projects.list(**kwargs)

    field_labels = ['Project ID']
    fields = ['project_id']
    utils.print_list(projects, fields, field_labels,
                     sortby=0)
