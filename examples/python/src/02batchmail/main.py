import random
from datetime import datetime
from prestring import Module


random.seed(1)
now = lambda: datetime(2000, 1, 1)
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
m.header.stmt(" batch script ({})".format(now()))


print(str(m))
"""
========================================
[Failure] batch script (2000-01-01 00:00:00)
========================================

progress:
task0: done (0.13436424411240122) S
task1: done (0.8474337369372327) F
task2: done (0.763774618976614) F
task3: done (0.2550690257394217) S
task4: done (0.49543508709194095) S
task5: done (0.4494910647887381) S
task6: done (0.651592972722763) S
task7: done (0.7887233511355132) F
task8: done (0.0938595867742349) S
task9: done (0.02834747652200631) S
----------------------------------------
1, 2, 7,
"""
