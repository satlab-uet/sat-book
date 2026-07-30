.PHONY: all book check clean

all: check

book:
	./scripts/build-book.sh

check: book
	./scripts/check-pdf.sh build/main.pdf

clean:
	./scripts/clean.sh
