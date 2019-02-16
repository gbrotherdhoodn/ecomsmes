build:
	python3.6 setup.py sdist bdist_wheel


upload:
	twine upload --repository-url $(url) -u $(username) -p $(pass) dist/*


clean:
	pip3 uninstall --yes bisma-pos
	rm -fR .cache/ .eggs/  build/ dist/ *.egg-info MANIFEST static reports


local-install: clean build
	pip3 install dist/*.whl


test: local-install
	PYTHON_PATH=$PWD/src python3 src/manage.py behave


lint:
	pylint src/bisma features/steps/*.py


