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
