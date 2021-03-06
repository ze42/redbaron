#!/usr/bin/python
# -*- coding:Utf-8 -*-


import baron
import pytest
from baron.path import make_path, path_to_node
from redbaron import (RedBaron, NameNode, EndlNode, IntNode, AssignmentNode,
                      PassNode, NodeList, CommaNode, DotNode, CallNode)


def test_empty():
    RedBaron("")


def test_is_list():
    assert [] == list(RedBaron(""))


def test_name():
    red = RedBaron("a\n")
    assert len(red) == 2
    assert isinstance(red[0], NameNode)
    assert isinstance(red[1], EndlNode)
    assert red[0].value == "a"


def test_int():
    red = RedBaron("1\n")
    assert isinstance(red[0], IntNode)
    assert red[0].value == 1


def test_assign():
    red = RedBaron("a = 2")
    assert isinstance(red[0], AssignmentNode)
    assert isinstance(red[0].value, IntNode)
    assert red[0].value.value == 2
    assert isinstance(red[0].target, NameNode)
    assert red[0].target.value == "a"


def test_binary_operator():
    red = RedBaron("z +  42")
    assert red[0].value == "+"
    assert isinstance(red[0].first, NameNode)
    assert red[0].first.value == "z"
    assert isinstance(red[0].second, IntNode)
    assert red[0].second.value == 42

    red = RedBaron("z  -      42")
    assert red[0].value == "-"
    assert isinstance(red[0].first, NameNode)
    assert red[0].first.value == "z"
    assert isinstance(red[0].second, IntNode)
    assert red[0].second.value == 42


def test_pass():
    red = RedBaron("pass")
    assert isinstance(red[0], PassNode)


def test_copy():
    red = RedBaron("a")
    name = red[0]
    assert name.value == name.copy().value
    assert name is not name.copy()


def test_dumps():
    some_code = "ax + (z * 4)"
    red = RedBaron(some_code)
    assert some_code == red.dumps()


def test_fst():
    some_code = "ax + (z * 4)"
    red = RedBaron(some_code)
    assert baron.parse(some_code) == red.fst()


def test_get_helpers():
    red = RedBaron("a")
    assert red[0]._get_helpers() == []
    red = RedBaron("import a")
    assert red[0]._get_helpers() == ['modules', 'names']


def test_help_is_not_crashing():
    some_code = "ax + (z * 4)"
    red = RedBaron(some_code)
    red.help()
    red[0].help()


def test_assign_on_string_value():
    some_code = "ax + (z * 4)"
    red = RedBaron(some_code)
    binop = red[0]
    assert binop.first.value == "ax"
    binop.first.value = "pouet"
    assert binop.first.value == "pouet"


def test_assign_on_object_value():
    some_code = "ax + (z * 4)"
    red = RedBaron(some_code)
    binop = red[0]
    assert binop.first.value == "ax"
    binop.first = "pouet"  # will be parsed as a name
    assert binop.first.value == "pouet"
    assert binop.first.type == "name"
    binop.first = "42"  # will be parsed as a int
    assert binop.first.value == 42
    assert binop.first.type == "int"


def test_assign_on_object_value_fst():
    some_code = "ax + (z * 4)"
    red = RedBaron(some_code)
    binop = red[0]
    binop.first = {"type": "name", "value": "pouet"}
    assert binop.first.value == "pouet"
    assert binop.first.type == "name"


def test_generate_helpers():
    red = RedBaron("def a(): pass")
    assert set(red[0]._generate_identifiers()) == set(["funcdef", "funcdef_", "funcdefnode", "def", "def_"])


def test_assign_node_list():
    red = RedBaron("[1, 2, 3]")
    l = red[0]
    l.value = "pouet"
    assert l.value[0].value == "pouet"
    assert l.value[0].type == "name"
    assert isinstance(l.value, NodeList)
    l.value = ["pouet"]
    assert l.value[0].value == "pouet"
    assert l.value[0].type == "name"
    assert isinstance(l.value, NodeList)


