import unittest

from datetime import datetime
from robber import expect
from python_orgmode import parse, OrgNode, Text


class HeadlinesTest(unittest.TestCase):
    def test_valid_headline(self):
        root = parse('''* TODO Hello''')
        expect(root.content).to.have.length(1)
        expect(root.content[0].kind).to.be.eq("TODO")
        expect(root.content[0].heading).to.be.eq("Hello")
        expect(root.content[0].level).to.be.eq(1)

    def test_not_a_headline(self):
        [expect(parse(st).content[0]).not_to.be.instanceof(OrgNode) for st in [
            "*Test*",
            "*TODO Hello",
            "Not a node *TODO*"
        ]]

    def test_with_body(self):
        root = parse('''* TODO Node 1
Node1->body1
Node1->body2
* TODO Node2
Node2->body1''')
        [expect(x).to.be.instanceof(OrgNode) for x in root.content]
        expect(root.content[0].content).to.be.eq([Text("Node1->body1"), Text("Node1->body2")])
        expect(root.content[1].content).to.be.eq([Text("Node2->body1")])

    def test_with_children(self):
        root = parse('''* TODO Parent
** TODO Child''')
        parent = root.content[0]
        child = parent.content[0]

        expect(root.content).to.have.length(1)
        expect(parent).to.be.instanceof(OrgNode)
        expect(parent.heading).to.be.eq("Parent")
        expect(parent.content).to.have.length(1)
        expect(child).to.be.instanceof(OrgNode)
        expect(child.heading).to.be.eq("Child")

    def test_multiple_level_of_children(self):
        root = parse('''* TODO Level 1
*** TODO First Level 3
** TODO Level 2
*** TODO Second Level 3
** TODO Another Level 2
* TODO Another Level 1''')
        level1 = root.content[0]
        level2 = level1.content[1]
        level3 = level2.content[0]

        expect(root.content).to.have.length(2)
        expect(level1.content).to.have.length(3)
        expect(level1.heading).to.be.eq("Level 1")
        expect(level2.content).to.have.length(1)
        expect(level2.heading).to.be.eq("Level 2")
        expect(level3.heading).to.be.eq("Second Level 3")

    def test_with_tags(self):
        root = parse("* TODO Heading :tag1:tag2:")
        node = root.content[0]

        expect(node.heading).to.be.eq("Heading")
        expect(node.tags).to.be.eq(["tag1", "tag2"])

    def test_with_date(self):
        root = parse('''* TODO Task
  DEADLINE: <2019-03-07 Wed> SCHEDULED: <2019-03-06 Wed>''')
        node = root.content[0]
        expect(node.dates).to.have.length(2)
        expect(node.dates[0].kind).to.be.eq("DEADLINE")
        expect(node.dates[0].date).to.be.eq(datetime(year=2019, month=3, day=7))
        expect(node.dates[1].kind).to.be.eq("SCHEDULED")
        expect(node.dates[1].date).to.be.eq(datetime(year=2019, month=3, day=6))

    def test_bug_heading_with_colon(self):
        root = parse('''* TODO hello:test''')
        expect(root.content[0].heading).to.be.eq("hello:test")

    def test_parse_properties(self):
        root = parse('''* Heading 
:PROPERTIES:
:CATEGORY: cat
:END:
''')
        node = root.content[0]
        print(node)
        expect(node.heading).to.be.eq("Heading")
        expect(node.properties).to.contain("CATEGORY")
        expect(node.properties["CATEGORY"]).to.be.eq("cat")
