SUBCOMMANDS = "" $(shell yana --help | egrep -o "\{(.*)\}" | head -n1 | \
							tr -d \{\} | tr "," " ")

pylint:
	pylint yana lib sub_commands finders

readme:
	for s in ${SUBCOMMANDS}; do \
		echo; \
		echo yana $$s --help; \
		echo yana $$s --help | sed -r 's/./=/g'; \
		echo; \
		yana $$s --help; \
		echo; \
	done > README.rst
