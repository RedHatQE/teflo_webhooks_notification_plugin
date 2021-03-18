# User Guide

### To return to documentation home page press [here](https://redhatqe.github.io/teflo_webhooks_notification_plugin/index.html).

## Installation

### Before Install
In order to use this plugin, user has to setup webhooks for the applications which teflo will send 
notifications to. Please take a look at links below on how you can set up the webhooks for the chat applications 
[slack](https://api.slack.com/messaging/webhooks) and
[gchat](https://developers.google.com/hangouts/chat/how-tos/webhooks)

**Note** 

This plugin is supported only with Python 3

### Install
To install the plugin you can use pip. 

```bash
$ pip install teflo_webhooks_notification_plugin=<tagged_version>
```

OR

```bash
$ pip install https://github.com/RedHatQE/teflo_webhooks_notification_plugin.git@<tagged_version>
```

## Credentials
In teflo.cfg, users will need to provide the webhook url under the credential section as below:

```ini
[credentials:webhook]
gchat_url=https://abc.com
slack_url=https://pqr.com

```

User can provide an username and password if the webhook requires authentication. 
Webhook plugin supports basic authorization

```ini
[credentials:webhook]
webhook_url=https://abc.com
username=<username>
password=<password>

```

User can also provide custom message headers for their message, if the webhook supports them.
These headers have to be provided in a comma separated format with the keys and values as **key=val**

```ini
[credentials:webhook]
webhook_url=https://abc.com
username=<username>
password=<password>
message_headers=tenant=TEFLO-DEV,key1=val1

```

## Notification block under Teflo SDF
Within teflo scenario descriptor file (SDF) you can provide the notification block for webhooks as 
below:

```bash
notifications:
  - name: <name>
    notifier: slack-notifier/gchat-notifier
    credential: webhook
    on_tasks: ['provision']
    on_start: true / or any other teflo notification triggers
    message_body: <message>
    message_template: <path to template>

```

<table class="tg">
  <tr>
    <th class="tg-7un6">Key</th>
    <th class="tg-14gg">Description</th>
    <th class="tg-14gg">Type</th>
    <th class="tg-14gg">Required</th>
  </tr>
  <tr>
    <td class="tg-8m83">name</td>
    <td class="tg-8m83">name for the notification block<br><span style="font-style:italic">path - </span>relative path to the pinfile in the Teflo workspace. <br><span style="font-style:italic">targets -  </span>list of targets in pinfile<br></td>
    <td class="tg-8m83">String</td>
    <td class="tg-8m83">True</td>
  </tr>
  <tr>
    <td class="tg-14gg">notifier</td>
    <td class="tg-14gg">Plugin name</td>
    <td class="tg-14gg">String</td>
    <td class="tg-14gg">True(Valid values are slack-notifier, gchat-notifier, webhook-notifier)</td>
  </tr>
  <tr>
    <td class="tg-8m83">credential</td>
    <td class="tg-8m83"> webhook </td>
    <td class="tg-8m83">String</td>
    <td class="tg-8m83">True</td>
  </tr>
  <tr>
    <td class="tg-14gg">message_body</td>
    <td class="tg-14gg">Any message to be sent</span> key</td>
    <td class="tg-14gg">String</td>
    <td class="tg-14gg">False</td>
  </tr>
    <tr>
    <td class="tg-14gg">message_template</td>
    <td class="tg-14gg">A user defined template for notification.It is path of the template within the teflo workspace</span> key</td>
    <td class="tg-14gg">String</td>
    <td class="tg-14gg">False</td>
  </tr>
  </table>
  
  **Note**
  
  When user defined template is provided, user needs to make sure it matches the format required
  by the applictaion being used. To know how to create message formats please see these 
  [slack](https://api.slack.com/messaging/webhooks#advanced_message_formatting) 
  and [gchat](https://developers.google.com/hangouts/chat/concepts/cards)
  
  **Note**
  
  When user defined template is provided, Teflo makes its scenario object available for users to be
  able to use teflo's scenario information in their templates. The key is **'scenario'**
  User can take a look at Teflo's [notification resource](https://teflo.readthedocs.io/en/latest/users/definitions/notifications.html) 
  and [scenario resource](https://teflo.readthedocs.io/en/latest/users/scenario_descriptor.html)
  to get an idea of how to access some of the attributes from Teflo's internal resource objects to create message templates
  
### Example
  
```yaml
notifications:
  - name: msg_template
    notifier: slack-notifier
    credential: webhook
    on_start: true
    message_template: user_template.txt
```
In the above example, the `user_template.txt` could use teflo's scenario object as below:

To get scenario name and passed/failed tasks

```json
{% raw %}
{
    "blocks": [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Teflo Notification On_start trigger : Scenario Name : {{ scenario.name }}"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Task Started* : {{ passed_tasks }} "
                }

            ]
        }

    ]
}
{% endraw %}
```

OR

To get the execute task information and the testrun results for each execute task

```bash
{% raw %}
{
    "blocks": [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Teflo Notification : Scenario Name : {{ scenario.name }}"
            }
        },
        {
            "type": "divider"
        },

        {
            "type": "section",
            "fields": [
                {% if scenario.executes %}
                    {% for execute in scenario.executes %}
                        {
                        "type": "mrkdwn",
                        "text": "*Execute task :* {{ execute.name }} "
                        },
                        {% if execute.testrun_results %}
                            {
                                "type": "mrkdwn",
                                "text": """\n> *Testrun Results* \n>
                                           *Total Tests:* {{ execute.testrun_results.aggregate_testrun_results.total_tests }} \n>
                                           *Passed Tests:* {{ execute.testrun_results.aggregate_testrun_results.passed_tests }} \n>
                                           *Failed Tests:* {{ execute.testrun_results.aggregate_testrun_results.failed_tests }} \n>
                                           *Skipped Tests:* {{ execute.testrun_results.aggregate_testrun_results.skipped_tests }}"""

                            }
                        {% if not loop.last  %}
                        ,
                        {% endif %}
                        {% else %}
                            {
                                    "type": "mrkdwn",
                                    "text": "No test run results generated for this execute task"
                            }
                        {% endif %}

                    {% endfor %}

                {% else %}
                {
                    "type": "mrkdwn",
                    "text": "*Execute task:* No execute tasks were run"
                }
                {% endif %}
            ]
        }
        
    ]
}
{% endraw %}

```

**Note**

The plugin currently supports webhooks for gchat and slack applications, but has a way for the user
to supply a webhook url for their required application to receive notifications, under **webhook_url** key in teflo.cfg
This will work better if the user then supplies the `message_body` or `message_template` which suits the webhook of that 
application. 

If the user template is not provided then teflo uses its generic json template for chat application which may or may
not suit the application being used. 

Here notifier to be used is **webhook_notifier**

```ini
[credentials:webhook]
webhook_url=https://generic_url.com

```

Below is the example of the generic template Teflo sends when `webhook_notifier` is used. Here the notification sent
comprises of the scenario name, the passed/failed tasks and the overall status.  Teflo uses teflo's scenario object 
to get this information
 
```bash
{% raw %}
{
    "text":
        {
            "header": "Teflo Notification ",
            "scenario": " {{ scenario.name }} ",
            "overall status": {% if scenario.overall_status == 0 %}"Passed"{% else %}"Failed"{% endif %},
            "Tasks": {% if not passed_tasks and not failed_tasks %} "No tasks were executed."{% else %} 
                     {% if passed_tasks %}"Passed: {{ passed_tasks }}"{% endif %}{% if failed_tasks %}"Failed: {{ failed_tasks }}"
                     {% endif %}{% endif %}

        }
}
{% endraw %}

```

## Examples

### Example 1

To use slack-notifier to send notification after provisioning task is completed with
user defined custom message instead of provision task you can use other tasks (validate/execute/orchestrate/report)

```yaml
notifications:
  - name: msg_template
    notifier: gchat-notifier
    credential: webhook
    on_task: ['provision']
    message_body: "Provsision task completed" 
```  


### Example 2

To use gchat-notifier to send notification with trigger `on_start` using user defined template.

```yaml
notifications:
  - name: msg_template
    notifier: gchat-notifier
    credential: webhook
    on_start: true
    message_template: user_template.txt
```


### Example 3

To use slack-notifier to send notification without specifiying any `message_body` or `message_template`.
Here Teflo then sends out a default templated message, when a failure occurs.

```yaml
notifications:
  - name: msg1
    notifier: gchat-notifier
    credential: webhook
    on_failure: true
```  


**Note**

In all the examples above you can use gchat-notifier instead of slack-notifier to send the 
notifications to gchat and vice versa. The thing that will change is you will need adjust the 
format for the message that gchat/slack accepts and will have to provide `gchat_url/slack_url`
in the credentials:webhook section of teflo.cfg.

### Example 4

To use generic webhook-notifier to send notification to chat application other than slack or gchat.

```yaml
notifications:
  - name: msg1
    notifier: webhook-notifier
    credential: webhook
    on_failure: true
    message_template: differnt_chat_app_template.jinja
```    
    
### Example 5

To use generic webhook-notifier to send notification to chat application other than slack or gchat without providing
the user template. Here teflo will send out its own json template.

```yaml
notifications:
  - name: msg1
    notifier: webhook-notifier
    credential: webhook
    on_failure: true
```
