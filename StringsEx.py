import re
import argparse


def AsciiExtractor(buffer, n, f):
    asciiDict = {}
    if (f == True):
        asciiPattern = rb"([%s]{%d,1})" % (Chars, n)
    else:
        asciiPattern = rb"([%s]{%d,})" % (Chars, n)
    asciiRegex = re.compile(asciiPattern)
    for item in asciiRegex.finditer(buffer):
        asciiDict[item.start()] = item.group().decode("ascii")
    return asciiDict


def UnicodeExtractor(buffer, n, f):
    unicodeDict = {}
    if (f == True):
        unicodePattern = rb"((?:[%s]\x00){%d,1})" % (Chars, n)
    else:
        unicodePattern = rb"((?:[%s]\x00){%d,})" % (Chars, n)
    unicoderegex = re.compile(unicodePattern)
    for item in unicoderegex.finditer(buffer):
        try:
            unicodeDict[item.start()] = item.group().decode("utf-16")
        except UnicodeDecodeError:
            pass
    return unicodeDict


def MergeString():
    asciiDict = AsciiExtractor(buffer, 1, True)
    unicodeDict = UnicodeExtractor(buffer, 1, True)
    asciiStrings = "".join(list(asciiDict.values()))
    unicodeStrings = "".join(list(unicodeDict.values()))
    return asciiStrings, unicodeStrings, asciiDict, unicodeDict


def StringFinder(asciiStrings, unicodeStrings, asciiDict, unicodeDict, string):
    stringsList = list(FindAll(asciiStrings, string))
    if (len(stringsList) != 0):
        for item in stringsList:
            dictIndex = list(asciiDict.keys())[item]
            Print(dictIndex, "A", string)
    stringsList = list(FindAll(unicodeStrings, string))
    if (len(stringsList) != 0):
        for item in stringsList:
            dictIndex = list(unicodeDict.keys())[item]
            Print(dictIndex, "U", string)


def RegexFinder(asciiStrings, unicodeStrings, asciiDict, unicodeDict, regex):
    regex = r"%s" % (regex)
    for item in re.finditer(regex, asciiStrings, re.IGNORECASE):
        startIndex = list(asciiDict.keys())[item.start()]
        Print(startIndex, "A", str(item.group()))
    for item in re.finditer(regex, unicodeStrings, re.IGNORECASE):
        startIndex = list(unicodeDict.keys())[item.start()]
        Print(startIndex, "U", str(item.group()))


def InputList(listPath, stringType):
    asciiStrings, unicodeStrings, asciiDict, unicodeDict = MergeString()
    try:
        with open(listPath) as inputList:
            for item in inputList:
                item = item.strip()
                if (stringType == "string"):
                    StringFinder(asciiStrings, unicodeStrings,
                                asciiDict, unicodeDict, item)
                elif (stringType == "regex"):
                    RegexFinder(asciiStrings, unicodeStrings,
                                asciiDict, unicodeDict, item)
    except:
        print("\n\nInvalid List!\n\n")
        parser.print_help()
        exit()


def FindAll(strings, string):
    startIndex = 0
    while True:
        startIndex = strings.find(string, startIndex)
        if startIndex == -1:
            return
        yield startIndex
        startIndex += len(string)


def Print(offset, type, string):
    stringLength = len(string)
    print("0x%-8x  %-4d  %-4s  %s" % (offset, stringLength, type, string))


parser = argparse.ArgumentParser(
    prog='StringEx.py', usage="%(prog)s [FilePath] [options]", description='Display printable strings in a file with different methods')

parser.add_argument('FilePath', type=str)
parser.add_argument('-n', '--count', metavar="", type=int,
                    help="The minimum number of character sequences in simple mode (default value is 3)")
parser.add_argument('-s', '--string', metavar="", type=str,
                    help="Display the location of a specific string if it exists")
parser.add_argument('-r', '--regex', metavar="", type=str,
                    help="Display the location of a specific regular expression pattern if it exists")
parser.add_argument('-sl', '--string-list', metavar="",
                    type=str, help="Read strings from a list and display the location of them if they exist")
parser.add_argument('-rl', '--regex-list', metavar="",
                    type=str, help="Read regular expression patterns from a list and display the location of them if they exist")
args = parser.parse_args()

Chars = rb" !\"#\$%&\'\(\)\*\+,-\./0123456789:;<=>\?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\[\]\^_`abcdefghijklmnopqrstuvwxyz\{\|\}\\\~\t"

try:
    inputFile = open(args.FilePath, "rb")
    buffer = inputFile.read()
except FileNotFoundError:
    print("\n\nFile Not Found!\n\n")
    parser.print_help()
    exit()

if (args.FilePath and args.count):
    asciiDict = AsciiExtractor(buffer, args.count, False)
    for item in asciiDict:
        Print(item, "A", asciiDict[item])
    unicodeDict = UnicodeExtractor(buffer, args.count, False)
    for item in unicodeDict:
        Print(item, "U", unicodeDict[item])
elif (args.FilePath and args.string):
    asciiStrings, unicodeStrings, asciiDict, unicodeDict = MergeString()
    StringFinder(asciiStrings, unicodeStrings,
                asciiDict, unicodeDict, args.string)
elif (args.FilePath and args.regex):
    asciiStrings, unicodeStrings, asciiDict, unicodeDict = MergeString()
    RegexFinder(asciiStrings, unicodeStrings,
                asciiDict, unicodeDict, args.regex)
elif (args.FilePath and args.string_list):
    InputList(args.string_list, "string")
elif (args.FilePath and args.regex_list):
    InputList(args.regex_list, "regex")
elif (args.FilePath):
    asciiDict = AsciiExtractor(buffer, 3, False)
    for item in asciiDict:
        Print(item, "A", asciiDict[item])
    unicodeDict = UnicodeExtractor(buffer, 3, False)
    for item in unicodeDict:
        Print(item, "U", unicodeDict[item])
else:
    print("\n\nInvalid Argument!\n\n")
    parser.print_help()
    exit()