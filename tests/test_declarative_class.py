from collections import OrderedDict
import pytest
from tri.struct import Struct

from tri.declarative import creation_ordered, declarative, with_meta, add_args_to_init_call


@creation_ordered
class Member(Struct):
    pass


@declarative(Member)
class Declarative(object):
    def __init__(self, members):
        self.members = members


def test_constructor_noop():

    subject = Declarative(members={'foo': Member(foo='bar')})

    assert subject.members == {'foo': Member(foo='bar')}


def test_find_members():

    class MyDeclarative(Declarative):
        foo = Member(foo='bar')

    subject = MyDeclarative()
    assert OrderedDict([('foo', Member(foo='bar'))]) == subject.members


def test_find_member_fail_on_tuple():
    with pytest.raises(TypeError):
        class MyDeclarative(Declarative):
            foo = Member(foo='bar'),


def test_missing_ordering():
    with pytest.raises(TypeError):
        @declarative(str)
        class Fail(object):
            x = "x"

        Fail()


def test_sort_key():
    @declarative(str, sort_key=lambda x: x)
    class Ok(object):
        a = "y"
        b = "x"

        def __init__(self, members):
            assert ['b', 'a'] == members.keys()

    Ok()


def test_find_members_not_shadowed_by_meta():

    class MyDeclarative(Declarative):
        foo = Member(foo='bar')

        class Meta:
            pass

    subject = MyDeclarative()
    assert OrderedDict([('foo', Member(foo='bar'))]) == subject.members


def test_find_members_inherited():

    class MyDeclarative(Declarative):
        foo = Member(foo='bar')

    class MyDeclarativeSubclass(MyDeclarative):
        bar = Member(foo='baz')

    subject = MyDeclarativeSubclass()
    assert OrderedDict([('foo', Member(foo='bar')), ('bar', Member(foo='baz'))]) == subject.members


def test_isolated_inheritance():
    @declarative(int, add_init_kwargs=False, sort_key=lambda x: x)
    class Base(object):
        a = 1

    class Foo(Base):
        b = 2

    class Bar(Base):
        c = 3

    assert OrderedDict([('a', 1)]) == Base.get_declared()
    assert OrderedDict([('a', 1), ('b', 2)]) == Foo.get_declared()
    assert OrderedDict([('a', 1), ('c', 3)]) == Bar.get_declared()


def test_find_members_from_base():

    @declarative(Member)
    class Base(object):
        foo = Member(foo='foo')

    class Sub(Base):
        bar = Member(bar='bar')

    assert OrderedDict([('foo', Member(foo='foo')), ('bar', Member(bar='bar'))]) == Sub._declarative_members


def test_find_members_shadow():
    @declarative(Member)
    class Base(object):
        foo = Member(bar='bar')

    class Sub(Base):
        foo = Member(bar='baz')

    assert OrderedDict([('foo', Member(bar='baz'))]) == Sub._declarative_members


def test_member_attribute_naming():

    @declarative(Member, 'foo')
    class Declarative(object):
        def __init__(self, foo):
            self.foo = foo

    class MyDeclarative(Declarative):
        bar = Member(baz='buzz')

    subject = MyDeclarative()
    assert OrderedDict([('bar', Member(baz='buzz'))]) == subject.foo


def test_string_members():

    @declarative(str, sort_key=lambda x: x)
    class Declarative(object):

        foo = 'bar'

    assert OrderedDict([('foo', 'bar')]) == Declarative.get_declared()


def test_declarative_and_meta():

    @with_meta
    @declarative(str, sort_key=lambda x: x)
    class Foo(object):
        foo = 'foo'

        class Meta:
            bar = 'bar'

        def __init__(self, members, bar):
            assert OrderedDict([('foo', 'foo')]) == members
            assert 'bar' == bar

    Foo()


def test_declarative_and_meta_other_order():

    @declarative(str, sort_key=lambda x: x)
    @with_meta
    class Foo(object):
        foo = 'foo'

        class Meta:
            bar = 'bar'

        def __init__(self, members, bar):
            assert OrderedDict([('foo', 'foo')]) == members
            assert 'bar' == bar

    Foo()


def test_multiple_types():

    @declarative(int, 'ints', sort_key=lambda x: x)
    @declarative(str, 'strs', sort_key=lambda x: x)
    class Foo(object):
        a = 1
        b = "b"

        def __init__(self, ints, strs):
            assert OrderedDict([('a', 1)]) == ints
            assert OrderedDict([('b', 'b')]) == strs

    Foo()


def test_multiple_types_inheritance():

    @declarative(int, 'ints', sort_key=lambda x: x)
    class Foo(object):
        i = 1
        a = 'a'

        def __init__(self, ints):
            assert OrderedDict([('i', 1), ('j', 2), ('k', 3)]) == ints
            super(Foo, self).__init__()

    @declarative(str, 'strs', sort_key=lambda x: x)
    class Bar(Foo):
        j = 2
        b = "b"

        def __init__(self, strs):
            assert OrderedDict([('b', 'b'), ('c', 'c')]) == strs
            super(Bar, self).__init__()

    class Baz(Bar):
        k = 3
        c = 'c'

        def __init__(self):
            super(Baz, self).__init__()

    Baz()


def test_add_args_to_init_call():

    class C(object):
        def __init__(self, x, y=None):
            self.x = x
            self.y = y

    add_args_to_init_call(C, lambda self: dict(x=17))

    c = C()
    assert 17 == c.x
    assert None == c.y

    add_args_to_init_call(C, lambda self: dict(y=42))

    c = C()
    assert 17 == c.x
    assert 42 == c.y

    c = C(x=1, y=2)
    assert 1 == c.x
    assert 2 == c.y

    c = C(1, 2)
    assert 1 == c.x
    assert 2 == c.y
