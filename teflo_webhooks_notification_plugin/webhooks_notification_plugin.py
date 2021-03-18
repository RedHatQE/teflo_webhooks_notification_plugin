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

    Teflo's notification for gchat/slack via webhooks.

    :copyright: (c) 2020 Red Hat, Inc.
    :license: GPLv3, see LICENSE for more details.
"""
import os
import os.path
import base64
from json import dumps
from httplib2 import Http
from teflo.core import NotificationPlugin
from teflo.helpers import template_render, schema_validator, generate_default_template_vars
from teflo.exceptions import TefloNotifierError


class WebhooksNotificationPlugin(NotificationPlugin):

    __plugin_name__ = 'webhook-notifier'
    __schema_file_path__ = os.path.abspath(os.path.join(os.path.dirname(__file__), "files/schema.yml"))

    def __init__(self, notification):

        super(WebhooksNotificationPlugin, self).__init__(notification=notification)

        self.scenario = getattr(self.notification, 'scenario')
        self.config_params = self.get_config_params()
        self.creds_params = self.get_credential_params()
        self.body = getattr(self.notification, 'message_body', '')
        self.body_tmpl = getattr(self.notification, 'message_template', '')
        self.create_logger(name='teflo_webhooks_notification_plugin', data_folder=self.config.get('DATA_FOLDER'))
        self.url = self.creds_params.get('webhook_url', None)
        self.default_cbn_template = 'templates/generic_template.jinja'
        self.onstart_temp = 'templates/generic_template.jinja'
        self.username = self.creds_params.get('username', None)
        self.password = self.creds_params.get('password', None)
        self.webhook_headers = self.creds_params.get('message_headers', None)

    def get_message_headers(self):
        """ This method generates the message header that will be used to send message.
            The method looks for any custom message headers and basic authentication information.
             By default it will provide the header with 'Content-Type': 'application/json; charset=UTF-8' """
        msg_headers = {}

        # checking if any custom headers are provided and add them to message header dictionary
        if self.webhook_headers:
            if isinstance(self.webhook_headers, str):
                headers = self.webhook_headers.split(',')
                for item in headers:
                    if '=' in item:
                        key, val = item.split('=', 1)
                        msg_headers[key] = val
                    else:
                        raise TefloNotifierError("The value for message headers need to be in a comma separated string "
                                                 "with keys and values separated by '=' "
                                                 "e.g. message_headers=key1=val1,key2=val2")
            else:
                raise TefloNotifierError("The value for message headers need to be in a comma separated string "
                                         "with keys and values separated by '=' "
                                         "e.g. message_headers=key1=val1,key2=val2")

        # if webhooks have authorization information provided
        if self.username and self.password:
            credentials = base64.b64encode("{0}:{1}".format(self.username, self.password).encode('utf-8')).decode()
            msg_headers.update({'Authorization': "Basic %s" % credentials})

        msg_headers.update({'Content-Type': 'application/json; charset=UTF-8'})
        return msg_headers

    def send_message(self):
        bot_message = eval(self.body)
        self.logger.debug('The loaded message body is: ')
        self.logger.debug(bot_message)

        if not isinstance(bot_message, dict):
            raise TefloNotifierError("There was an issue with the message body format."
                                     "It needs to be a dictionary %s " % bot_message)

        http_obj = Http()
        try:
            response = http_obj.request(
                uri=self.url,
                method='POST',
                headers=self.get_message_headers(),
                body=dumps(bot_message)

            )
            self.logger.debug("Response : %s" % (response,))
        except Exception as e:
            raise TefloNotifierError("Error while communicating to the webhook : %s" % e)

        if int(response[0]['status']) != 200:
            raise TefloNotifierError("Error while creating the webhoook payload : %s" % response[1])
        else:
            self.logger.info("Notification Successful for %s " % self.__plugin_name__)

    def notify(self):
        """
        Implementation of the notify method for generating the
        notification and sending it to the webhook
        :return:
        """
        if not self.body and not self.body_tmpl:
            if getattr(self.notification, 'on_start'):
                self.logger.info("Using teflo's onstart webhook template")
                self.body = template_render(os.path.abspath(os.path.join(os.path.dirname(__file__), self.onstart_temp)),
                                            generate_default_template_vars(self.scenario, self.notification))
            else:
                self.logger.info("Using teflo's generic webhook template")
                self.body = template_render(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            self.default_cbn_template)),
                                            generate_default_template_vars(self.scenario, self.notification))
        elif not self.body and self.body_tmpl:
            self.logger.info('Using user provided webhook template')
            var_dict = dict()
            # Updating the the var_dict with scenario object to be used if needed by the user template
            var_dict.update(scenario=generate_default_template_vars(self.scenario, self.notification).get('scenario'))
            # Updating the the var_dict with environmental variables be used in the user template
            var_dict.update(os.environ)
            self.body = template_render(os.path.abspath(os.path.join(getattr(self.notification, 'workspace'),
                                        self.body_tmpl)), var_dict)
        elif self.body and not self.body_tmpl:
            self.logger.debug("Only message body is provided without any template")
            self.body = str({'text': self.body})

        if self.url:
            self.logger.info('Sending notification using %s' % self.__plugin_name__)
            self.send_message()
        else:
            raise TefloNotifierError('No url was set for the Webhook Notifier in the teflo.cfg.')

    def validate(self):

        schema_validator(schema_data=self.build_profile(self.notification),
                         schema_creds=self.creds_params,
                         schema_files=[self.__schema_file_path__])


class SlackNotificationPlugin(WebhooksNotificationPlugin):
    __plugin_name__ = 'slack-notifier'

    def __init__(self, notification):

        super(SlackNotificationPlugin, self).__init__(notification=notification)

        self.url = self.creds_params.get('slack_url', None)
        self.default_cbn_template = 'templates/slack_template.jinja'
        self.onstart_temp = 'templates/slack_onstart_template.jinja'


class GchatNotificationPlugin(WebhooksNotificationPlugin):
    __plugin_name__ = 'gchat-notifier'

    def __init__(self, notification):

        super(GchatNotificationPlugin, self).__init__(notification=notification)

        self.url = self.creds_params.get('gchat_url', None)
        self.default_cbn_template = 'templates/gchat_template.jinja'
        self.onstart_temp = 'templates/gchat_onstart_template.jinja'
