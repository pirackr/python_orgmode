import datetime
from pyparsing import OneOrMore, oneOf, Keyword, White, restOfLine, ParseException, Optional, SkipTo, LineEnd, Or, ZeroOrMore, Literal, Word, nums, alphas, Suppress, Group

def integer(name):
    return Word(nums).setParseAction(lambda x: int(x.get(name))).setResultsName(name)


kind = Keyword("TODO") | Keyword("DONE")
level = OneOrMore("*")
whitespace = White()
tags = ZeroOrMore(Literal(":").suppress() + SkipTo(":")).setResultsName("tags") + Literal(":").suppress()
org_node = level.setResultsName("level") + whitespace + Optional(kind.setResultsName("kind") + whitespace) + (SkipTo(":") | SkipTo(LineEnd())).setResultsName("heading") + Optional(tags)
_datetime = integer("year") + Suppress('-') + integer('month') + Suppress('-') + integer('day') + whitespace.suppress() + Word(alphas).suppress()
schedule = (Keyword("SCHEDULED") | Keyword("DEADLINE")).setResultsName("type")  + Literal(":").suppress() + whitespace.suppress() + Literal("<").suppress() + _datetime + Literal(">").suppress() 
text = OneOrMore(Group(schedule)).setResultsName("schedules")

class OrgNode:
    def __init__(self, kind, heading, level, content=None, tags=None, scheduled=None, deadline=None):
        self.kind = kind
        self.heading = heading
        self.level = level
        self.content = content or []
        self.tags = tags or []
        self.scheduled = scheduled
        self.deadline = deadline


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

def parse_line(st):
    try:
        parsed = org_node.parseString(st)
        tags = list(parsed["tags"]) if "tags" in parsed else None
        return OrgNode(parsed["kind"], parsed["heading"], len(parsed["level"]), [], tags)
    except ParseException as e:
        try:
            print("parsed as date")
            parsed = text.parseString(st)

            schedules = list(parsed["schedules"]) if "schedules" in parsed else []
            return Collection(
                [DateTime(p["type"],
                         datetime.datetime(year=p["year"], month=p["month"], day=p["day"]))
                for p in parsed])
        except ParseException as e:
            print(st)
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
            print(parsed.collections)
            for date in parsed.collections:
                print(date.kind)
                if date.kind == "SCHEDULED":
                    current.scheduled = date
                else:
                    current.deadline = date
        else:
            current.content.append(parsed)

    return root