def test_assign_node_list_fst():
    red = RedBaron("[1, 2, 3]")
    l = red[0]
    l.value = {"type": "name", "value": "pouet"}
    assert l.value[0].value == "pouet"
    assert l.value[0].type == "name"
    assert isinstance(l.value, NodeList)
    l.value = [{"type": "name", "value": "pouet"}]
    assert l.value[0].value == "pouet"
    assert l.value[0].type == "name"
    assert isinstance(l.value, NodeList)


def test_assign_node_list_mixed():
    red = RedBaron("[1, 2, 3]")
    l = red[0]
    l.value = ["plop", {"type": "comma", "first_formatting": [], "second_formatting": []}, {"type": "name", "value": "pouet"}]
    assert l.value[0].value == "plop"
    assert l.value[0].type == "name"
    assert l.value[1].type == "comma"
    assert l.value[2].value == "pouet"
    assert l.value[2].type == "name"
    assert isinstance(l.value, NodeList)


def test_parent():
    red = RedBaron("a = 1 + caramba")
    assert red.parent is None
    assert red[0].parent is red
    assert red[0].on_attribute == "root"
    assert red[0].target.parent is red[0]
    assert red[0].target.on_attribute == "target"
    assert red[0].value.parent is red[0]
    assert red[0].value.on_attribute == "value"
    assert red[0].value.first.parent is red[0].value
    assert red[0].value.first.on_attribute == "first"
    assert red[0].value.second.parent is red[0].value
    assert red[0].value.second.on_attribute == "second"

    red = RedBaron("[1, 2, 3]")
    assert red.parent is None
    assert red[0].parent is red
    assert [x.parent for x in red[0].value] == [red[0]]*5
    assert [x.on_attribute for x in red[0].value] == ["value"]*5


def test_parent_copy():
    red = RedBaron("a = 1 + caramba")
    assert red[0].value.copy().parent is None


def test_parent_assign():
    red = RedBaron("a = 1 + caramba")
    assert red[0].target.parent is red[0]
    red[0].target = "plop"
    assert red[0].target.parent is red[0]
    assert red[0].target.on_attribute == "target"
    red[0].target = {"type": "name", "value": "pouet"}
    assert red[0].target.parent is red[0]
    assert red[0].target.on_attribute == "target"
    red[0].target = NameNode({"type": "name", "value": "pouet"})
    assert red[0].target.parent is red[0]
    assert red[0].target.on_attribute == "target"

    red = RedBaron("[1, 2, 3]")
    assert [x.parent for x in red[0].value] == [red[0]]*5
    assert [x.on_attribute for x in red[0].value] == ["value"]*5
    red[0].value = "pouet"
    assert [x.parent for x in red[0].value] == [red[0]]
    assert [x.on_attribute for x in red[0].value] == ["value"]
    red[0].value = ["pouet"]
    assert [x.parent for x in red[0].value] == [red[0]]
    assert [x.on_attribute for x in red[0].value] == ["value"]
    red[0].value = {"type": "name", "value": "plop"}
    assert [x.parent for x in red[0].value] == [red[0]]
    assert [x.on_attribute for x in red[0].value] == ["value"]
    red[0].value = [{"type": "name", "value": "plop"}]
    assert [x.parent for x in red[0].value] == [red[0]]
    assert [x.on_attribute for x in red[0].value] == ["value"]
    red[0].value = NameNode({"type": "name", "value": "pouet"})
    assert [x.parent for x in red[0].value] == [red[0]]
    assert [x.on_attribute for x in red[0].value] == ["value"]
    red[0].value = [NameNode({"type": "name", "value": "pouet"})]
    assert [x.parent for x in red[0].value] == [red[0]]
    assert [x.on_attribute for x in red[0].value] == ["value"]


def test_node_next():
    red = RedBaron("[1, 2, 3]")
    assert red.next is None
    assert red[0].next is None
    inner = red[0].value
    assert inner[0].next == inner[1]
    assert inner[1].next == inner[2]
    assert inner[2].next == inner[3]
    assert inner[3].next == inner[4]
    assert inner[4].next is None


