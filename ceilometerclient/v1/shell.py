# Copyright 2012 OpenStack LLC.
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

import json

from ceilometerclient.common import utils
import ceilometerclient.exc as exc


@utils.arg('-s', '--source', metavar='<SOURCE>',
           help='ID of the resource to show events for.')
@utils.arg('-r', '--resource_id', metavar='<RESOURCE_ID>',
           help='ID of the resource to show events for.')
@utils.arg('-u', '--user_id', metavar='<USER_ID>',
           help='ID of the user to show events for.')
@utils.arg('-p', '--project_id', metavar='<PROJECT_ID>',
           help='ID of the project to show events for.')
@utils.arg('-c', '--counter_name', metavar='<NAME>',
           help='Name of meter to show events for.')
def do_event_list(cc, args):
    '''List the events for this meters'''
    fields = {'counter_name': args.counter_name,
              'resource_id': args.resource_id,
              'user_id': args.user_id,
              'project_id': args.project_id,
              'source': args.source}
    try:
        events = cc.events.list(**fields)
    except exc.HTTPNotFound:
        raise exc.CommandError('Events not found: %s' % args.counter_name)
    else:
        json_format = lambda js: json.dumps(js, indent=2)
        formatters = {
            'metadata': json_format,
        }
        for e in events:
            utils.print_dict(e.to_dict(), formatters=formatters)


@utils.arg('-s', '--source', metavar='<SOURCE>',
           help='ID of the resource to show events for.')
@utils.arg('-r', '--resource_id', metavar='<RESOURCE_ID>',
           help='ID of the resource to show events for.')
@utils.arg('-u', '--user_id', metavar='<USER_ID>',
           help='ID of the user to show events for.')
@utils.arg('-p', '--project_id', metavar='<PROJECT_ID>',
           help='ID of the project to show events for.')
def do_metric_list(cc, args={}):
    '''List the user's metrices'''
    fields = {'resource_id': args.resource_id,
              'user_id': args.user_id,
              'project_id': args.project_id,
              'source': args.source}
    metrics = cc.meters.list(**fields)
    field_labels = ['Name', 'Resource ID', 'User ID']
    fields = ['counter_name', 'resource_id', 'user_id']
    utils.print_list(metrics, fields, field_labels,
                     sortby=0)


def do_user_list(cc, args={}):
    '''List the users'''
    kwargs = {}
    users = cc.users.list(**kwargs)
    field_labels = ['User ID']
    fields = ['user_id']
    utils.print_list(users, fields, field_labels,
                     sortby=0)


@utils.arg('-s', '--source', metavar='<SOURCE>',
           help='ID of the resource to show events for.')
@utils.arg('-u', '--user_id', metavar='<USER_ID>',
           help='ID of the user to show events for.')
def do_resource_list(cc, args={}):
    '''List the users'''
    kwargs = {'source': args.source,
              'user_id': args.user_id}
    resources = cc.resources.list(**kwargs)

    field_labels = ['Resource ID', 'Source', 'User ID', 'Project ID']
    fields = ['resource_id', 'source', 'user_id', 'project_id']
    utils.print_list(resources, fields, field_labels,
                     sortby=1)


@utils.arg('-s', '--source', metavar='<SOURCE>',
           help='ID of the resource to show events for.')
def do_project_list(cc, args={}):
    '''List the projects'''
    kwargs = {'source': args.source}
    projects = cc.projects.list(**kwargs)

    field_labels = ['Project ID']
    fields = ['project_id']
    utils.print_list(projects, fields, field_labels,
                     sortby=0)
