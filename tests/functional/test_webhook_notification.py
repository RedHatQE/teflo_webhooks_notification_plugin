# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Red Hat, Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
    tests.test_webhooks_notification_plugin.py

    Unit tests for testing Webhook Notification Plugin.

    :copyright: (c) 2020 Red Hat, Inc.
    :license: GPLv3, see LICENSE for more details.
"""

import pytest
import mock
import os
from teflo_webhooks_notification_plugin.webhooks_notification_plugin import WebhooksNotificationPlugin, \
    SlackNotificationPlugin, GchatNotificationPlugin
from teflo.resources import Notification, Scenario
from teflo.exceptions import TefloNotifierError
from teflo.utils.config import Config
from teflo.utils.scenario_graph import ScenarioGraph
from termcolor import colored

@pytest.fixture()
def config():
    config_file = '../assets/teflo.cfg'
    os.environ['TEFLO_SETTINGS'] = config_file
    config = Config()
    config.load()
    return config

@pytest.fixture()
def scenario_resource(config):
    sc = Scenario(config=config, parameters={'name': 'test_scenario'})
    setattr(sc, 'passed_tasks', ['validate'])
    setattr(sc, 'failed_tasks', [])
    setattr(sc, 'overall_status', 0)
    return sc

@pytest.fixture()
def scenario_graph(scenario_resource):
    sg = ScenarioGraph(root_scenario=scenario_resource, scenario_vars= {'username': 'teflo_user'})
    return sg

@pytest.fixture()
def params():

    params = dict(
        description='description goes here.',
        notifier='webhook-notifier',
        credential='webhook_generic'
    )
    return params

@pytest.fixture()
def slack_params():

    params = dict(
        description='description goes here.',
        notifier='slack-notifier',
        on_start=True,
        credential='webhook'
    )
    return params

@pytest.fixture()
def gchat_params():

    params = dict(
        description='description goes here.',
        notifier='gchat-notifier',
        on_start=True,
        credential='webhook',
        message_template='user_temp.jinja'
    )
    return params

@pytest.fixture()
def notification(params, config, scenario_resource, scenario_graph):
    note = Notification(name='notify1', parameters=params,  config=getattr(scenario_resource, 'config'))
    setattr(scenario_resource, 'passed_tasks', ['provision'])
    setattr(scenario_resource, 'failed_tasks', [])
    setattr(scenario_resource, 'overall_status', 0)
    setattr(scenario_resource, 'scenario_graph', scenario_graph)
    scenario_resource.add_notifications(note)
    note.scenario = scenario_resource
    return note

@pytest.fixture()
def webhook_notification_plugin(notification):
    wb_plugin = WebhooksNotificationPlugin(notification)
    return wb_plugin


@pytest.fixture()
def slack_notification_plugin(scenario_resource, slack_params, scenario_graph):
    setattr(scenario_resource, 'passed_tasks', ['provision'])
    setattr(scenario_resource, 'failed_tasks', [])
    setattr(scenario_resource, 'overall_status', 0)
    setattr(scenario_resource, 'scenario_graph', scenario_graph)
    note = Notification(name='slack1', parameters=slack_params, config=getattr(scenario_resource, 'config'))
    scenario_resource.add_notifications(note)
    note.scenario = scenario_resource
    sl_plugin = SlackNotificationPlugin(note)
    return sl_plugin


@pytest.fixture()
def gc_notification_plugin(scenario_resource, gchat_params, scenario_graph):
    setattr(scenario_resource, 'passed_tasks', ['provision'])
    setattr(scenario_resource, 'failed_tasks', [])
    setattr(scenario_resource, 'overall_status', 0)
    setattr(scenario_resource, 'scenario_graph', scenario_graph)
    note = Notification(name='gchat1', parameters=gchat_params, config=getattr(scenario_resource, 'config'))
    scenario_resource.add_notifications(note)
    note.scenario = scenario_resource
    gc_plugin = GchatNotificationPlugin(note)
    return gc_plugin


class TestWebhookNotificationPlugin(object):

    @staticmethod
    def test_slack_plugin(scenario_resource, slack_params, scenario_graph):
        setattr(scenario_resource, 'scenario_graph', scenario_graph)
        note = Notification(name='slack1', parameters=slack_params, config=getattr(scenario_resource, 'config'))
        note.scenario = scenario_resource
        sl = SlackNotificationPlugin(note)
        assert isinstance(sl, WebhooksNotificationPlugin)

    @staticmethod
    def test_gchat_plugin(scenario_resource, gchat_params, scenario_graph):
        setattr(scenario_resource, 'scenario_graph', scenario_graph)
        note = Notification(name='gchat1', parameters=gchat_params, config=getattr(scenario_resource, 'config'))
        note.scenario = scenario_resource
        gc = GchatNotificationPlugin(note)
        assert isinstance(gc, WebhooksNotificationPlugin)

    @staticmethod
    def test_generic_webhook_plugin(notification):
        assert notification.notifier.__plugin_name__ == WebhooksNotificationPlugin.__plugin_name__

    @staticmethod
    @mock.patch('teflo_webhooks_notification_plugin.webhooks_notification_plugin.template_render')
    @mock.patch('httplib2.Http.request')
    def test_send_message_response_failure(mock_method2, mock_method1, slack_notification_plugin):
        """To test send message method fails when status is anything other than 200"""
        mock_method1.return_value = str({"text": "hello"})
        mock_method2.return_value = ({'status':'503'}, 'Service Unavailable')
        with pytest.raises(TefloNotifierError):
            slack_notification_plugin.notify()

    @staticmethod
    @mock.patch('teflo_webhooks_notification_plugin.webhooks_notification_plugin.template_render')
    @mock.patch('httplib2.Http.request')
    def test_send_message_method_httplib2_failure(mock2, mock1, slack_notification_plugin):
        """To test send message method fails when exception occurs"""
        mock1.return_value = '{"text": "hello"}'
        mock2.side_effect = Exception('Mock httplib2 Failure')
        with pytest.raises(Exception):
            slack_notification_plugin.send_message()

    @staticmethod
    @mock.patch('teflo_webhooks_notification_plugin.webhooks_notification_plugin.template_render')
    @mock.patch('httplib2.Http.request')
    def test_notify_method(mock_method2, mock_method1, slack_notification_plugin):
        """To test notify method with no body and no template on start"""
        mock_method1.return_value = str({'text': 'teflo_notification'})
        mock_method2.return_value = ({'status':'200'},)
        slack_notification_plugin.notify()
        assert slack_notification_plugin.body == str({'text': 'teflo_notification'})

    @staticmethod
    @mock.patch('httplib2.Http.request')
    def test_notify_method_with_user_template(mock_method, gc_notification_plugin):
        """To test notify method with no body and user template is provided"""
        os.system('cp ../assets/user_temp.jinja /tmp/')

        mock_method.return_value = ({'status': '200'},)
        gc_notification_plugin.notify()
        assert gc_notification_plugin.body == '{"text": "hello teflo_user "}'
        os.system('rm /tmp/user_temp.jinja')

    @staticmethod
    def test_with_no_auth_header_no_custom_header(gc_notification_plugin):
        """To test when no custom headers or username/pass are provided message_headers is created correctly"""
        op = gc_notification_plugin.get_message_headers()
        assert isinstance(op, dict)
        assert 'Authorization' not in op.keys()
        assert len(op) == 1


    @staticmethod
    def test_with_auth_header_and_custom_header(webhook_notification_plugin):
        """To test when custom headers or username/pass are provided message_headers is created correctly"""
        op = webhook_notification_plugin.get_message_headers()
        assert isinstance(op, dict)
        assert 'tenant' in op.keys()
        assert 'Authorization' in op.keys()

    @staticmethod
    def test_with_incorrect_message_header_format(webhook_notification_plugin):
        """To test when message_headers is given in the incorrect format in teflo.cfg"""
        webhook_notification_plugin.webhook_headers = 'tenant'
        with pytest.raises(TefloNotifierError) as ex:
            webhook_notification_plugin.get_message_headers()
        assert colored("The value for message headers need to be in a comma separated string with "
                       "keys and values separated by '=' e.g. message_headers=key1=val1,key2=val2", "red") \
               in ex.value.args
