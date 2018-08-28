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
