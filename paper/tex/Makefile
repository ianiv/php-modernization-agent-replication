# Build the paper: requires TeX Live with pgfplots, listings, natbib, booktabs (e.g. Debian texlive-latex-extra + texlive-pictures).
main.pdf: main.tex refs.bib
	latexmk -pdf -interaction=nonstopmode main.tex
clean:
	latexmk -C