def test_node_previous():
    red = RedBaron("[1, 2, 3]")
    assert red.previous is None
    assert red[0].previous is None
    inner = red[0].value
    assert inner[4].previous == inner[3]
    assert inner[3].previous == inner[2]
    assert inner[2].previous == inner[1]
    assert inner[1].previous == inner[0]
    assert inner[0].previous is None


def test_node_next_generator():
    red = RedBaron("[1, 2, 3]")
    assert list(red[0].value[2].next_generator()) == list(red[0].value[3:])


def test_node_previous_generator():
    red = RedBaron("[1, 2, 3]")
    assert list(red[0].value[2].previous_generator()) == list(reversed(red[0].value[:2]))


def test_map():
    red = RedBaron("[1, 2, 3]")
    assert red('int').map(lambda x: x.value) == NodeList([1, 2, 3])


def test_apply():
    red = RedBaron("a()\nb()")
    assert red('call').apply(lambda x: x.append_value("plop")) == red('call')


def test_filter():
    red = RedBaron("[1, 2, 3]")
    assert red[0].value.filter(lambda x: x.type != "comma") == red('int')
    assert isinstance(red[0].value.filter(lambda x: x.type != "comma"), NodeList)


def test_append_item_comma_list_empty():
    red = RedBaron("[]")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"


def test_append_item_comma_list_one():
    red = RedBaron("[1]")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"


def test_append_item_comma_list_one_comma():
    red = RedBaron("[1,]")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"


def test_append_item_comma_list_empty_trailing():
    red = RedBaron("[]")
    r = red[0]
    r.append_value("4", trailing=True)
    assert r.value.dumps() == "4,"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"


def test_append_item_comma_list_one_trailing():
    red = RedBaron("[1]")
    r = red[0]
    r.append_value("4", trailing=True)
    assert r.value.dumps() == "1, 4,"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"


def test_append_item_comma_list_one_comma_trailing():
    red = RedBaron("[1,]")
    r = red[0]
    r.append_value("4", trailing=True)
    assert r.value.dumps() == "1, 4,"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"


def test_append_item_comma_set():
    red = RedBaron("{1}")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    # FIXME: bug in baron, can't parse next stuff
    # red = RedBaron("{1,}")
    # r = red[0]
    # r.append_value("4")
    # assert r.value.dumps() == "1, 4"
    # assert r.value[-1].parent is r
    # assert r.value[-1].on_attribute == "value"
    # assert r.value[-2].parent is r
    # assert r.value[-2].on_attribute == "value"


def test_append_item_comma_tuple():
    red = RedBaron("()")
    r = red[0]
    r.append_value("4")
    # should add a comma for a single item tuple
    assert r.value.dumps() == "4,"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    red = RedBaron("(1,)")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"
    red = RedBaron("(1, 2)")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 2, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"


def test_append_item_comma_tuple_without_parenthesis():
    red = RedBaron("1,")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"
    red = RedBaron("1, 2")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 2, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"


def test_append_item_comma_dict_empty():
    red = RedBaron("{}")
    r = red[0]
    r.append_value(key="a", value="b")
    assert r.value.dumps() == "a: b"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    red = RedBaron("{1: 2}")
    r = red[0]
    r.append_value(key="a", value="b")
    assert r.value.dumps() == "1: 2, a: b"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    red = RedBaron("{1: 2,}")
    r = red[0]
    r.append_value(key="a", value="b")
    assert r.value.dumps() == "1: 2, a: b"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"


def test_append_item_comma_list_node():
    red = RedBaron("[]")
    r = red[0]
    r.append_value(IntNode({"value": "4", "type": "int"}))
    assert r.value.dumps() == "4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"


def test_append_item_comma_repr():
    red = RedBaron("`1`")
    r = red[0]
    r.append_value("4")
    assert r.value.dumps() == "1, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"


