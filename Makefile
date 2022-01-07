all: pypi

pypi: lblsolve/*.py requirements.txt README.md setup.py
	. venv/bin/activate
	rm -rf dist/
	python setup.py sdist bdist_wheel

publish_test: dist/
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish_prod: dist/
	twine upload --repository-url https://pypi.org/legacy/ dist/*

clean:
	rm -rf dist