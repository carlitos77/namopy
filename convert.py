

import urllib2, os, base64, urllib
import xml.etree.ElementTree
import time

HOST="api.online-convert.com"
API_URL="/queue-insert"
API_STATUS_URL="/queue-status"
KEY="08a3dbe33f3e66daa2d7a958fee50b09"


class OnlineConverter:
    convertTo = "convert-to-png"
    testMode = "false"
    filePath = ''

    def SetResultJpg(self):
        self.convertTo = "convert-to-jpg"

    def SetResultPng(self):
        self.convertTo = "convert-to-png"

    def SetFile(self, filePath):
        self.filePath = filePath

    def SetTestMode(self, mode):
        self.testMode = "false"
        if mode:
            self.testMode = "true"

    def _conversionRequest(self):
        if not os.path.isfile(self.filePath):
            return False
        return """<?xml version="1.0" encoding="utf-8" ?>
<queue>
    <apiKey>%s</apiKey>
    <targetType>image</targetType>
    <targetMethod>%s</targetMethod>
    <testMode>%s</testMode>
    <file>
        <fileName>%s</fileName>
        <fileData>
            %s
        </fileData>
    </file>
</queue>""" % (KEY, self.convertTo, self.testMode, os.path.basename(self.filePath), base64.b64encode(open(self.filePath, "r").read()))

    def _statusRequest(self, hash):
        return """<?xml version="1.0" encoding="utf-8" ?>
<queue>
    <apiKey>%s</apiKey>
    <hash>%s</hash>
</queue>""" % (KEY, hash)

    def Convert(self, saveFile):
        xmlstr = self._conversionRequest()
        if xmlstr == False:
            return False
        req = urllib2.Request("http://" + HOST + API_URL, urllib.urlencode({"queue" : xmlstr}))
        res = urllib2.urlopen(req)
        xmlres = xml.etree.ElementTree.XML(res.read())
        hash = xmlres.find("params/hash").text

        code = i = 0
        while code != 100 and i < 5:
            if i > 0:
                time.sleep(2)
            req = urllib2.Request("http://" + HOST + API_STATUS_URL, urllib.urlencode({"queue" : self._statusRequest(hash)}))
            res = urllib2.urlopen(req)
            xmlres = xml.etree.ElementTree.XML(res.read())
            code = int(xmlres.find("status/code").text)
            i += 1
        if code == 0:
            return False
        urllib.urlretrieve(xmlres.find("params/directDownload").text, saveFile)
        
"""
        #localFile = open(saveFile, "w")
        #downloadUrl = xmlres.find("params/directDownload").text
        #req = urllib2.Request(downloadUrl)
        #web = urllib2.urlopen(req)
        #localFile.write(web.read())
        #localFile.close()

<queue-answer>
  <status>
    <code>104</code>
    <message>The file is currently being processed.</message>
  </status>
  <params>
    <hash>766d7faafb8d95a55b8c55b5d07c8bbc</hash>
  </params>
</queue-answer>




<queue-answer>
  <status>
    <code>100</code>
    <message>The file has been successfully converted.</message>
  </status>
  <params>
    <downloadCounter>0</downloadCounter>
    <dateProcessed>1329758242</dateProcessed>
    <directDownload>http://www2.online-convert.com/download-file/766d7faafb8d95a55b8c55b5d07c8bbc</directDownload>
    <checksum>ba543dbf3a4741574b67c598b124f20e</checksum>
    <target_size>154</target_size>
    <convert_to>png</convert_to>
    <mime_type>image/png</mime_type>
    <hash>766d7faafb8d95a55b8c55b5d07c8bbc</hash>
  </params>
</queue-answer>



"""

import sys


if len(sys.argv) != 3:
    print "convert <infile> <destfile.png>"
    sys.exit(1)

inFile = sys.argv[1]
if not os.path.isfile(inFile):
    print "no file found " + inFile
    sys.exit(1)

outFile = sys.argv[2]

c = OnlineConverter()
c.SetFile(inFile)

x = c.Convert(outFile)




