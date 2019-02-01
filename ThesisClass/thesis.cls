%!TEX root = /Users/jeremy/Documents/Writing Projects/Master's Thesis/example.tex

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Document Class: thesis
%% Created By: Jeremy West - April 17, 2009
%% Updated July 21, 2015 to support inverted pyramid titles

%% Packages, classes, and options
\NeedsTeXFormat{LaTeX2e}[1995/06/01]
\ProvidesClass{thesis}[2009/04/16 v1.0 LaTeX document class for theses]
\newcommand{\sides}{oneside}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\DeclareOption{oneside}{%
	\renewcommand{\sides}{oneside}
}
\DeclareOption{twoside}{%
	\renewcommand{\sides}{twoside}
}
\DeclareOption{twocolumn}{%
	\PackageWarning{thesis}{Option not supported `twocolumn'}
}
\ExecuteOptions{oneside}
\ProcessOptions
\LoadClass[\sides]{book}
\widowpenalty=1000
\clubpenalty=1000

% Add support for an index, math stuff, and spacing control
\RequirePackage{makeidx, amsmath, amsfonts, amssymb, amsthm, setspace}
\usepackage{tocbibind}

\newcommand{\indext}[1]{\index{#1@\texttt{#1}}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Basic document formatting

% turn on double spacing for the paper
\doublespacing

% save the paper lengths so they can be restored at any time
\newcommand{\setpaperlengths}{%

	% Horizontal lengths
	\setlength{\textwidth}{6.5in}
	\setlength{\oddsidemargin}{0in}%
	\setlength{\evensidemargin}{0in}%
	\setlength{\marginparwidth}{0in}%
	\setlength{\marginparsep}{0in}%
	% Vertical lengths
	\setlength{\topmargin}{-.2in}%
	\setlength{\headheight}{0in}%
	\setlength{\headsep}{0in}%
	\setlength{\footskip}{3em}%
	\setlength{\textheight}{9.1in}
}
\setpaperlengths

% Set footnote styles
\renewcommand{\thefootnote}{\arabic{footnote}}

% set the custom header styles

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Additional Document Parameters
\newcommand{\degree}[1]{\def\@degree{#1}}\degree{***DEGREE***}
\newcommand{\university}[1]{\def\@university{#1}}\university{***UNIVERSITY***}
\newcommand{\department}[1]{\def\@department{#1}}\department{***DEPARTMENT***}
\newcommand{\committeechair}[1]{\def\@committeechair{#1}}\committeechair{***COMMITTEE CHAIR***}
\newcommand{\memberA}[1]{\def\@memberA{#1}}
\memberA{***MEMBER1***}
\newcommand{\memberB}[1]{\def\@memberB{#1}}
\memberB{***MEMBER1***}
\newcommand{\memberC}[1]{\def\@memberC{#1}}
\memberC{***MEMBER1***}
\newcommand{\memberD}[1]{\def\@memberD{#1}}
\memberD{***MEMBER1***}
\newcommand{\keywords}[1]{\def\@keywords{#1}}\keywords{***KEYWORDS***}
\newcommand{\subject}[1]{\def\@subject{#1}}\subject{***SUBJECT***}
\renewcommand{\month}[1]{\def\@month{#1}}\month{***MONTH***}
\renewcommand{\year}[1]{\def\@year{#1}}\year{***YEAR***}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Support PDF Bookmarks
% Call \pdfbookmarks in the preamble of the document to turn on PDF bookmarks

%% This command is a place-holder. If bookmarks are turned on, it is recplaced with a 
%% command that actually places the specified bookmark. Otherwise, it does nothing
\newcommand{\placebookmark}[2]{%
	\pdfbookmark[0]{#1}{#2}%
}

\newcommand{\pdfbookmarks}{%
\usepackage[pdfborder={0 0 0},
	pdftitle={\@title}, 
	pdfauthor={\@author}, 
	pdfsubject={\@subject},
	pdfkeywords={\@keywords},
	pdfcreator={\@author},
	pdfproducer={LaTeX}
	pdftex, 
	bookmarks=true, 
	bookmarksnumbered=true,
	pdfdisplaydoctitle=true]{hyperref}
	}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Document section formatting (numbering, headers for standard pages)
\let\oldfrontmatter\frontmatter
\renewcommand{\frontmatter}{%
	\pagestyle{plain}\oldfrontmatter
}

\let\oldmainmatter\mainmatter
\renewcommand{\mainmatter}{%
	\pagestyle{plain}\oldmainmatter
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Chapter Headers

%\newcommand{\chapformat}{\large\scshape}
\newcommand{\chapformat}{\large\scshape}

\renewcommand\chapter{%
                    \vspace{5ex}
                    \global\@topnum\z@
                    \@afterindentfalse
                    \secdef\@chapter\@schapter}
\def\@chapter[#1]#2{\ifnum \c@secnumdepth >\m@ne
                       \if@mainmatter
                         \refstepcounter{chapter}%
                         \typeout{\@chapapp\space\thechapter.}%
                         \addcontentsline{toc}{chapter}%
                                   {\protect\numberline{\thechapter}#1}%
                       \else
                         \addcontentsline{toc}{chapter}{#1}%
                       \fi
                    \else
                      \addcontentsline{toc}{chapter}{#1}%
                    \fi
                    \chaptermark{#1}%
                    \addtocontents{lof}{\protect\addvspace{10\p@}}%
                    \addtocontents{lot}{\protect\addvspace{10\p@}}%
                    \if@twocolumn
                      \@topnewpage[\@makechapterhead{#2}]%
                    \else
                      \@makechapterhead{#2}%
                      \@afterheading
                    \fi}

\renewcommand{\@makechapterhead}[1]{%
  %\vspace*{4\p@}%
  \vbox{%
  \centering
  \parindent=0pt
  \leftskip=0pt plus.5fil
  \rightskip=0pt plus-0.5fil
  \parfillskip=0pt plus1fil
  %\emergencystretch=1in
  \parshape7
  1.0in 4.7in
  1.0in 4.50in
  1.25in 4.00in
  1.50in 3.50in
  1.75in 3.00in
  2.00in 2.50in
  2.25in 2.00in
  \strut
  \normalfont
    \ifnum \c@secnumdepth >\m@ne
      \if@mainmatter
        \chapformat \@chapapp\space \thechapter.
      \fi
    \fi
    \interlinepenalty\@M
    \chapformat #1\par\nobreak
    \vskip 15\p@
  }}

\renewcommand{\@makeschapterhead}[1]{%
  %\vspace*{4\p@}%
  {\parindent \z@ \centering \normalfont
    \interlinepenalty\@M
    \chapformat  #1\par\nobreak
    \vskip 15\p@
  }}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Section Headers

% this actually creates the section header
\newcommand{\makesection}[2]{%
	\@startsection{section}{#1}%
		{\z@}%  Indentation from left margin
		{-4ex}%  Skip above. Negative supresses paragraph indent of content
		{2ex}%  Space between heading and content, negative means on the same line
		{\normalfont\large\scshape}{#2}% Formatting of header
}

% this determines if the section header should or should not be numbered.
\renewcommand{\section}{\@ifstar{\makesection{10}}{\makesection{1}}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Subsection Headers

\newcommand\makesubsection[2]{%
	\@startsection{subsection}{#1}%
		{\z@}%  Indentation from left margin
		{-3ex}%  Skip above. Negative supresses paragraph indent of content
		{-1em}%  Space between heading and content, negative means on the same line
		{\normalfont\normalsize\bfseries}{#2.}% Formatting of header
}

\renewcommand{\subsection}{\@ifstar{\makesubsection{10}}{\makesubsection{2}}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Subsubsection Headers

\newcommand{\makesubsubsection}[2]{%
	\@startsection{subsubsection}{#1}%
		{\parindent}%  Indentation from left margin
		{\z@}%  Skip above. Negative supresses paragraph indent of content
		{-0.5em}%  Space between heading and content, negative means on the same line
		{\normalfont\normalsize\bfseries}{#2.}% Formatting of header
}

\renewcommand{\subsubsection}{\@ifstar{\makesubsubsection{10}}{\makesubsubsection{3}}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Paragraph Headers

\newcommand{\makeparagraph}[2]{%
	\@startsection{paragraph}{#1}%
		{\parindent}%  Indentation from left margin
		{\z@}%  Skip above. Negative supresses paragraph indent of content
		{-0.5em}%  Space between heading and content, negative means on the same line
		{\normalfont\normalsize\slshape\bfseries}{#2.}% Formatting of header
}

\renewcommand{\paragraph}{\@ifstar{\makeparagraph{10}}{\makeparagraph{4}}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Subparagraph Headers

\newcommand{\makesubparagraph}[2]{%
	\@startsection{subparagraph}{#1}%
		{\parindent}%  Indentation from left margin
		{\z@}%  Skip above. Negative supresses paragraph indent of content
		{-0.5em}%  Space between heading and content, negative means on the same line
		{\normalfont\normalsize\slshape}{#2.}% Formatting of header
}

\renewcommand{\subparagraph}{\@ifstar{\makesubparagraph{10}}{\makesubparagraph{5}}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Title Page
\renewcommand{\maketitle}{%
	%% Place a PDF bookmark (remember, this only does something if turned on)
	\cleardoublepage
	\placebookmark{Title Page}{user-title-page}
	\pagestyle{empty}
	\begin{center}
		\mbox{}\vskip .0in
		{\@title}\\
		\vfill\vfil%\vfill
		%by\\[2ex]
		{\@author}
		\vfill%\vfill\vfill
      \singlespacing
		A project submitted to the faculty of \\
		\@university \\
		in partial fulfillment of the requirements for the degree of\\[4mm]
		%\vfill
		\@degree
		\vfill%\vfill
    \@committeechair, Chair\\
    \@memberA\\
    \@memberB\\
    %\@memberC\\
    %\@memberD
       \vfill
       \doublespacing
		\@department \\
		\@university \\
		%\@month\ \@year\\
       \vfill%\vfill\vfill
       Copyright \copyright\ \@year\ \@author\ \\
       All Rights Reserved
	\end{center}
	\cleardoublepage
	\pagestyle{plain}
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Abstract

\newenvironment{abstract}{% Opening Code
	\cleardoublepage
	\singlespacing
	\chapter*{abstract}
	\placebookmark{Abstract}{user-abstract}
	\pagestyle{empty}
	\begin{center}
		%\bigskip
		\@title\\
		\bigskip
		\@author\\
		\@department , BYU\\
		\@degree
	\end{center}
}{ %
    \cleardoublepage
	\pagestyle{plain}
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Acknowledgements

\newenvironment{acknowledgments}{%
	\cleardoublepage
	\chapter*{Acknowledgments}
	\placebookmark{Acknowledgments}{user-acknowledgments}
	\pagestyle{empty}
}{%
	\cleardoublepage
	\pagestyle{plain}
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% OPTIONAL SIGNATURE PAGE

\newcommand{\member}[1]{%
	\noindent\rule{.4\textwidth}{0.1pt}%
	\hspace{.05\textwidth}%
	\rule{.5\textwidth}{0.1pt}\\
	\parbox{.45\textwidth}{Date}%
	\parbox[t]{.5\textwidth}{#1}%
	\vfill\vfill\vfill
}

\newenvironment{committee}{%
	\cleardoublepage
	%\placebookmark{Graduate Committee Approval}{user-grad-comm-approval}
	% Create the \member command, then create the intro title page portion
	\pagestyle{empty}
	\begin{center}
		\mbox{}\vfill\vfill
		\MakeUppercase\@university \\
		\vfill\vfill
		SIGNATURE PAGE
		\vfill\vfill\vfill
		of a thesis submitted by \\
		\@author
		\vfill
	\end{center}
	\singlespacing
The thesis of \@author\ is acceptable in its final form including (1) its format, citations, and bibliographical style are consistent and acceptable and fulfill university and department style requirements; (2) its illustrative materials including figures, tables, and charts are in place; and (3) the final manuscript is satisfactory and ready for submission.
	\vfill\vfill
	\member{\@committeechair, Chair}
}{% Close the titlepage environment
	\doublespacing
	\cleardoublepage
	\pagestyle{plain}
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Table of Contents
\setcounter{secnumdepth}{2}
\setcounter{tocdepth}{1}

\let\oldtableofcontents\tableofcontents

\renewcommand{\tableofcontents}{%
	\cleardoublepage
	%\placebookmark{Table of Contents}{user-table-of-contents}
	\oldtableofcontents
	\cleardoublepage
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% List of Tables

\let\oldlistoftables\listoftables

\renewcommand{\listoftables}{%
	\cleardoublepage
	%\placebookmark{List of Tables}{user-list-of-tables}
	\oldlistoftables
	\cleardoublepage
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% List of Figures

\let\oldlistoffigures\listoffigures

\renewcommand{\listoffigures}{%
	\cleardoublepage
	%\placebookmark{List of Figures}{user-list-of-figures}
	\oldlistoffigures
	\cleardoublepage
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Bibliography

\let\oldbibliography\bibliography

\renewcommand{\bibliography}[1]{%
	\cleardoublepage
	\singlespacing
%	\placebookmark{References}{user-references}
	\oldbibliography{#1}
	\cleardoublepage
	\doublespacing
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Index

\let\oldprintindex\printindex

\renewcommand{\printindex}{%
	\cleardoublepage
	\singlespacing
	\placebookmark{Index}{user-index}
	\oldprintindex
	\cleardoublepage
	\doublespacing
}

