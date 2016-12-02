examples/go/go-routine.py

```python
from prestring.go import Module


m = Module()
m.package('main')

with m.import_group() as mg:
    mg.import_('golang.org/x/net/context')
    mg.import_('log')
    mg.import_('sync')


with m.func('gen', 'nums ...int', return_='<-chan int'):
    m.stmt('out := make(chan int)')
    with m.block('go func()'):
        with m.for_('_,  n := range nums'):
            m.stmt('out <- n')
        m.stmt('close(out)')
    m.insert_after('()')
    m.return_('out')


with m.func('sq', 'ctx context.Context', 'in <-chan int', return_='<-chan int'):
    m.stmt('out := make(chan int)')
    with m.block('go func()'):
        m.stmt('defer close(out)')
        with m.for_('n := range in'):
            with m.select() as s:
                with s.case('<-ctx.Done()'):
                    s.return_('')
                with s.case('out <- n*n'):
                    pass
    m.unnewline()
    m.stmt('()')
    m.return_('out')


with m.func('merge', 'ctx context.Context', 'cs ...<-chan int', return_='<-chan int'):
    m.stmt('var wg sync.WaitGroup')
    m.stmt('out := make(chan int)')
    m.sep()
    with m.block('output := func(c <- chan int)'):
        m.stmt('defer wg.Done()')
        with m.for_('n := range c'):
            with m.select() as s:
                with s.case('out <- n'):
                    pass
                with s.case('<-ctx.Done()'):
                    m.return_('')
    m.sep()
    m.stmt('wg.Add(len(cs))')
    with m.for_('_, c := range cs'):
        m.stmt('go output(c)')
    with m.block('go func()'):
        m.stmt('wg.Wait()')
        m.stmt('close(out)')
    m.insert_after('()')
    m.return_('out')


with m.func('main'):
    m.stmt('ctx := context.Background()')
    m.stmt('ctx, cancel := context.WithCancel(ctx)')
    m.sep()
    m.stmt('in := gen(1, 2, 3, 4, 5)')
    m.stmt('c1 := sq(ctx, in)')
    m.stmt('c2 := sq(ctx, in)')
    m.sep()
    m.stmt('out := merge(ctx, c1, c2)')
    m.sep()
    m.stmt('log.Printf("%d\\n", <-out) // 1')
    m.stmt('log.Printf("%d\\n", <-out) // 4')
    m.sep()
    m.stmt("cancel()")


print(m)
```

output

```
package main

import (
	"golang.org/x/net/context"
	"log"
	"sync"
)

func gen(nums ...int) <-chan int {
	out := make(chan int)
	go func() {
		for _,  n := range nums  {
			out <- n
		}
		close(out)
	}()
	return out
}

func sq(ctx context.Context, in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for n := range in  {
			select {
			case <-ctx.Done():
				return 
			case out <- n*n:

			}

		}
	}()
	return out
}

func merge(ctx context.Context, cs ...<-chan int) <-chan int {
	var wg sync.WaitGroup
	out := make(chan int)

	output := func(c <- chan int) {
		defer wg.Done()
		for n := range c  {
			select {
			case out <- n:

			case <-ctx.Done():

			}

			return 
		}
	}

	wg.Add(len(cs))
	for _, c := range cs  {
		go output(c)
	}
	go func() {
		wg.Wait()
		close(out)
	}()
	return out
}

func main()  {
	ctx := context.Background()
	ctx, cancel := context.WithCancel(ctx)

	in := gen(1, 2, 3, 4, 5)
	c1 := sq(ctx, in)
	c2 := sq(ctx, in)

	out := merge(ctx, c1, c2)

	log.Printf("%d\n", <-out) // 1
	log.Printf("%d\n", <-out) // 4

	cancel()
}
```

examples/go/hello.py

