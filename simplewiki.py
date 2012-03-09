import re



EXAMPLE_WIKI_TEXT = """
  = Header 1 =

  Some text '''and some bold text'''

  === Header 3 ===

  Other text ___and underlined text___
  
  Link to google shwoing link URL [[http://google.com]] 

  Link to google with  [[http://google.com custom text]]  
    
 - a list element
 # another list element
   - a sublist element
   
And here an horizontal line
----

    """



def HeaderReplace(text):
    htmlTmp = text
    for i in [6, 5, 4, 3, 2, 1]:
        html = ''
        for line in htmlTmp.split("\n"):
            html += re.sub("^(\s*)" + "="*i + "(.+?)" + "="*i + "(\s*)$", \
                           "\\1<h%d>\\2</h%d>\\3" % (i, i), \
                           line) + "\n"
        htmlTmp = html.rstrip("\n")
    return html.rstrip("\n")

def BoldReplace(text):
    return re.sub("(^|[^'])'''(.+?)'''($|[^'])", "\\1<b>\\2</b>\\3", text)

def UnderlineReplace(text):
    return re.sub("([^_]|^)___(.+?)___([^_]|$)", "\\1<u>\\2</u>\\3", text)

def LineReplace(text):
    # 4 or more consecutive '-'
    return re.sub("(.*)-----*(.*)", "\\1<hr/>\\2", text)

def LineBreakReplace(text):
    html = ''
    for line in text.split("\n"):
        if re.match("^\s*$", line):
            html += "<br/>\n"
        else:
            html += line + "\n"
    return html.rstrip().replace("__br", "<br/>")

def LinkReplace(text):
    html = ''
    copyFrom = 0
    linkRe = re.compile("\[\[(.+?)\]\]")
    reMatch = linkRe.search(text)
    while reMatch:
        html += text[copyFrom:reMatch.start()]
        linkData = reMatch.group(1).strip().split(" ")
        linkUrl = linkData[0]
        linkText = ''
        if len(linkData) > 1:
            i = 1
            while i < len(linkData):
                linkText += linkData[i]
                i += 1
        else:
            linkText = linkUrl
        html += "<a href=\"%s\">%s</a>" % (linkUrl.strip(), linkText.strip())
        copyFrom = reMatch.end()+1
        reMatch = linkRe.search(text, copyFrom)
    html += text[copyFrom:]
    return html

def ListReplace(text):
    lines = text.split("\n")
    lineBlock = []
    blocks = {}
    currBlock = i = 0
    inBlock = False
    while i<len(lines):
        if inBlock:
            if re.match("^\s* ([#\*-]) ", lines[i]):
                blocks[currBlock].append((i, CountSpacesAtBeginning(lines[i])))
                lineBlock.append(currBlock)
            else:
                inBlock = False
                currBlock += 1
                lineBlock.append(-1)
        else:
            if re.match("^\s* ([#\*-]) ", lines[i]):
                inBlock = True
                blocks[currBlock] = [(i, CountSpacesAtBeginning(lines[i]))]
                lineBlock.append(currBlock)
            else:
                lineBlock.append(-1)
        i += 1
    
    blocksHtml = {}
    for currBlock, blockLines in blocks.iteritems():
        blocksHtml[currBlock] = ""
        ulOpen = 0
        currLevel = -1

        for i, level in blockLines:
            if level > currLevel:
                blocksHtml[currBlock] += "<ul>\n"
                ulOpen += 1
            if level < currLevel and ulOpen > 0:
                blocksHtml[currBlock] += "</ul>\n"
                ulOpen -= 1
            currLevel = level
            blocksHtml[currBlock] += re.sub("^(\s*) [#\*-] (.*)", "\\1<li>\\2</li>\n", lines[i])

        while ulOpen > 0:
            blocksHtml[currBlock] += "</ul>\n"
            ulOpen -= 1
    
    html = ''
    i = 0
    currBlock = -1
    while i<len(lines):
        if lineBlock[i] == -1:
            html += lines[i] + "\n"
        else:
            if currBlock != lineBlock[i]:
                currBlock = lineBlock[i]
                html += blocksHtml[currBlock]
        i += 1
    return html.rstrip()

def CountSpacesAtBeginning(text):
    i = 0
    while text[i] == " ":
        i += 1
    return i

def ParseWiki(text):
    text = HeaderReplace(text)
    text = ListReplace(text)
    text = UnderlineReplace(text)
    text = BoldReplace(text)
    text = LineBreakReplace(text)
    text = LineReplace(text)
    text = LinkReplace(text)
    return text

class NamopyWiki:
    def __init__(self):
        self.enableJavascript = False
        self.addBody          = False

    def Parse(self, text):
        html = ParseWiki(text)

        if not self.enableJavascript:
            html = html.replace("<script", "<!-- script -->").replace("</script>", "<!-- /script -->")

        if self.addBody:
            html = "<html><body>%s</body></html>" % html

        return html



if __name__ == "__main__":

    print "Testing simple wiki parsing with ParseWiki\n"
    print "------------------------------------------\n\n"

    print " *** Text string with wiki markup\n\n"

    print EXAMPLE_WIKI_TEXT

    print "_"*80 + "\n\n"

    print " *** HTML markup\n\n"

    print ParseWiki(EXAMPLE_WIKI_TEXT)
