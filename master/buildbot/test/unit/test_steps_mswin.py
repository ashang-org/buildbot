# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

from buildbot.status.results import SUCCESS, FAILURE, WARNINGS
from buildbot.steps import mswin
from buildbot.test.fake.remotecommand import ExpectShell
from buildbot.test.util import steps
from twisted.trial import unittest
from buildbot.process.properties import Property

from mock import Mock


class TestRobocopySimple(steps.BuildStepMixin, unittest.TestCase):
    """
    Test L{Robocopy} command building.
    """
    def setUp(self):
        return self.setUpBuildStep()

    def tearDown(self):
        return self.tearDownBuildStep()

    def _run_simple_test(self, source, destination, expected_args=None, expected_code=0, expected_res=SUCCESS, **kwargs):
        s = mswin.Robocopy(source, destination, **kwargs)
        self.setupStep(s)
        self.assertEqual(s.describe(), ['???'])
        self.assertEqual(s.describe(done=True), ['???'])

        command = ['robocopy', source, destination]
        if expected_args:
            command += expected_args
        command += ['/TEE', '/UNICODE', '/NP']
        self.expectCommands(
                ExpectShell(
                        workdir='wkdir',
                        command=command,
                        usePTY="slave-config"
                    )
                + expected_code
            )
        status_text = ["'robocopy", source, "...'"]
        if expected_res == WARNINGS:
            status_text.append('warnings')
        elif expected_res == FAILURE:
            status_text.append('failed')
        self.expectOutcome(result=expected_res, status_text=status_text)
        return self.runStep()

    def test_copy(self):
        self._run_simple_test('D:\source', 'E:\dest')

    def test_copy_files(self):
        self._run_simple_test(
                'D:\source', 'E:\dest', files=['a.txt', 'b.txt', '*.log'],
                expected_args=['a.txt', 'b.txt', '*.log']
            )

    def test_copy_recursive(self):
        self._run_simple_test(
                'D:\source', 'E:\dest', recursive=True,
                expected_args=['/E']
            )

    def test_mirror_files(self):
        self._run_simple_test(
                'D:\source', 'E:\dest', files=['*.foo'], mirror=True,
                expected_args=['*.foo', '/MIR']
            )

    def test_move_files(self):
        self._run_simple_test(
                'D:\source', 'E:\dest', files=['*.foo'], move=True,
                expected_args=['*.foo', '/MOVE']
            )

    def test_exclude(self):
        self._run_simple_test(
                'D:\source', 'E:\dest', files=['blah*'], exclude=['*.foo', '*.bar'],
                expected_args=['blah*', '/XF', '*.foo', '*.bar']
            )

    def test_codes(self):
        # Codes that mean uneventful copies (including no copy at all).
        for i in [0, 1]:
            self._run_simple_test(
                    'D:\source', 'E:\dest', expected_code=i,
                    expected_res=SUCCESS
                )

        # Codes that mean some mismatched or extra files were found.
        for i in range(2, 8):
            self._run_simple_test(
                    'D:\source', 'E:\dest', expected_code=i,
                    expected_res=WARNINGS
                )
        # Codes that mean errors have been encountered.
        for i in range(8, 32):
            self._run_simple_test(
                    'D:\source', 'E:\dest', expected_code=i,
                    expected_res=FAILURE
                )