```python
from prestring.go import Module

m = Module()
m.package('main')

with m.import_group() as import_:
    import_('fmt')
    import_("os")

m.comment("Hello is print Hello")
with m.func('Hello', "name string"):
    m.stmt('fmt.Printf("%s: Hello", name)')


with m.func('main'):
    m.stmt('var name string')
    with m.if_('len(os.Args) > 1'):
        m.stmt('name = os.Args[1]')
    with m.else_():
        m.stmt('name = "foo"')

    m.comment('with block')
    with m.block():
        m.stmt("Hello(name)")


print(m)
```

output

```
package main

import (
	"fmt"
	"os"
)

// Hello is print Hello
func Hello(name string)  {
	fmt.Printf("%s: Hello", name)
}

func main()  {
	var name string
	if len(os.Args) > 1  {
		name = os.Args[1]
	} else  {
		name = "foo"
	}
	// with block
	{
		Hello(name)
	}
}
```

examples/go/models.py

```python
import copy
import json
import logging
import os.path
from prestring.go import Module


logger = logging.getLogger(__name__)


class Reader(object):
    def read_world(self, data, parent=None):
        world = World(parent=parent, reader=self)
        for name, module in data["module"].items():
            world.read_module(name, module)
        return world

    def read_module(self, data, parent=None):
        module = Module(data["name"], parent=parent, reader=self)
        for name, file in data["file"].items():
            module.read_file(name, file)
        return module

    def read_file(self, data, parent=None):
        file = File(data["name"], parent=parent, reader=self)
        for name, alias in data["alias"].items():
            file.read_alias(name, alias)
        for name, struct in data["struct"].items():
            file.read_struct(name, struct)
        return file

    def read_struct(self, data, parent=None):
        struct = Struct(data["name"], data, parent=parent, reader=self)
        return struct

    def read_alias(self, data, parent=None):
        alias = Alias(data["name"], data, parent=parent, reader=self)
        return alias


class GOWriter(object):
    prestring_module = Module

    def write_file(self, file, m=None):
        m = m or self.prestring_module()
        self.write_packagename(file, m=m)
        for struct in file.structs.values():
            self.write_struct(struct, m=m)
        for alias in file.aliases.values():
            self.write_alias(alias, m=m)
        return m

    def write_packagename(self, file, m=None):
        m = m or self.prestring_module()
        package_name = file.package_name
        if package_name is not None:
            m.package(package_name)
        return m

    def write_struct(self, struct, m=None):
        m = m or self.prestring_module()
        struct = struct.data
        self.write_comment(struct, m=m)
        with m.type_(struct["name"], "struct"):
            for field in sorted(struct["fields"].values(), key=lambda f: f["name"]):
                self.write_comment(field, m=m)
                if field["embed"]:
                    m.stmt(as_type(field["type"]))
                else:
                    m.stmt("{} {}".format(field["name"], as_type(field["type"])))
                if "tags" in field:
                    m.insert_after("  ")
                    for tag in field["tags"]:
                        m.insert_after(tag)
        return m

    def write_alias(self, alias, m=None):
        m = m or self.prestring_module()
        alias = alias.data
        m.type_alias(alias["name"], alias["original"]["value"])
        with m.const_group() as const:
            for c in alias.get("candidates", []):
                self.write_comment(c, m=const) or const.comment("{} : a member of {}".format(c["name"], alias["name"]))
                const("{} {} = {}".format(c["name"], alias["name"], c["value"]))
        return m

    def write_comment(self, target, m=None):
        m = m or self.prestring_module()
        if "comment" in target:
            m.comment(target["comment"])
            return m
        else:
            return None


def as_type(type_dict):
    kind = type_dict.get("kind", "primitive")
    if kind == "primitive":
        return type_dict["value"]
    elif kind == "pointer":
        return "*{}".format(as_type(type_dict["value"]))
    elif kind == "selector":
        return "{}".format(type_dict["value"])
    else:
        raise ValueError("unknown type: {}".format(type_dict))


class World(object):
    def __init__(self, parent=None, reader=None):
        self.parent = parent
        self.reader = reader
        self.modules = {}

    def read_module(self, name, module):
        self.modules[name] = self.reader.read_module(module, parent=self)

    def normalize(self):
        for module in self.modules.values():
            module.normalize()


class Module(object):
    def __init__(self, name, parent=None, reader=None):
        self.name = name
        self.parent = parent
        self.reader = reader
        self.files = {}

    def read_file(self, name, file):
        self.files[name] = self.reader.read_file(file, parent=self)

    def normalize(self):
        for files in self.files.values():
            files.normalize()


class File(object):
    def __init__(self, name, parent=None, reader=None):
        self.name = name
        self.parent = parent
        self.reader = reader
        self.aliases = {}
        self.structs = {}

    @property
    def package_name(self):
        if self.parent is None:
            return None
        return self.parent.name

    def normalize(self):
        for struct in self.structs.values():
            struct.normalize()
        for alias in self.aliases.values():
            alias.normalize()

    def read_alias(self, name, alias):
        self.aliases[name] = self.reader.read_alias(alias, parent=self)

    def read_struct(self, name, struct):
        self.structs[name] = self.reader.read_struct(struct, parent=self)

    def dump(self, writer):
        return writer.write_file(self)


class Alias(object):
    def __init__(self, name, data, parent=None, reader=None):
        self.name = name
        self.parent = parent
        self.reader = reader
        self.data = data

    def dump(self, writer):
        return writer.write_alias(self)

    def normalize(self):
        pass


class Struct(object):
    def __init__(self, name, data, parent=None, reader=None):
        self.name = name
        self.parent = parent
        self.reader = reader
        self.rawdata = data
        self.data = data

    def dump(self, writer):
        return writer.write_struct(self)

    def normalize(self):
        self.rawdata = copy.deepcopy(self.rawdata)
        for k in self.data.keys():
            self.data[k.lower()] = self.data.pop(k)


def main():
    fname = os.path.join(os.path.abspath(os.path.dirname(__file__)), "./models.json")
    writer = GOWriter()
    reader = Reader()
    with open(fname) as rf:
        data = json.load(rf)
        world = reader.read_world(data)
        world.normalize()
        # print(world)
        # print(world.modules["models"])
        # print(world.modules["models"].files["examples/models/person.go"])
        # print(world.modules["models"].files["examples/models/person.go"].structs["Person"])
        for name, file in world.modules["models"].files.items():
            outname = "output_{}".format(os.path.basename(file.name))
            logger.info("write %s", outname)
            print(file.dump(writer))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
```

