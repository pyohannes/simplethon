#### +                                                                          
#```((mode docu) (post ("replace-variables")))                                  
#\section{\tc{``(file-basename)``}: Parsing Simplethon code}                    
#                                                                               
# The first step in the Simplethon compiling workflow is parsing.  In this step  
# Simplethon source code is transformed into an abstract syntax tree (AST), which 
# was described in the previous section~\ref{sec:sthast}. All Simplethon AST    
# elements are imported to be used later on to build the tree.                  
#```                                                                            
from sth.ast import *                                                           
#```                                                                            
# The transformation of source code into an AST involves two major steps:       
# lexing and parsing. Simplethon utilizes \href{http://www.dabeaz.com/ply}{PLY} 
# (Python Lex-Yacc) for this purpose. \tc{lex} and \tc{yacc} are integrated     
# and imported into sth as external Python modules:                             
#```                                                                            
from sth.external import lex, yacc 
#```                                                                            
# \subsection{Lexer}
#
# The lexer transforms the input source code into a sequence of tokens. Every
# token has a name. Tokens representing numerals, strings and identifiers also
# hold a value.
#
# \subsubsection{Literals}
#
# The PLY lexer supports a simple way of specifying literals that only consist
# of one character:
#```                                                                            
literals = [ '+', '-', '*', '/', '%', '=', '<', '>',
             ':', ',', '(', ')']
#```
# Literals consisting of more than one character have to be defined and named
# explicitely:
#```
t_PLUSEQUALS    = r'\+='
t_MINUSEQUALS   = r'-='
t_STAREQUALS    = r'\*='
t_SLASHEQUALS   = r'/='
t_DOUBLEEQUALS  = r'=='
t_NOTEQUALS     = r'!='
t_LESSEQUALS    = r'<='
t_GREATEREQUALS = r'>='
#```                                                                            
# \subsubsection{Comments}
#
# Everything on a line following a hash is considered a comment and is ignored
# by the lexer:
#```                                                                            
t_ignore_COMMENT = r'\#.*'
#```
# Blanks and tabs are ignored too, except when they appear after a newline. In
# this case they are treated as indentation (see section~\ref{sec:indent}).
#```
t_ignore         = ' \t'
#```                                                                            
# \subsubsection{Strings}
#
# In this early version of Simplethon strings cannot be productively used. Only 
# a minimum string support is provided so that type information can be provided
# and handled.
#```                                                                            
def t_SHORTSTRING(t):
    r'".*?"|\'.*?\''
    t.value = t.value[1:-1]
    return t
#```                                                                            
# \subsubsection{Numerals}
#
# Numerals start with an optional sign and then continues with one of the 
# following:
# \begin{itemize}
#     \item Zero or more digits followed by a dot and one or more digits. This
#        covers cases such as \tc{3.14} and \tc{.14}.
#      \item One ore more digits followed by an optional dot. This covers cases
#        such as \tc{314} and \tc{3.}.
# \end{itemize}
# They then continues with an optional exponent.
#
# This rule also matches integers, so an additional check is made if the
# matched sequence contains a dot or an exponent. If not the numeral is an
# integer, otherwise it is a float.
#```                                                                            
def t_FLOAT(t):
    r'''[-+]?
        (?:
            (?: \d* \. \d+ )
            |
            (?: \d+ \.? )
        )
        (?: [Ee] [+-]? \d+ ) ?
    '''
    if not set(t.value).intersection('eE.'):
        t.type = 'INTEGER'
    return t
#```                                                                            
# \subsubsection{Identifiers and keywords}
#
# An identifier is a sequence of alphanumeric characters and underscores,
# whereas the first character must not be a digit.
#
# This rule also applies to all reserved keywords. To avoid defining separate
# rules for each keyword a dictionary holding keywords as keys and token names
# as values is defined:
#```                                                                            
reserved = {
        'break'    : 'BREAK',
        'continue' : 'CONTINUE',
        'def'      : 'DEF',
        'elif'     : 'ELIF',
        'else'     : 'ELSE',
        'False'    : 'FALSE',
        'finally'  : 'FINALLY',
        'if'       : 'IF',
        'return'   : 'RETURN',
        'True'     : 'TRUE',
        'while'    : 'WHILE'
}
#```
# The rule for identifiers checks, if the identifier is a keyword. If so the
# name of the identifier is set to the name of the keyword. So the rule
# \tc{t\_IDENTIFIER} can either return an identifier or any keyword token.
#```
def t_IDENTIFIER(t):
    r'[a-zA-Z_]+\w*'
    t.type = reserved.get(t.value, t.type)
    return t
