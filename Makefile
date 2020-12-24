clean:
	rm -rf dist/*

upload:
	python setup.py sdist bdist_wheel
	twine upload dist/*
