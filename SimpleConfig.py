

import re
import os


class SimpleConfig:
    """ FIXME documentation """

    def __init__(self):
        self.data = {}

    def Load(self, configRes):
        if os.path.isfile(configRes):
            return self.LoadFromFile(configRes)
        return self.LoadFromString(configRes)

    def LoadFromFile(self, filePath, overwrite=True):
        try:
            fileData = open(filePath).read()
        except IOError:
            return False
        return self.LoadFromString(fileData, overwrite)

    def LoadFromString(self, configString, overwrite=True):
        lines = configString.split("\n")

        readingMultiline = False
        valueName = value = None
        for line in lines:
            if readingMultiline:
                reMatch = re.search("^\s*<<<\s*" + valueName, line)
                if reMatch:
                    readingMultiline = False
                    if overwrite or valueName not in self.data:
                        self.data[valueName] = value
                else:
                    value += line + "\n"
                continue

            # single line values
            reMatch = re.search("^\s*([a-z][a-z_0-9]*)\s*=\s*(.*)$", line, re.I)
            if reMatch:
                valueName = reMatch.group(1)
                if overwrite or valueName not in self.data:
                    self.data[valueName] = reMatch.group(2)
                continue

            # multiline value 
            reMatch = re.search("^\s*([a-z][a-z_0-9]*)\s*<<<", line, re.I)
            if reMatch:
                valueName = reMatch.group(1)
                readingMultiline = True
                value = ''
        
        return True

    def IsValue(self, valueName):
        return valueName in self.data

    def Value(self, valueName):
        if not self.IsValue(valueName):
            raise Exception("Value not found " + valueName)
        return self.data[valueName]

    def AddValue(self, valueName, value, overwrite=True):
        if overwrite or not self.IsValue(valueName):
            self.data[valueName] = value
            return True
        return False

    def __getattr__(self, name):
        if name == "data":
            return self.data
        else:
            return self.Value(name)

if __name__ == "__main__":
    sc = SimpleConfig()
    if not sc.Load("test.cfg"):
        print "Config file error"

    import pprint

    pprint.pprint(sc.data)
