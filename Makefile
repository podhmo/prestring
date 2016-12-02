example:
	touch _tmp
	for i in `find examples -name "*.py" | grep -v gen.py`; do echo $$i >> _tmp; echo '\n```python' >> _tmp; cat $$i >> _tmp; echo '```\n' >> _tmp; echo "output" >> _tmp; echo '\n```' >> _tmp; python $$i >> _tmp; echo '```\n' >> _tmp; done
	mv _tmp examples.md
