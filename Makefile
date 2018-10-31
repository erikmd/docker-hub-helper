all::
	$(info Run "make doc" to auto-generate the usage section in README.md)

doc::
	export COLUMNS=80 && ./update-usage.pl && git diff
