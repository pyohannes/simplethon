# -*- coding: utf-8
import pytest
from sth.parser import lex_string


def assert_lexer(input, output, ret):
    ret = [ str(t) for t in lex_string(input) ]

    assert output == '\n'.join(ret) + '\n'


def assert_lexer_error(input):
    with pytest.raises(SyntaxError):
        list(lex_string(input))


def test_number():
    assert_lexer(
"""1 2 3 500 9876543210 3 -9""",
"""LexToken(INTEGER,'1',1,0)
LexToken(INTEGER,'2',1,2)
LexToken(INTEGER,'3',1,4)
LexToken(INTEGER,'500',1,6)
LexToken(INTEGER,'9876543210',1,10)
LexToken(INTEGER,'3',1,21)
LexToken(INTEGER,'-9',1,23)
""", 0)


def test_float():
    assert_lexer(
"""1. .3 0.0 -3.14 1e5 1e-5 -.3""",
"""LexToken(FLOAT,'1.',1,0)
LexToken(FLOAT,'.3',1,3)
LexToken(FLOAT,'0.0',1,6)
LexToken(FLOAT,'-3.14',1,10)
LexToken(FLOAT,'1e5',1,16)
LexToken(FLOAT,'1e-5',1,20)
LexToken(FLOAT,'-.3',1,25)
""", 0)


def test_newline():
    assert_lexer(
"""1
2
3
500
""",
"""LexToken(INTEGER,'1',1,0)
LexToken(NEWLINE,'\\n',1,1)
LexToken(INTEGER,'2',2,2)
LexToken(NEWLINE,'\\n',2,3)
LexToken(INTEGER,'3',3,4)
LexToken(NEWLINE,'\\n',3,5)
LexToken(INTEGER,'500',4,6)
LexToken(NEWLINE,'\\n',4,9)
""", 0)


def test_identifier():
    assert_lexer(
"""x y
ab
identifier
id id2 id3
a b c
""",
"""LexToken(IDENTIFIER,'x',1,0)
LexToken(IDENTIFIER,'y',1,2)
LexToken(NEWLINE,'\\n',1,3)
LexToken(IDENTIFIER,'ab',2,4)
LexToken(NEWLINE,'\\n',2,6)
LexToken(IDENTIFIER,'identifier',3,7)
LexToken(NEWLINE,'\\n',3,17)
LexToken(IDENTIFIER,'id',4,18)
LexToken(IDENTIFIER,'id2',4,21)
LexToken(IDENTIFIER,'id3',4,25)
LexToken(NEWLINE,'\\n',4,28)
LexToken(IDENTIFIER,'a',5,29)
LexToken(IDENTIFIER,'b',5,31)
LexToken(IDENTIFIER,'c',5,33)
LexToken(NEWLINE,'\\n',5,34)
""", 0)


def test_shortstring():
    assert_lexer(
""""ab"
'ab'
""",
"""LexToken(SHORTSTRING,'ab',1,0)
LexToken(NEWLINE,'\\n',1,4)
LexToken(SHORTSTRING,'ab',2,5)
LexToken(NEWLINE,'\\n',2,9)
""", 0)


#def test_longstring():
#    assert_lexer(
#"""\"\"\"A longer
#text with quotes "Hi"
#\"\"\"
#'''Single quotes
#can be
#used too.'''
#""",
#"""LexToken(STRING,"A longer\ntext with quotes \"Hi\"\n",1,0)
#LexToken(NEWLINE,"\n",3,3)
#LexToken(STRING,"Single quotes\ncan be\nused too.",4,0)
#LexToken(NEWLINE,"\n",6,12)
#""", 0)


def test_indent():
    assert_lexer(
"""
a
  b
    c
    d
    e
  f
    g
    h
           i
k
    l
""",
"""LexToken(NEWLINE,'\\n',1,0)
LexToken(IDENTIFIER,'a',2,1)
LexToken(NEWLINE,'\\n  ',2,2)
LexToken(INDENT,'\\n  ',2,2)
LexToken(IDENTIFIER,'b',3,5)
LexToken(NEWLINE,'\\n    ',3,6)
LexToken(INDENT,'\\n    ',3,6)
LexToken(IDENTIFIER,'c',4,11)
LexToken(NEWLINE,'\\n    ',4,12)
LexToken(IDENTIFIER,'d',5,17)
LexToken(NEWLINE,'\\n    ',5,18)
LexToken(IDENTIFIER,'e',6,23)
LexToken(NEWLINE,'\\n  ',6,24)
LexToken(DEINDENT,'\\n  ',6,24)
LexToken(IDENTIFIER,'f',7,27)
LexToken(NEWLINE,'\\n    ',7,28)
LexToken(INDENT,'\\n    ',7,28)
LexToken(IDENTIFIER,'g',8,33)
LexToken(NEWLINE,'\\n    ',8,34)
LexToken(IDENTIFIER,'h',9,39)
LexToken(NEWLINE,'\\n           ',9,40)
LexToken(INDENT,'\\n           ',9,40)
LexToken(IDENTIFIER,'i',10,52)
LexToken(NEWLINE,'\\n',10,53)
LexToken(DEINDENT,'\\n',10,53)
LexToken(DEINDENT,'\\n',10,53)
LexToken(DEINDENT,'\\n',10,53)
LexToken(IDENTIFIER,'k',11,54)
LexToken(NEWLINE,'\\n    ',11,55)
LexToken(INDENT,'\\n    ',11,55)
LexToken(IDENTIFIER,'l',12,60)
LexToken(NEWLINE,'\\n',12,61)
LexToken(DEINDENT,'\\n',12,61)
""", 0)


def test_indent_error():
    assert_lexer_error(
"""
a
    b
  c
""")


def test_keywords():
    assert_lexer(
"""if else elif
def return
while continue break
True False
""",
"""LexToken(IF,'if',1,0)
LexToken(ELSE,'else',1,3)
LexToken(ELIF,'elif',1,8)
LexToken(NEWLINE,'\\n',1,12)
LexToken(DEF,'def',2,13)
LexToken(RETURN,'return',2,17)
LexToken(NEWLINE,'\\n',2,23)
LexToken(WHILE,'while',3,24)
LexToken(CONTINUE,'continue',3,30)
LexToken(BREAK,'break',3,39)
LexToken(NEWLINE,'\\n',3,44)
LexToken(TRUE,'True',4,45)
LexToken(FALSE,'False',4,50)
LexToken(NEWLINE,'\\n',4,55)
""", 0)


def test_literals():
    assert_lexer(
""": = ,
- / * % +
( )
> <
== != <= >=
""",
"""LexToken(:,':',1,0)
LexToken(=,'=',1,2)
LexToken(,,',',1,4)
LexToken(NEWLINE,'\\n',1,5)
LexToken(-,'-',2,6)
LexToken(/,'/',2,8)
LexToken(*,'*',2,10)
LexToken(%,'%',2,12)
LexToken(+,'+',2,14)
LexToken(NEWLINE,'\\n',2,15)
LexToken((,'(',3,16)
LexToken(),')',3,18)
LexToken(NEWLINE,'\\n',3,19)
LexToken(>,'>',4,20)
LexToken(<,'<',4,22)
LexToken(NEWLINE,'\\n',4,23)
LexToken(DOUBLEEQUALS,'==',5,24)
LexToken(NOTEQUALS,'!=',5,27)
LexToken(LESSEQUALS,'<=',5,30)
LexToken(GREATEREQUALS,'>=',5,33)
LexToken(NEWLINE,'\\n',5,35)
""", 0)


def test_literals_error():
    for lit in "$&|§äö":
        assert_lexer_error(lit)
