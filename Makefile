all: pdf clean

pdf: cvrp.tex
	pdflatex cvrp.tex

clean:
	rm -f *.aux *.log *.out

