# Portfolio LaTeX · N'solé Samson Yamontche

Site : **<https://samsonyamontchensolegit.github.io>**

Portfolio d'un expert LaTeX : mise en forme de thèses, diagrammes TikZ, bibliographies et projets Overleaf.
Le site est statique (HTML, CSS, JavaScript), bilingue (français / anglais), avec un mode clair et un mode sombre.

*English: portfolio of a LaTeX expert (thesis formatting, TikZ diagrams, bibliographies, Overleaf projects). Static, bilingual site with light and dark modes.*

## Projets de démonstration

Documents réalisés pour illustrer le travail, avec le code source complet. Les données sont calculées ou synthétiques, pas mesurées. Les noms d'auteur, d'université et de jury sont des exemples.

| Projet | Contenu | PDF | Source |
|---|---|---|---|
| Modèle de mémoire de master | 21 pages en français, KOMA-Script, biblatex, TikZ, pgfplots | [PDF](projects/thesis-template/main.pdf) | [dossier](projects/thesis-template) |
| Article scientifique | Deux colonnes, théorème, algorithme, tableau, figure | [PDF](projects/scientific-article/main.pdf) | [dossier](projects/scientific-article) |
| Présentation de soutenance | 11 diapositives Beamer 16:9, thème personnalisé | [PDF](projects/beamer-defense/main.pdf) | [dossier](projects/beamer-defense) |
| Galerie de diagrammes TikZ | Six figures vectorielles, TikZ et tikz-cd | [PDF](projects/tikz-gallery/main.pdf) | [dossier](projects/tikz-gallery) |
| Visualisation de données | Six graphiques pgfplots lus depuis des fichiers CSV | [PDF](projects/pgfplots-dataviz/main.pdf) | [dossier](projects/pgfplots-dataviz) |

## Compiler un projet

Chaque dossier de `projects/` contient un `main.tex` et les fichiers dont il dépend. Avec une distribution TeX Live récente :

```bash
cd projects/thesis-template
latexmk -pdf main.tex
```

Le mémoire, l'article et la présentation utilisent `biber` pour la bibliographie ; `latexmk` l'appelle automatiquement.
Pour régénérer les données de `projects/pgfplots-dataviz`, exécuter `generate_data.ps1` (PowerShell).

## Structure

```
index.html, style.css, script.js   site du portfolio
projects/<nom>/main.tex            source LaTeX du projet
projects/<nom>/main.pdf            PDF compilé
projects/<nom>/preview.png         aperçu affiché sur le site
```

## Contact

- Upwork : <https://www.upwork.com/freelancers/~01fd37c12968c7e43a>
- LinkedIn : <https://www.linkedin.com/in/n-sol%C3%A9-samson-yamontche-1b8328349>
- E-mail : samsonyamontchensolegit@gmail.com
