all: pypi

pypi: lblsolve/*.py requirements.txt README.md setup.py
	[ -d venv ] || python -m venv venv
	. venv/bin/activate
	pip install -r requirements.txt --upgrade
	rm -rf dist/
	python setup.py sdist bdist_wheel

publish_test: dist/
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish_prod: dist/
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

clean:
	rm -rf dist