#```                                                                            
# \subsubsection{Indentation}
# \label{sec:indent}
#
# Unlike in most other programming languages, indentations are crucial syntax
# tokens in Python and Simplethon. An increased indentation marks the beginning
# of a block whereas a decreased indentation marks the end of a block. In the
# sequence of tokens produced by the lexer, every \tc{NEWLINE} token can be
# followed by:
# \begin{itemize}
#     \item An \tc{INDENT} token if the line following the newline character is
#     of increased indentation.
#     \item A \tc{DEINDENT} token if the line following the newline character is
#     of decreased indentation.
#     \item No indentation token if the line following the newline characters
#     is of the same indentation as the previous line.
# \end{itemize}
# To provide this functionality, the lexer has to keep track of the nested
# levels of indentation, which the PLY lexer cannot do by default. The
# following adaptions were made to the lexer:
# \begin{enumerate}
#     \item Every lex rule returns a token. However, an indentation rule 
#     sometimes has to return multiple tokens. For this purpose a 
#     \emph{token stack} is added to the lexer. The lexer first returns the
#     token that is returned by the current rule. Then all tokens on the token
#     stack are returned before any further parsing is done. Only when the
#     token stack is empty, further parsing is done.
#     \item An indentation stack was added. On every idendation increase the
#     number of additional whitespaces is pushed on top of an \emph{indentation
#     stack}. On every indentation decrease a value is popped from the stack 
#     until the whitespace count of the whole stack matches the whitespace 
#     count of the current line. For every pop of the stack a \tc{DEINDENT} 
#     token is pushed onto the token stack. If the whitespace count of the 
#     current line cannot be matched to the indentation stack an syntax error 
#     is raised.
# \end{enumerate}
#
# An example should illustrate how indentation token parsing works. This
# example only shows indentation and newline tokens and disregards all other
# tokens. IS denotes the indentation stack and TS denotes the token stack,
# \tc{I} denotes a \tc{INDENT} token, \tc{D} denotes a \tc{DEINDENT} token and
# \tc{N} denotes a \tc{NEWLINE} token.
#
# \begin{tabularx}{\linewidth}{l|l|l|l}
#  Code & IS & TS & returned token sequence \\
#  \hline 
#  \tc{def f(x):} 
#     & $\emptyset$ & $\emptyset$ & \tc{N} \\
#  \hspace{5mm}\tc{``cint -> cint''} 
#     & 4 & \tc{I} & \tc{N} \tc{I} \\
#  \hspace{5mm}\tc{if x < 2:}
#     & 4 & $\emptyset$ & \tc{N} \\
#  \hspace{10mm}\tc{return x}
#     & 4 4 & \tc{I} & \tc{N} \tc{I}\\
#  \hspace{5mm}\tc{else:}
#     & 4 & \tc{D} & \tc{N} \tc{D}\\
#  \hspace{10mm}\tc{return f(x-1) + f(x-2)}
#     & 4 4 & \tc{I} & \tc{N} \tc{I}\\
#     & $\emptyset$ & \tc{D} \tc{D} & \tc{N} \tc{D} \tc{D}\\
# \end{tabularx}
#
# This logic is implemented in the \tc{t\_INDENT} rule. This rule is triggered
# by any newline found (except newlines found in strings).
#```                                                                            
def t_INDENT(t):
    r'\n\s*'

    lexer = t.lexer
#```
# The rule matches the newline and consecutive white spaces, which can also 
# include further newlines. We increase the line number count of the lexer by
# the amount of newline characters we find in the match.
#```
    lexer.lineno += t.value.count('\n')
#```
# To avoid corruption of the indentation stack by
# empty lines inserted between indented lines, only white spaces after the last
# newline in the matched sequence are considered. This empty lines do not
# affect the indentation stack:
#```
    t.value = '\n%s' % t.value.split('\n')[-1]
#```
# In a next step the two indentation values to be compared are calculated. The
# old indentation (refering to the previous line) is the sum of all 
# indentations on the indentation stack. The new indentation of the current
# line is calculated as the sum of all spaces and tabs in the matched 
# indentation sequence:
#```
    oldindent = sum(lexer.indentstack)
    newindent = t.value.count(' ') + t.value.count('\t')
#```
# In the table above it can be seen that a newline token has to be returned in
# any case. This happens at the end of this function. Regarding the indentation
# tokens that have to go on the token stack three cases have to be distinguished:
#
# \begin{itemize}
# \item [1] The new indentation matches the old indentation. Nothing has to be done
# in this case.
# \item [2] The new indentation is greater than the old indentation. One
# indentation token has to be pushed onto the token stack and the difference
# between the old and the new indentation has to be pushed onto the
# indentation stack:
# \end{itemize}
#```
    if newindent > oldindent:
        lexer.push_token(t)
        lexer.indentstack.insert(0, newindent - oldindent)
#```
# \begin{itemize}
# \item [3]  The new indentation is smaller than the old indentation. In this case
# indentation values are popped from the indentation stack until the
# indentation stack matches the current new indentation. For every pop a
# \tc{DEINDENT} token is pushed onto the token stack.
#
# If for some reason the indentation stack cannot be brought to match with the
# current indentation, the lexer signals an error.
# \end{itemize}
#```
    elif newindent < oldindent:
        while sum(lexer.indentstack) > newindent:
            t_deindent = t.copy(type='DEINDENT')
            lexer.push_token(t_deindent)
            lexer.indentstack.pop()
        if sum(lexer.indentstack) != newindent:
            raise SyntaxError("Indentation error at line %d" % t.lineno)
#```
# Finally the obligatory newline token is returned.
#```
    return t.copy(type='NEWLINE')
#```
# \subsubsection{Error handling
#
# A \tc{SyntaxError} is raised in case a character cannot be parsed into a 
# lex token.
#```
def t_error(t):
    raise SyntaxError("Illegal character '%s' at line %d, position %d" % (
        t.value[0], t.lineno, t.lexpos))
#```
# \subsubsection{Conclusion}
#
# The PLY lexer reads a list of all tokens he has to support from the list
# \tc{tokens}. This list consists of all tokens for which we have defined rules
# as well as the keyword names, which are handled via the \tc{t\_IDENTIFIER}
# rule.
#```
tokens = [
        'IDENTIFIER', 
        'INTEGER', 'FLOAT', 
        'SHORTSTRING',
        'INDENT', 'DEINDENT', 'NEWLINE', 
        'PLUSEQUALS', 'MINUSEQUALS', 'STAREQUALS', 'SLASHEQUALS',
        'DOUBLEEQUALS', 'NOTEQUALS', 'LESSEQUALS', 'GREATEREQUALS'
    ] + list(reserved.values())
#```
# The function \tc{lex\_string} returns an iterable lexer object that was
# initialized with a string. This function is provided for testing purposes.
#```
def lex_string(s):
    lexer = lex.lex()
    lexer.input(s)
    return lexer
