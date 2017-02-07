all: mo

mo: *.py Makefile
	# Why not use 'git archive' here? Because for some reason python won't accept
	# the zip files it generates.
	bash -c "cat <(echo '#!/usr/bin/env python2') <(zip - *.py) > mo"
	chmod a+x mo
