import datetime
from pyparsing import (OneOrMore, oneOf, Keyword, White, restOfLine, ParseException, Optional, SkipTo, LineEnd, Or,
                       ZeroOrMore, Literal, Word, nums, alphas, Suppress, Group, alphanums, printables, delimitedList)

def integer(name):
    return Word(nums).setResultsName(name).setParseAction(lambda x: int(x.get(name)))


def safe(parsed, key, default=None):
    if key in parsed:
        return parsed[key]

    return default

word = Word(printables)
colon = Suppress(":")
whitespace = White().suppress()
minus = Suppress("-")

kind = (Keyword("TODO") | Keyword("DONE")).setResultsName("kind") + whitespace
level = OneOrMore("*").setParseAction(lambda x: len(x)).setResultsName("level")
tags = colon + delimitedList(Word(alphanums), delim=":").setResultsName("tags") + colon
text = ZeroOrMore(~tags + Word(printables)). \
    setParseAction(lambda x: " ".join(x["heading"])). \
    setResultsName("heading")
org_node = level + whitespace + Optional(kind) + text + Optional(tags)

start_properties = Literal(":PROPERTIES:").suppress() + restOfLine()
a_property = colon + Word(printables, excludeChars=":").setResultsName("key") + colon + restOfLine().setResultsName("value")
end_properties = Literal(":END:").suppress() + restOfLine()

_datetime = integer("year") + Suppress('-') + integer('month') + Suppress('-') + integer('day') + whitespace + \
    Word(alphas).suppress()
schedule = Optional((Keyword("SCHEDULED") | Keyword("DEADLINE"))).setResultsName("type")  + Literal(":").suppress() + whitespace + \
    Literal("<").suppress() + _datetime + Literal(">").suppress()

text = Group(OneOrMore(Group(schedule))).setResultsName("schedules") | \
    Group(org_node).setResultsName("org_node") | \
    Group(start_properties | end_properties | a_property).setResultsName("property")
class OrgNode:
    def __init__(self, kind, heading, level, content=None, tags=None, dates=None):
        self.kind = kind
        self.heading = heading
        self.level = level
        self.content = content or []
        self.tags = tags or []
        self.dates = dates or []
        self.properties = {}

    @classmethod
    def from_parsed_results(cls, parsed):
        return cls(safe(parsed, "kind"), safe(parsed, "heading"), safe(parsed, "level"), [], list(safe(parsed, "tags", [])))


class Text:
    def __init__(self, content):
        self.content = content

    def __eq__(self, other):
        return self.content == other.content


class Collection:
    def __init__(self, collections=None):
        self.collections = collections or []


class DateTime:
    def __init__(self, kind, date):
        self.date = date
        self.kind = kind

class Property:
    def __init__(self, key, value):
        self.key = key
        self.value = value


def parse_line(st):
    try:
        parsed = text.parseString(st)
        if "org_node" in parsed:
            return OrgNode.from_parsed_results(parsed["org_node"])
        elif "schedules" in parsed:
            return Collection(
                [DateTime(p["type"],
                         datetime.datetime(year=p["year"], month=p["month"], day=p["day"]))
                 for p in parsed["schedules"]])
        elif "property" in parsed:
            if "key" in parsed['property']:
                return Property(parsed['property']["key"], parsed['property']["value"].strip())
    except ParseException as e:
        return Text(st)


def find_ancestor(ancestors, parsed):
    while len(ancestors) > 0:
        ancestor = ancestors[-1]

        if ancestor.level < parsed.level:
            ancestors.append(parsed)
            return ancestors, ancestor
        else:
            ancestors.pop()

    return ancestors, None


def parse(st):
    current = root = OrgNode(None, None, 0, [])
    ancestors = [root]

    for line in st.split('\n'):
        parsed = parse_line(line)

        if isinstance(parsed, OrgNode):
            ancestors, ancestor = find_ancestor(ancestors, parsed)
            ancestor.content.append(parsed)
            current = parsed
        elif isinstance(parsed, Collection):
            current.dates = parsed.collections
        elif isinstance(parsed, Property):
            current.properties[parsed.key] = parsed.value
        else:
            current.content.append(parsed)

    return root