output

```
package models

type Group struct {
	// ID : this is unique ID for persistent
	ID bson.ObjectId  `json:"id" bson:"_id"`
	Name string  `json:"name"`
}
package models

// Person : this is person model
type Person struct {
	Age int  `json:"age" bson:"age"`
	Group *Group  `json:"-"`
	GroupID *bson.ObjectId  `json:"groupId,omitempty" bson:"groupId"`
	// ID : this is unique ID for persistent
	ID bson.ObjectId  `json:"id" bson:"_id"`
	Name string  `json:"name" bson:"name"`
	Status PersonStatus  `json:"status" bson:"status"`
}

type PersonStatus string

const (
	PersonstatusHungry PersonStatus = "hungry"
	PersonstatusAngry PersonStatus = "angry"
	// PersonstatusHungry : maybe he or she is requesting something to eat
	// PersonstatusAngry : maybe he or she is angry
)
package models

type ArchiveFormat string

const (
	Tarball ArchiveFormat = "tarball"
	Zipball ArchiveFormat = "zipball"
	// Tarball : a member of ArchiveFormat
	// Zipball : a member of ArchiveFormat
)
```

examples/go/person.py

```python
from prestring.go import Module

m = Module()

m.package('main')

with m.import_group() as im:
    im('encoding/json')
    im("log", as_="logging")


m.type_alias('PersonStatus', 'string')
with m.const_group() as c:
    c('PersonHungry = PersonStatus("hungry")')
    c('PersonAngry = PersonStatus("angry")')

with m.type_('Person', 'struct'):
    m.stmt('Name string `json:"name"`')
    m.stmt('Age int `json:"age"`')
    m.stmt('Status PersonStatus `json:"status"`')


with m.func('main'):
    m.stmt('person := &Person{Name: "foo", Age: 20, Status: PersonHungry}')
    m.stmt('b, err := json.Marshal(person)')
    with m.if_("err != nil"):
        m.stmt('logging.Fatal(err)')
    m.stmt('logging.Println(string(b))')

print(m)
```

