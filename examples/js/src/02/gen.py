from prestring.js import Module

m = Module()

with m.class_("ArrayLike"):
    with m.method("constructor", items="[]"):
        m.stmt("this._items = items")

    with m.method("get items"):
        m.return_("this._items")

    with m.method("set items", "newLength"):
        m.stmt("const currentItemLength = this.items.length")
        with m.if_("newLength < currentItemLength"):
            m.stmt("this._items = this.items.slice(0, newLength)")
        with m.elif_("newLength > currentItemLength"):
            m.stmt("this._items = this.items.concat(new Array(newLength - currentItemLength))")

m.stmt("const arrayLike = new ArrayLike([1, 2, 3, 4, 5])")
m.sep()
m.stmt("arrayLike.length = 2")
m.stmt("console.log(arrayLike.items.join(', '))", comment="=> '1, 2'")
m.sep()
m.stmt("arrayLike.length = 5")
m.stmt("console.log(arrayLike.items.join(', '))", comment="=> '1, 2, , ,'")

with m.class_("ArrayWrapper"):
    with m.method("consutructor", array="[]"):
        m.stmt("this.array = array")

    with m.method("static of", "...items"):
        m.return_("new ArrayWrapper(items)")

    with m.method("get length"):
        m.return_("this.array.length")

m.stmt("arrayWrapperA = new ArrayWrapper([1, 2, 3])")
m.sep()
m.stmt("arrayWrapperB = ArrayWrapper.of(1, 2, 3)")
m.stmt("console.log(arrayWrapperA.length)", comment="=> 3")
m.stmt("console.log(arrayWrapperB.length)", comment="=> 3")
m.sep()

with m.class_("MyArray", "Array"):
    with m.method("get first"):
        with m.if_("this.length === 0"):
            m.return_("undefined")
        with m.else_():
            m.return_("this[0]")

    with m.method("get last"):
        with m.if_("this.length === 0"):
            m.return_("undefined")
        with m.else_():
            m.return_("this[this.length - 1]")

print(m)