def test_indent_root():
    red = RedBaron("pouet")
    assert red[0].indentation == ""
    red = RedBaron("pouet\nplop\npop")
    assert [x.indentation for x in red] == ["", "", "", "", ""]
    assert [x.get_indentation_node() for x in red] == [None]*5


def test_in_while():
    red = RedBaron("while a:\n    pass\n")
    assert red[0].value[-2].indentation == "    "
    assert red[0].value[-1].indentation == ""
    assert red[0].value[-2].get_indentation_node() is red[0].value[-3]
    assert red[0].value[-1].get_indentation_node() is None
    assert red[0].value[-3].get_indentation_node() is None
    assert red[0].value[-2].indentation_node_is_direct()


def test_one_line_while():
    red = RedBaron("while a: pass\n")
    assert red[0].value[0].indentation == ""
    assert red[0].value[-2].get_indentation_node() is None
    assert not red[0].value[-2].indentation_node_is_direct()


def test_inner_node():
    red = RedBaron("while a: pass\n")
    assert red[0].test.indentation == ""
    assert red[0].value[-2].get_indentation_node() is None
    assert not red[0].value[-2].indentation_node_is_direct()


def test_indentation_endl():
    red = RedBaron("a.b.c.d")
    assert red[0].value[-3].indentation == ""
    assert red[0].value[-2].get_indentation_node() is None
    assert not red[0].value[-2].indentation_node_is_direct()


def test_filtered_endl():
    red = RedBaron("while a:\n    pass\n")
    assert red[0].value.filtered() == (red[0].value[-2],)


def test_filtered_comma():
    red = RedBaron("[1, 2, 3]")
    assert red[0].value.filtered() == tuple(red[0].value.filter(lambda x: not isinstance(x, CommaNode)))


def test_filtered_dot():
    red = RedBaron("a.b.c(d)")
    assert red[0].value.filtered() == tuple(red[0].value.filter(lambda x: not isinstance(x, DotNode)))