output

```
package main

import (
	"encoding/json"
	logging "log"
)

type PersonStatus string

const (
	PersonHungry = PersonStatus("hungry")
	PersonAngry = PersonStatus("angry")
)

type Person struct {
	Name string `json:"name"`
	Age int `json:"age"`
	Status PersonStatus `json:"status"`
}

func main()  {
	person := &Person{Name: "foo", Age: 20, Status: PersonHungry}
	b, err := json.Marshal(person)
	if err != nil  {
		logging.Fatal(err)
	}
	logging.Println(string(b))
}
```

examples/python/batch_mail.py

```python
# -*- coding:utf-8 -*-
import random
from datetime import datetime
from prestring import Module
m = Module()

m.stmt("========================================")
m.header = m.submodule()
m.stmt("========================================")
m.stmt("")
m.stmt("progress:")
m.progress = m.submodule()
m.stmt("----------------------------------------")
m.footer = m.submodule()

status = True
for i in range(10):
    v = random.random()
    m.progress.append("task{}: done ({})".format(i, v))
    if v > 0.7:
        m.progress.stmt(" F")
        status = False
        m.footer.append("{}, ".format(i))
    else:
        m.progress.stmt(" S")

m.header.append("[Success]" if status else "[Failure]")
m.header.stmt(" batch script ({})".format(datetime.now()))


print(str(m))
"""
========================================
[Failure] batch script (2015-10-20 15:40:42.208806)
========================================

progress:
task0: done (0.5611604727086437) S
task1: done (0.6576818372636405) S
task2: done (0.3459254985420931) S
task3: done (0.3123168020519609) S
task4: done (0.2264300461912806) S
task5: done (0.3765172681605966) S
task6: done (0.26508001623433797) S
task7: done (0.7826309508687302) F
task8: done (0.43771075231997414) S
task9: done (0.8992100765193392) F
----------------------------------------
7, 9,
"""
```

output

```
========================================
[Failure] batch script (2016-12-03 00:31:33.541010)
========================================

progress:
task0: done (0.6371787675394867) S
task1: done (0.033967246079762425) S
task2: done (0.9543477182751686) F
task3: done (0.5840952778982481) S
task4: done (0.0015167428683615647) S
task5: done (0.1554536793690794) S
task6: done (0.6276027820576783) S
task7: done (0.436119745372873) S
task8: done (0.5512452425253807) S
task9: done (0.8548636860168785) F
----------------------------------------
2, 9,
```

examples/python/cross_product.py

```python
# -*- coding:utf-8 -*-
from prestring.python import PythonModule

m = PythonModule()

with m.class_("Point", metaclass="InterfaceMeta"):
    with m.method("__init__", "value"):
        m.stmt("self.value = value")

    with m.method("__str__"):
        m.return_("self.value")


for n in range(1, 5):
    def rec(i):
        if i >= n:
            m.stmt("r.append(({}))".format(", ".join("x{}".format(j) for j in range(i))))
        else:
            with m.for_("x{}".format(i), "xs{}".format(i)):
                rec(i + 1)
    with m.def_("cross{}".format(n), *["xs{}".format(i) for i in range(n)]):
        m.stmt("r = []")
        rec(0)
        m.return_("r")

print(m)

# output
"""
class Point(object, metaclass=InterfaceMeta)
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


def cross1(xs0):
    r = []
    for x0 in xs0:
        r.append((x0))
    return r


def cross2(xs0, xs1):
    r = []
    for x0 in xs0:
        for x1 in xs1:
            r.append((x0, x1))
    return r


def cross3(xs0, xs1, xs2):
    r = []
    for x0 in xs0:
        for x1 in xs1:
            for x2 in xs2:
                r.append((x0, x1, x2))
    return r


def cross4(xs0, xs1, xs2, xs3):
    r = []
    for x0 in xs0:
        for x1 in xs1:
            for x2 in xs2:
                for x3 in xs3:
                    r.append((x0, x1, x2, x3))
    return r
"""
```

