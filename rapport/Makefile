# Compilation du rapport de stage
#
#   make          compile le PDF
#   make clean    supprime les fichiers auxiliaires
#   make propre   supprime aussi le PDF
#   make verif    signale les avertissements typographiques restants

CIBLE = main

.PHONY: all clean propre verif

all: $(CIBLE).pdf

$(CIBLE).pdf: $(CIBLE).tex preambule.tex pagedegarde.tex chapitres/*.tex bibliographie.bib
	latexmk -pdf -interaction=nonstopmode $(CIBLE).tex

clean:
	latexmk -c
	rm -f chapitres/*.aux

propre:
	latexmk -C
	rm -f chapitres/*.aux

verif: $(CIBLE).pdf
	@echo "Débordements de ligne : $$(grep -c Overfull $(CIBLE).log)"
	@echo "Références indéfinies :"
	@grep -E "LaTeX Warning: (Reference|Citation)" $(CIBLE).log | sort -u || echo "  aucune"
	@grep -oE "Output written on $(CIBLE).pdf \([0-9]+ pages" $(CIBLE).log
