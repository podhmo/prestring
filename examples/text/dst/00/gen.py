from prestring.text import Module


def gen(*, m=None, indent='  '):
    m = m or Module(indent=indent)

    m.stmt('<!DOCTYPE html>')
    m.stmt('<!-- from https://gist.github.com/ocean90/1268328 -->')
    m.stmt('<html>')
    with m.scope():
        m.stmt('<head>')
        with m.scope():
            m.stmt('<title>Box Shadow</title>')
            m.sep()
            m.stmt('<style>')
            with m.scope():
                m.stmt('.box {')
                with m.scope():
                    m.stmt('height: 150px;')
                    m.stmt('width: 300px;')
                    m.stmt('margin: 20px;')
                    m.stmt('border: 1px solid #ccc;')
                m.stmt('}')
                m.sep()
                m.stmt('.top {')
                with m.scope():
                    m.stmt('box-shadow: 0 -5px 5px -5px #333;')
                m.stmt('}')
                m.sep()
                m.stmt('.right {')
                with m.scope():
                    m.stmt('box-shadow: 5px 0 5px -5px #333;')
                m.stmt('}')
                m.sep()
                m.stmt('.bottom {')
                with m.scope():
                    m.stmt('box-shadow: 0 5px 5px -5px #333;')
                m.stmt('}')
                m.sep()
                m.stmt('.left {')
                with m.scope():
                    m.stmt('box-shadow: -5px 0 5px -5px #333;')
                m.stmt('}')
                m.sep()
                m.stmt('.all {')
                with m.scope():
                    m.stmt('box-shadow: 0 0 5px #333;')
                m.stmt('}')
            m.stmt('</style>')
        m.stmt('</head>')
        m.stmt('<body>')
        with m.scope():
            m.stmt('<div class="box top">top</div>')
            m.stmt('<div class="box right">right</div>')
            m.stmt('<div class="box bottom">bottom</div>')
            m.stmt('<div class="box left">left</div>')
            m.stmt('<div class="box all">all</div>')
        m.stmt('</body>')
    m.stmt('</html>')
    return m


if __name__ == "__main__":
    m = gen(indent='  ')
    print(m)
