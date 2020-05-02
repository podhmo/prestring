from prestring.go import Module

m = Module()

m.package('main')

with m.import_group() as im:
    im('encoding/json')
    im("log", as_="logging")


m.new_type('PersonStatus', 'string')
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
