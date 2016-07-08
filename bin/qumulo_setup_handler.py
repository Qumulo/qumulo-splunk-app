"""
Custom Qumulo Setup Handler
"""
import os
import sys

import splunk
import splunk.admin
import splunk.entity

from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path


class ConfigHandler(splunk.admin.MConfigHandler):

    def setup(self):
        if self.requestedAction == splunk.admin.ACTION_EDIT:
            for arg in ['username', 'password','nodehost','port' ]:
                self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        confDict = self.readConf("inputs")
        if None != confDict:
            for stanza, settings in confDict.items():
                for key, val in settings.items():
                    if key in ['port'] and val in [None, '']:
                        val = 8000
                    confInfo[stanza].append(key, val)

    def handleEdit(self, confInfo):
        if self.callerArgs.data['port'][0] in [None, '']:
            self.callerArgs.data['port'][0] = 8000
        
        self.writeConf('inputs', 'qumulo', self.callerArgs.data)



def main():
    splunk.admin.init(ConfigHandler, splunk.admin.CONTEXT_NONE)


if __name__ == '__main__':

    main()