output

```
class Point(object, metaclass=InterfaceMeta):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value



def cross1(xs0):
    r = []
    for x0 in xs0:
        r.append((x0))
    return r


def cross2(xs0, xs1):
    r = []
    for x0 in xs0:
        for x1 in xs1:
            r.append((x0, x1))
    return r


def cross3(xs0, xs1, xs2):
    r = []
    for x0 in xs0:
        for x1 in xs1:
            for x2 in xs2:
                r.append((x0, x1, x2))
    return r


def cross4(xs0, xs1, xs2, xs3):
    r = []
    for x0 in xs0:
        for x1 in xs1:
            for x2 in xs2:
                for x3 in xs3:
                    r.append((x0, x1, x2, x3))
    return r
```

examples/python/poormans_fizzbuzz.py

```python
# -*- coding:utf-8 -*-
from prestring.python import PythonModule

m = PythonModule()


def fizzbuzz(i):
    r = []
    if i % 3 == 0:
        r.append("fizz")
    if i % 5 == 0:
        r.append("buzz")
    return "".join(r) if r else i


def genfizzbuzz(m, beg, end):
    def genfn():
        with m.def_("fizzbuzz", "n"):
            with m.if_("n == {}".format(beg)):
                m.return_(repr(fizzbuzz(beg)))

            for i in range(beg + 1, end + 1):
                with m.elif_("n == {}".format(i)):
                    m.return_(repr(fizzbuzz(i)))

            with m.else_():
                m.raise_("NotImplementedError('hmm')")

    def genmain():
        with m.main():
            m.import_("sys")
            m.stmt("print(fizzbuzz(int(sys.argv[1])))")
    genfn()
    genmain()
    return m


if __name__ == "__main__":
    import sys
    try:
        beg, end = sys.argv[1:]
    except ValueError:
        beg, end = 1, 100
    m = PythonModule()
    print(genfizzbuzz(m, int(beg), int(end)))
```

output

