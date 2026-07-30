.PHONY: all book check site-assets site check-site clean

all: check check-site

book:
	./scripts/build-book.sh

check: book
	./scripts/check-pdf.sh build/main.pdf

site-assets: book
	./scripts/generate-site-assets.py

site: book
	./scripts/build-site.sh

check-site: site
	./scripts/check-site.sh

clean:
	./scripts/clean.sh
