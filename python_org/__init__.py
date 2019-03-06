from pyparsing import OneOrMore, oneOf, Keyword, White, restOfLine, ParseException, Optional


kind = Keyword("TODO") | Keyword("DONE")
level = OneOrMore("*")
whitespace = White()
org_node = level.setResultsName("level") + whitespace + Optional(kind.setResultsName("kind") + whitespace) + restOfLine.setResultsName("heading")


class OrgNode:
    def __init__(self, kind, heading, level, content=None):
        self.kind = kind
        self.heading = heading
        self.level = level
        self.content = content or []


class Text:
    def __init__(self, content):
        self.content = content

    def __eq__(self, other):
        return self.content == other.content


def parse_line(st):
    try:
        parsed = org_node.parseString(st)
        return OrgNode(parsed["kind"], parsed["heading"], len(parsed["level"]), [])
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
        else:
            current.content.append(parsed)

    return root