def test_endl_list_append_value():
    red = RedBaron("while a:\n    pass\n")
    red[0].append_value("pouet")
    assert red.dumps() == "while a:\n    pass\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_trailing():
    red = RedBaron("while a:\n    p\n    \n")
    red[0].append_value("pouet")
    assert red.dumps() == "while a:\n    p\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_one_line_while():
    red = RedBaron("while a: pass\n")
    red[0].append_value("pouet")
    assert red.dumps() == "while a:\n    pass\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_with():
    red = RedBaron("with a:\n    pass\n")
    red[0].append_value("pouet")
    assert red.dumps() == "with a:\n    pass\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_trailing_with():
    red = RedBaron("with a:\n    p\n    \n")
    red[0].append_value("pouet")
    assert red.dumps() == "with a:\n    p\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_one_line_with():
    red = RedBaron("with a: pass\n")
    red[0].append_value("pouet")
    assert red.dumps() == "with a:\n    pass\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_class():
    red = RedBaron("class a:\n    pass\n")
    red[0].append_value("pouet")
    assert red.dumps() == "class a:\n    pass\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_trailing_class():
    red = RedBaron("class a:\n    p\n    \n")
    red[0].append_value("pouet")
    assert red.dumps() == "class a:\n    p\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_one_line_class():
    red = RedBaron("class a: pass\n")
    red[0].append_value("pouet")
    assert red.dumps() == "class a:\n    pass\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_def():
    red = RedBaron("def a():\n    pass\n")
    red[0].append_value("pouet")
    assert red.dumps() == "def a():\n    pass\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_trailing_def():
    red = RedBaron("def a():\n    p\n    \n")
    red[0].append_value("pouet")
    assert red.dumps() == "def a():\n    p\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_one_line_def():
    red = RedBaron("def a(): pass\n")
    red[0].append_value("pouet")
    assert red.dumps() == "def a():\n    pass\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_for():
    red = RedBaron("for a in a:\n    pass\n")
    red[0].append_value("pouet")
    assert red.dumps() == "for a in a:\n    pass\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_trailing_for():
    red = RedBaron("for a in a:\n    p\n    \n")
    red[0].append_value("pouet")
    assert red.dumps() == "for a in a:\n    p\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_one_line_for():
    red = RedBaron("for a in a: pass\n")
    red[0].append_value("pouet")
    assert red.dumps() == "for a in a:\n    pass\n    pouet\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_if():
    red = RedBaron("if a:\n    pass\n")
    red[0].value[0].append_value("pouet")
    assert red.dumps() == "if a:\n    pass\n    pouet\n"
    assert red[0].value[0].value[-2].parent is red[0].value[0]
    assert red[0].value[0].value[-3].parent is red[0].value[0]
    assert red[0].value[0].value[-2].on_attribute == "value"
    assert red[0].value[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_elif():
    red = RedBaron("if a:\n    pass\nelif b:\n    pass\n")
    red[0].value[1].append_value("pouet")
    assert red.dumps() == "if a:\n    pass\nelif b:\n    pass\n    pouet\n"
    assert red[0].value[1].value[-2].parent is red[0].value[1]
    assert red[0].value[1].value[-3].parent is red[0].value[1]
    assert red[0].value[1].value[-2].on_attribute == "value"
    assert red[0].value[1].value[-3].on_attribute == "value"


def test_endl_list_append_value_else():
    red = RedBaron("if a:\n    pass\nelse:\n    pass\n")
    red[0].value[1].append_value("pouet")
    assert red.dumps() == "if a:\n    pass\nelse:\n    pass\n    pouet\n"
    assert red[0].value[1].value[-2].parent is red[0].value[1]
    assert red[0].value[1].value[-3].parent is red[0].value[1]
    assert red[0].value[1].value[-2].on_attribute == "value"
    assert red[0].value[1].value[-3].on_attribute == "value"


def test_endl_list_append_value_trailing_if():
    red = RedBaron("if a:\n    p\n    \n")
    red[0].value[0].append_value("pouet")
    assert red.dumps() == "if a:\n    p\n    pouet\n"
    assert red[0].value[0].value[-2].parent is red[0].value[0]
    assert red[0].value[0].value[-3].parent is red[0].value[0]
    assert red[0].value[0].value[-2].on_attribute == "value"
    assert red[0].value[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_trailing_elif():
    red = RedBaron("if a:\n    p\n    \nelif b:\n    p\n    \n")
    red[0].value[1].append_value("pouet")
    assert red.dumps() == "if a:\n    p\n    \nelif b:\n    p\n    pouet\n"
    assert red[0].value[1].value[-2].parent is red[0].value[1]
    assert red[0].value[1].value[-3].parent is red[0].value[1]
    assert red[0].value[1].value[-2].on_attribute == "value"
    assert red[0].value[1].value[-3].on_attribute == "value"


def test_endl_list_append_value_trailing_else():
    red = RedBaron("if a:\n    p\n    \nelse:\n    p\n    \n")
    red[0].value[1].append_value("pouet")
    assert red.dumps() == "if a:\n    p\n    \nelse:\n    p\n    pouet\n"
    assert red[0].value[1].value[-2].parent is red[0].value[1]
    assert red[0].value[1].value[-3].parent is red[0].value[1]
    assert red[0].value[1].value[-2].on_attribute == "value"
    assert red[0].value[1].value[-3].on_attribute == "value"


def test_endl_list_append_one_line_if():
    red = RedBaron("if a: pass\n")
    red[0].value[0].append_value("pouet")
    assert red.dumps() == "if a:\n    pass\n    pouet\n"
    assert red[0].value[0].value[-2].parent is red[0].value[0]
    assert red[0].value[0].value[-3].parent is red[0].value[0]
    assert red[0].value[0].value[-2].on_attribute == "value"
    assert red[0].value[0].value[-3].on_attribute == "value"


def test_endl_list_append_one_line_elif():
    red = RedBaron("if a: pass\nelif b: pass\n")
    red[0].value[1].append_value("pouet")
    assert red.dumps() == "if a: pass\nelif b:\n    pass\n    pouet\n"
    assert red[0].value[1].value[-2].parent is red[0].value[1]
    assert red[0].value[1].value[-3].parent is red[0].value[1]
    assert red[0].value[1].value[-2].on_attribute == "value"
    assert red[0].value[1].value[-3].on_attribute == "value"


def test_endl_list_append_one_line_else():
    red = RedBaron("if a: pass\nelse: pass\n")
    red[0].value[1].append_value("pouet")
    assert red.dumps() == "if a: pass\nelse:\n    pass\n    pouet\n"
    assert red[0].value[1].value[-2].parent is red[0].value[1]
    assert red[0].value[1].value[-3].parent is red[0].value[1]
    assert red[0].value[1].value[-2].on_attribute == "value"
    assert red[0].value[1].value[-3].on_attribute == "value"


def test_endl_list_append_value_try():
    red = RedBaron("try:\n    pass\nexcept:\n    pass\n")
    red[0].append_value("pouet")
    assert red.dumps() == "try:\n    pass\n    pouet\nexcept:\n    pass\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_except():
    red = RedBaron("try:\n    pass\nexcept:\n    pass\n")
    red[0].excepts[0].append_value("pouet")
    assert red.dumps() == "try:\n    pass\nexcept:\n    pass\n    pouet\n"
    assert red[0].excepts[0].value[-2].parent is red[0].excepts[0]
    assert red[0].excepts[0].value[-3].parent is red[0].excepts[0]
    assert red[0].excepts[0].value[-2].on_attribute == "value"
    assert red[0].excepts[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_finally():
    red = RedBaron("try:\n    pass\nfinally:\n    pass\n")
    red[0].finally_.append_value("pouet")
    assert red.dumps() == "try:\n    pass\nfinally:\n    pass\n    pouet\n"
    assert red[0].finally_.value[-2].parent is red[0].finally_
    assert red[0].finally_.value[-3].parent is red[0].finally_
    assert red[0].finally_.value[-2].on_attribute == "value"
    assert red[0].finally_.value[-3].on_attribute == "value"


def test_endl_list_append_value_trailing_try():
    red = RedBaron("try:\n    pass\n    \nexcept:\n    pass\n")
    red[0].append_value("pouet")
    assert red.dumps() == "try:\n    pass\n    pouet\nexcept:\n    pass\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_trailing_except():
    red = RedBaron("try:\n    pass\nexcept:\n    pass\n    \n")
    red[0].excepts[0].append_value("pouet")
    assert red.dumps() == "try:\n    pass\nexcept:\n    pass\n    pouet\n"
    assert red[0].excepts[0].value[-2].parent is red[0].excepts[0]
    assert red[0].excepts[0].value[-3].parent is red[0].excepts[0]
    assert red[0].excepts[0].value[-2].on_attribute == "value"
    assert red[0].excepts[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_trailing_finally():
    red = RedBaron("try:\n    pass\nfinally:\n    pass\n    \n")
    red[0].finally_.append_value("pouet")
    assert red.dumps() == "try:\n    pass\nfinally:\n    pass\n    pouet\n"
    assert red[0].finally_.value[-2].parent is red[0].finally_
    assert red[0].finally_.value[-3].parent is red[0].finally_
    assert red[0].finally_.value[-2].on_attribute == "value"
    assert red[0].finally_.value[-3].on_attribute == "value"


def test_endl_list_append_one_line_try():
    red = RedBaron("try: pass\nexcept:\n    pass\n")
    red[0].append_value("pouet")
    assert red.dumps() == "try:\n    pass\n    pouet\nexcept:\n    pass\n"
    assert red[0].value[-2].parent is red[0]
    assert red[0].value[-3].parent is red[0]
    assert red[0].value[-2].on_attribute == "value"
    assert red[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_one_line_except():
    red = RedBaron("try:\n    pass\nexcept: pass\n")
    red[0].excepts[0].append_value("pouet")
    assert red.dumps() == "try:\n    pass\nexcept:\n    pass\n    pouet\n"
    assert red[0].excepts[0].value[-2].parent is red[0].excepts[0]
    assert red[0].excepts[0].value[-3].parent is red[0].excepts[0]
    assert red[0].excepts[0].value[-2].on_attribute == "value"
    assert red[0].excepts[0].value[-3].on_attribute == "value"


def test_endl_list_append_value_one_line_finally():
    red = RedBaron("try:\n    pass\nfinally: pass\n")
    red[0].finally_.append_value("pouet")
    assert red.dumps() == "try:\n    pass\nfinally:\n    pass\n    pouet\n"
    assert red[0].finally_.value[-2].parent is red[0].finally_
    assert red[0].finally_.value[-3].parent is red[0].finally_
    assert red[0].finally_.value[-2].on_attribute == "value"
    assert red[0].finally_.value[-3].on_attribute == "value"


def test_append_item_comma_call_empty():
    red = RedBaron("a()")
    r = red[0].value[1]
    r.append_value("4")
    assert r.value.dumps() == "4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"


def test_append_item_comma_call_one():
    red = RedBaron("a(1)")
    r = red[0].value[1]
    r.append_value("4")
    assert r.value.dumps() == "1, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"


def test_append_item_comma_call_one_comma():
    red = RedBaron("a(1,)")
    r = red[0].value[1]
    r.append_value("4")
    assert r.value.dumps() == "1, 4"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"
    assert r.value[-2].parent is r
    assert r.value[-2].on_attribute == "value"


def test_append_item_call_node_star_arg():
    red = RedBaron("a()")
    r = red[0].value[1]
    r.append_value("*a")
    assert r.value.dumps() == "*a"
    assert r.value[-1].parent is r
    assert r.value[-1].on_attribute == "value"

some_data_for_test = """\
def plop():
    def a():
        with b as c:
            d = e
"""

def test_parent_find_empty():
    red = RedBaron("a")
    assert red[0].parent_find('a') is None


def test_parent_find_direct():
    red = RedBaron(some_data_for_test)
    r = red.assignment.target
    assert r.parent_find('with') is red.with_


def test_parent_find_two_levels():
    red = RedBaron(some_data_for_test)
    r = red.assignment.target
    assert r.parent_find('funcdef') is red.find('funcdef', name='a')


def test_parent_find_two_levels_options():
    red = RedBaron(some_data_for_test)
    r = red.assignment.target
    assert r.parent_find('def', name='plop') is red.def_
    assert r.parent_find('def', name='dont_exist') is None


def test_find_empty():
    red = RedBaron("")
    assert red.find("stuff") is None
    assert red.find("something_else") is None
    assert red.find("something_else", useless="pouet") is None
    assert red.something_else is None


def test_find():
    red = RedBaron("def a(): b = c")
    assert red.find("name") is red[0].value[0].target
    assert red.find("name", value="c") is red[0].value[0].value
    assert red.name is red[0].value[0].target


def test_find_other_properties():
    red = RedBaron("def a(): b = c")
    assert red.funcdef == red[0]
    assert red.funcdef_ == red[0]
    assert red.def_ == red[0]


def test_find_case_insensitive():
    red = RedBaron("a")
    assert red.find("NameNode") is red[0]
    assert red.find("NaMeNoDe") is red[0]
    assert red.find("namenode") is red[0]


def test_copy_correct_isntance():
    red = RedBaron("a()")
    assert isinstance(red[0].value[1].copy(), CallNode)


def test_indentation_no_parent():
    red = RedBaron("a")
    assert red[0].copy().get_indentation_node() is None
    assert red[0].copy().indentation == ''


@pytest.fixture
def red():
    return RedBaron("""\
@deco
def a(c, d):
    b = c + d
""")


def check_path(root, node, path):
    assert node.path().to_baron_path() == path
    assert root.find_by_path(path) is node


def test_path_root(red):
    check_path(red, red, make_path())


def test_path_first_statement(red):
    check_path(red,
            red.funcdef,
            make_path([], "list", 0)
        )


def test_path_funcdef_decorators(red):
    check_path(red,
            red.funcdef.decorators,
            make_path([0], "funcdef", 0)
        )


def test_path_decorators_first(red):
    check_path(red,
            red.funcdef.decorators[0],
            make_path([0, "decorators"], "list", 0)
        )


def test_path_decorators_first_dotted_name(red):
    check_path(red,
            red.funcdef.decorators[0].value,
            make_path([0, "decorators", 0], "decorator", 1)
        )


def test_path_decorators_first_dotted_name_value(red):
    check_path(red,
            red.funcdef.decorators[0].value.value,
            make_path([0, "decorators", 0, "value"], "dotted_name", 0)
        )


def test_path_decorators_first_dotted_name_value_first(red):
    check_path(red,
            red.funcdef.decorators[0].value.value[0],
            make_path([0, "decorators", 0, "value", "value"], "list", 0)
        )


def test_path_decorators_endl(red):
    check_path(red,
            red.funcdef.decorators[1],
            make_path([0, "decorators"], "list", 1)
        )


def test_path_first_formatting(red):
    check_path(red,
            red.funcdef.first_formatting,
            make_path([0], "funcdef", 2)
        )


def test_path_first_formatting_value(red):
    check_path(red,
            red.funcdef.first_formatting[0],
            make_path([0, "first_formatting"], "list", 0)
        )


def test_path_second_formatting(red):
    check_path(red,
            red.funcdef.second_formatting,
            make_path([0], "funcdef", 4)
        )


def test_path_third_formatting(red):
    check_path(red,
            red.funcdef.third_formatting,
            make_path([0], "funcdef", 6)
        )


def test_path_arguments(red):
    check_path(red,
            red.funcdef.arguments,
            make_path([0], "funcdef", 7)
        )


def test_path_arguments_first(red):
    check_path(red,
            red.funcdef.arguments[0],
            make_path([0, "arguments"], "list", 0)
        )


def test_path_arguments_comma(red):
    check_path(red,
            red.funcdef.arguments[1],
            make_path([0, "arguments"], "list", 1)
        )


def test_path_arguments_second(red):
    check_path(red,
            red.funcdef.arguments[2],
            make_path([0, "arguments"], "list", 2)
        )


def test_path_fourth_formatting(red):
    check_path(red,
            red.funcdef.fourth_formatting,
            make_path([0], "funcdef", 8)
        )


def test_path_fifth_formatting(red):
    check_path(red,
            red.funcdef.fifth_formatting,
            make_path([0], "funcdef", 10)
        )


def test_path_sixth_formatting(red):
    check_path(red,
            red.funcdef.sixth_formatting,
            make_path([0], "funcdef", 12)
        )


def test_path_value(red):
    check_path(red,
            red.funcdef.value,
            make_path([0], "funcdef", 13)
        )


def test_path_value_first_endl(red):
    check_path(red,
            red.funcdef.value[0],
            make_path([0, "value"], "list", 0)
        )


def test_path_value_assignment(red):
    check_path(red,
            red.funcdef.value[1],
            make_path([0, "value"], "list", 1)
        )


def test_path_value_assignment_target(red):
    check_path(red,
            red.funcdef.value[1].target,
            make_path([0, "value", 1], "assignment", 0)
        )


def test_path_value_assignment_value(red):
    check_path(red,
            red.funcdef.value[1].value,
            make_path([0, "value", 1], "assignment", 5)
        )


def test_path_value_assignment_value_first(red):
    check_path(red,
            red.funcdef.value[1].value.first,
            make_path([0, "value", 1, "value"], "binary_operator", 0)
        )


def test_path_value_assignment_value_second(red):
    check_path(red,
            red.funcdef.value[1].value.second,
            make_path([0, "value", 1, "value"], "binary_operator", 4)
        )


def test_path_value_second_endl(red):
    check_path(red,
            red.funcdef.value[2],
            make_path([0, "value"], "list", 2)
        )

