SUBCOMMANDS = "" $(shell yana --help | egrep -o "\{(.*)\}" | head -n1 | \
							tr -d \{\} | tr "," " ")
USAGE_FILE = USAGE.rst

pylint:
	pylint yana lib plugins

usage:
	echo ".. this file is auto generated by \`make usage\`" > ${USAGE_FILE}; \
	echo >> ${USAGE_FILE}; \
	echo .. contents:: >> ${USAGE_FILE}; \
	for s in ${SUBCOMMANDS}; do \
		echo; \
		echo yana $$s --help; \
		echo yana $$s --help | sed -r 's/./=/g'; \
		echo; \
		echo ::; \
		echo; \
		yana $$s --help | sed -e 's/^/  /'; \
		echo; \
	done >> ${USAGE_FILE}
