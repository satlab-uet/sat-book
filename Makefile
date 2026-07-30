.PHONY: all book check site-assets site check-site clean

all: check-site

book:
	./scripts/build-book.sh

check: book
	./scripts/check-pdf.sh build/main.pdf

site-assets: check
	./scripts/generate-site-assets.py

site: check
	./scripts/build-site.sh

check-site: site
	./scripts/check-site.sh

clean:
	./scripts/clean.sh
