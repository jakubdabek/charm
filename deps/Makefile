include ../config.mk

# relic openssl pbc
DIRS:=relic pbc
CLEAN_DIRS:=$(addsuffix _clean,$(DIRS))

.PHONY: all clean $(DIRS) $(CLEAN_DIRS)

all: $(DIRS)

$(DIRS):
	$(MAKE) -C $@

clean: $(CLEAN_DIRS)
	rm -rf root

$(CLEAN_DIRS):
	$(MAKE) -C $(patsubst %_clean,%,$@) clean