```
def fizzbuzz(n):
    if n == 1:
        return 1
    elif n == 2:
        return 2
    elif n == 3:
        return 'fizz'
    elif n == 4:
        return 4
    elif n == 5:
        return 'buzz'
    elif n == 6:
        return 'fizz'
    elif n == 7:
        return 7
    elif n == 8:
        return 8
    elif n == 9:
        return 'fizz'
    elif n == 10:
        return 'buzz'
    elif n == 11:
        return 11
    elif n == 12:
        return 'fizz'
    elif n == 13:
        return 13
    elif n == 14:
        return 14
    elif n == 15:
        return 'fizzbuzz'
    elif n == 16:
        return 16
    elif n == 17:
        return 17
    elif n == 18:
        return 'fizz'
    elif n == 19:
        return 19
    elif n == 20:
        return 'buzz'
    elif n == 21:
        return 'fizz'
    elif n == 22:
        return 22
    elif n == 23:
        return 23
    elif n == 24:
        return 'fizz'
    elif n == 25:
        return 'buzz'
    elif n == 26:
        return 26
    elif n == 27:
        return 'fizz'
    elif n == 28:
        return 28
    elif n == 29:
        return 29
    elif n == 30:
        return 'fizzbuzz'
    elif n == 31:
        return 31
    elif n == 32:
        return 32
    elif n == 33:
        return 'fizz'
    elif n == 34:
        return 34
    elif n == 35:
        return 'buzz'
    elif n == 36:
        return 'fizz'
    elif n == 37:
        return 37
    elif n == 38:
        return 38
    elif n == 39:
        return 'fizz'
    elif n == 40:
        return 'buzz'
    elif n == 41:
        return 41
    elif n == 42:
        return 'fizz'
    elif n == 43:
        return 43
    elif n == 44:
        return 44
    elif n == 45:
        return 'fizzbuzz'
    elif n == 46:
        return 46
    elif n == 47:
        return 47
    elif n == 48:
        return 'fizz'
    elif n == 49:
        return 49
    elif n == 50:
        return 'buzz'
    elif n == 51:
        return 'fizz'
    elif n == 52:
        return 52
    elif n == 53:
        return 53
    elif n == 54:
        return 'fizz'
    elif n == 55:
        return 'buzz'
    elif n == 56:
        return 56
    elif n == 57:
        return 'fizz'
    elif n == 58:
        return 58
    elif n == 59:
        return 59
    elif n == 60:
        return 'fizzbuzz'
    elif n == 61:
        return 61
    elif n == 62:
        return 62
    elif n == 63:
        return 'fizz'
    elif n == 64:
        return 64
    elif n == 65:
        return 'buzz'
    elif n == 66:
        return 'fizz'
    elif n == 67:
        return 67
    elif n == 68:
        return 68
    elif n == 69:
        return 'fizz'
    elif n == 70:
        return 'buzz'
    elif n == 71:
        return 71
    elif n == 72:
        return 'fizz'
    elif n == 73:
        return 73
    elif n == 74:
        return 74
    elif n == 75:
        return 'fizzbuzz'
    elif n == 76:
        return 76
    elif n == 77:
        return 77
    elif n == 78:
        return 'fizz'
    elif n == 79:
        return 79
    elif n == 80:
        return 'buzz'
    elif n == 81:
        return 'fizz'
    elif n == 82:
        return 82
    elif n == 83:
        return 83
    elif n == 84:
        return 'fizz'
    elif n == 85:
        return 'buzz'
    elif n == 86:
        return 86
    elif n == 87:
        return 'fizz'
    elif n == 88:
        return 88
    elif n == 89:
        return 89
    elif n == 90:
        return 'fizzbuzz'
    elif n == 91:
        return 91
    elif n == 92:
        return 92
    elif n == 93:
        return 'fizz'
    elif n == 94:
        return 94
    elif n == 95:
        return 'buzz'
    elif n == 96:
        return 'fizz'
    elif n == 97:
        return 97
    elif n == 98:
        return 98
    elif n == 99:
        return 'fizz'
    elif n == 100:
        return 'buzz'
    else:
        raise NotImplementedError('hmm')


if __name__ == "__main__":
    import sys
    print(fizzbuzz(int(sys.argv[1])))
```

examples/python/submodule_sample.py

```python
# -*- coding:utf-8 -*-
from prestring.python import PythonModule

m = PythonModule()

with m.def_("setup", "config"):
    import_area = m.submodule()
    m.sep()
    for k in ["a", "b", "c", "d", "e"]:
        import_area.from_(".plugins", "{}_plugin".format(k))
        m.stmt("config.activate({}_plugin)", k)


print(m)
"""
def setup(config):
    from .plugins import(
        a_plugin,
        b_plugin,
        c_plugin,
        d_plugin,
        e_plugin
    )

    config.activate(a_plugin)
    config.activate(b_plugin)
    config.activate(c_plugin)
    config.activate(d_plugin)
    config.activate(e_plugin)
"""
```

output

```
def setup(config):
    from .plugins import(
        a_plugin,
        b_plugin,
        c_plugin,
        d_plugin,
        e_plugin
    )

    config.activate(a_plugin)
    config.activate(b_plugin)
    config.activate(c_plugin)
    config.activate(d_plugin)
    config.activate(e_plugin)
```

