# -*- encoding: utf-8 -*-
""" App entry point. """
from malscan.settings import Settings
from malscan.help import Help
from malscan.error import Error

from sys import argv as Argv
from os import path, getcwd


class Malscan():
    """ Malscan is an app object that allows us
    to run various malscan commands """

    def __init__(self):
        self.settings = Settings()
        self.settings.load()

        self.arguments = Argv
        self.argument_count = len(self.arguments)
        self.help = Help()

    def load(self):
        # Making sure that we've received the appropriate number of arguments
        if self.argument_count > 1:
            # Removing the self-referencing argument
            del self.arguments[0]

            # If there's only 1 argument we're likely running a command
            if self.argument_count == 2:
                command = self.arguments[0]

                # There's one single command, so we verify it's not a target.
                if path.exists(command):
                    # User didn't pass a scan type, we're going to set -s
                    self.arguments.append(self.arguments[0])
                    self.arguments[0] = '-s'
                    self._run_scanner()
                else:
                    # Determining which non-scan command we're running
                    if 'update' in command:
                        from malscan.core.update import Update
                        updater = Update()
                        updater.run()
                    elif 'version' in command:
                        self.help.version()
                    elif 'settings' in command:
                        self.settings.show()
                    else:
                        self.help.display(self.settings.get('last_db_update'))
            else:
                # Two arguments usually indicates a target
                self._run_scanner()
        else:
            self.help.display(self.settings.get('last_db_update'))

    def _run_scanner(self):
        """ Configures the scanning instance and invokes the scanner """
        self.targets = []
        self.scan_modes = []
        for arg in self.arguments:
            if arg.startswith("-"):
                for opt in arg:
                    if opt in self.settings.optargs:
                        self.scan_modes.append(self.settings.optargs[opt])
            else:
                self._add_target(arg)
        if self.targets == []:
            self._add_target(getcwd())
        print('We are going to be running scans on:')
        print('    ' + '\n    '.join(self.targets))
        print('Scan types:')
        print('    ' + '\n    '.join(self.scan_modes))

    def _check_target(self, target):
        """ Determines if a string is a valid target for scanning """
        if path.exists(target):
            return True
        else:
            return False

    def _add_target(self, target):
        """ Adds a target to the target list, if it is a valid target """
        if self._check_target(target):
            self.targets.append(target)
        else:
            # The target doesn't exist, so we're going to error here.
            exception = Error()
            exception.error('The specified target "{}"'
                            ' does not exist.'.format(target))
