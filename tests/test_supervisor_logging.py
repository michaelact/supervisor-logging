#
# Copyright 2014  Infoxchange Australia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test supervisor_logging.
"""

import os
import SocketServer as socketserver
import subprocess
import threading

from time import sleep

from unittest import TestCase


class SupervisorLoggingTestCase(TestCase):
    """
    Test logging.
    """

    def test_logging(self):
        """
        Test logging.
        """

        messages = []

        class SyslogHandler(socketserver.BaseRequestHandler):
            """
            Save received messages.
            """

            def handle(self):
                messages.append(self.request[0].strip().decode())

        syslog = socketserver.UDPServer(('0.0.0.0', 0), SyslogHandler)
        try:
            threading.Thread(target=syslog.serve_forever).start()

            os.environ['SYSLOG_HOST'] = syslog.server_address[0]
            os.environ['SYSLOG_PORT'] = str(syslog.server_address[1])
            os.environ['SYSLOG_PROTO'] = 'udp'

            mydir = os.path.dirname(__file__)

            os.environ['PATH'] = mydir + ':' + os.environ['PATH']
            supervisor = subprocess.Popen([
                'supervisord',
                '-c',
                os.path.join(mydir, 'supervisord.conf')
            ])
            try:

                sleep(10)

                self.assertEqual(
                    messages,
                    [
                        'test message',
                    ]
                )
            finally:
                supervisor.terminate()

        finally:
            syslog.shutdown()