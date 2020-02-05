# type: ignore
import unittest
from collections import namedtuple


class TestDigs(unittest.TestCase):
    def test_it(self):
        from prestring.minifs._glob import _fix, _dig, STAR

        C = namedtuple("C", "msg, path, want")

        d = {"a": {"b": {"c": {"d": "ok"}}, "z": {"d": "zok"}}}

        cases = [
            C(
                msg="path0",
                path=["a"],
                want=[(["a"], {"b": {"c": {"d": "ok"}}, "z": {"d": "zok"}}, True)],
            ),
            C(
                msg="path1",
                path=["a", "b"],
                want=[(["a", "b"], {"c": {"d": "ok"}}, True)],
            ),
            C(
                msg="path2",
                path=["a", "b", "c"],
                want=[(["a", "b", "c"], {"d": "ok"}, True)],
            ),
            C(
                msg="path3",
                path=["a", "b", "c", "d"],
                want=[(["a", "b", "c", "d"], "ok", True)],
            ),
            C(
                msg="path-ng3",
                path=["a", "b", "c", "e"],
                want=[(["a", "b", "c"], {"d": "ok"}, False)],
            ),
            C(
                msg="path-ng4",
                path=["a", "x"],
                want=[(["a"], {"b": {"c": {"d": "ok"}}, "z": {"d": "zok"}}, False)],
            ),
            # *
            C(
                msg="star1",
                path=["a", "b", STAR, "d"],
                want=[(["a", "b", "c", "d"], "ok", True)],
            ),
            C(
                msg="star2",
                path=["a", STAR, "c"],
                want=[
                    (["a", "b", "c"], {"d": "ok"}, True),
                    (["a", "z"], {"d": "zok"}, False),
                ],
            ),
            C(
                msg="star3",
                path=["a", STAR, "d"],
                want=[
                    (["a", "b"], {"c": {"d": "ok"}}, False),
                    (["a", "z", "d"], "zok", True),
                ],
            ),
            C(
                msg="star4",
                path=["a", STAR, STAR],
                want=[
                    (["a", "b", "c"], {"d": "ok"}, True),
                    (["a", "z", "d"], "zok", True),
                ],
            ),
        ]

        for c in cases:
            with self.subTest(msg=c.msg):
                got = _fix(_dig(d, c.path))
                self.assertEqual(got, c.want)


class TestGlobs(unittest.TestCase):
    def test_it(self):
        from prestring.minifs._glob import glob

        C = namedtuple("C", "query,  want")

        d = {
            "projects": {
                "xx.py": "ok",
                "yy.txt": "ng",
                "sub": {"a.txt": "aaa", "b.py": "bbb"},
            }
        }

        cases = [
            C(query="*.py", want=[]),
            C(query="*.txt", want=[]),
            C(query="projects/*.py", want=[("projects/xx.py", "ok")]),
            C(query="projects/*.txt", want=[("projects/yy.txt", "ng")]),
            C(query="*/*.py", want=[("projects/xx.py", "ok")]),
            C(query="*/*.txt", want=[("projects/yy.txt", "ng")]),
            C(
                query="**/*.py",
                want=[("projects/xx.py", "ok"), ("projects/sub/b.py", "bbb")],
            ),
            C(
                query="projects/**/*.py",
                want=[("projects/xx.py", "ok"), ("projects/sub/b.py", "bbb")],
            ),
            C(
                query="projects/**/*.txt",
                want=[("projects/yy.txt", "ng"), ("projects/sub/a.txt", "aaa")],
            ),
        ]

        for c in cases:
            with self.subTest(msg=c.query):
                got = list(glob(d, c.query))
                self.assertEqual(got, c.want)
