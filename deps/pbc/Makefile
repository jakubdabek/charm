.PHONY: all clean distclean

include ../../config.mk

VERSION := 0.5.14
LIBPBC := pbc-${VERSION}

all: ${LIBPBC}.tar.gz ${LIBPBC}/.built

${LIBPBC}/.built: ${LIBPBC}
	@echo "[+] Building ${LIBPBC}"
	cd $< && ./configure --prefix=$(prefix)
	$(MAKE) -C $<
	$(MAKE) -C $< install
	touch $@

${LIBPBC}: ${LIBPBC}.tar.gz
	tar -xf $^

${LIBPBC}.tar.gz:
	./download_libpbc.sh ${VERSION}

clean:
	rm -rf ${LIBPBC}

distclean:
	rm -rf ${LIBPBC} ${LIBPBC}.tar.gz
