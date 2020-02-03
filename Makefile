.DEFAULT_GOAL := develop

develop:
	/usr/bin/env python3 setup.py develop

install:
	/usr/bin/env python3 setup.py install

zipapp:
	shiv --compressed -o pygluu-kubernetes.pyz -p '/usr/bin/env python3' -e pygluu.kubernetes.create:main . -r requirements.txt --no-cache
