import os
import re
from setuptools import setup, find_packages


ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([a-zA-Z0-9.]+)['"]''')


def get_version():
    init = open(os.path.join(ROOT, 'teflo_webhooks_notification_plugin', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


setup(
    name='teflo_webhooks_notification_plugin',
    version=get_version(),
    description="teflo's chat notifier for teflo notifications",
    long_description="""# teflo_webhooks_notification_plugin\n\n
                        * A notification plugin for Teflo to send notifications to gchat/slack using webhooks\n""",
    long_description_content_type='text/markdown',
    author="Red Hat Inc",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'httplib2'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'notification_plugins': [
            'webhook-notifier = teflo_webhooks_notification_plugin:WebhooksNotificationPlugin',
            'slack-notifier = teflo_webhooks_notification_plugin:SlackNotificationPlugin',
            'gchat-notifier = teflo_webhooks_notification_plugin:GchatNotificationPlugin',
            ]

    }
)
