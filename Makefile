test:
	pytest
lint:
	flake8
typecheck:
	mypy
formatcheck:
	black --check .

qa:
	make -s formatcheck
	make -s lint
	make -s typecheck
	make -s test
