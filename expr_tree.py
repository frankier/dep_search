import re

import lex as lex
import yacc as yacc



class ExpressionError(ValueError):

    pass


class BaseNode():
    node_id = ''
    level = 0
    negs_above = False
    neg = False
    deprel = False

class SetNode_Token(BaseNode):
    #Makes a single operation, and returns a single set
    def __init__(self, token_restriction):
        self.node_id = ''
        self.token_restriction = token_restriction
        self.proplabel = ''

    def get_kid_nodes(self):
        return []

    def to_unicode(self):
        return u'SetNode(Token:' + self.proplabel + self.token_restriction + u')' 


class SetNode_And(BaseNode):

    def __init__(self, setnode1, setnode2):
        self.node_id = ''
        self.setnode1 = setnode1
        self.setnode2 = setnode2
        self.proplabel = ''

    def get_kid_nodes(self):
        return [self.setnode1, self.setnode2]

    def to_unicode(self):
        return u'Node(' + self.setnode1.to_unicode() + ' AND ' + self.setnode2.to_unicode() + ')'

class SetNode_Or(BaseNode):

    def __init__(self, setnode1, setnode2):
        self.node_id = ''
        self.setnode1 = setnode1
        self.setnode2 = setnode2
        self.proplabel = ''

    def get_kid_nodes(self):
        return [self.setnode1, self.setnode2]

    def to_unicode(self):
        return u'Node(' + self.setnode1.to_unicode() + ' OR ' + self.setnode2.to_unicode() + ')'

class SetNode_Dep(BaseNode):

    def __init__(self, setnode1, setnode2, deprel):
        self.node_id = ''
        self.index_node = setnode1
        self.deprels = [(deprel, setnode2)]
        #self.setnode2 = setnode2
        #self.deprel = deprel
        self.proplabel = ''

    def get_kid_nodes(self):
        to_return = [self.index_node,]
        for dr_tuple in self.deprels:
            to_return.append(dr_tuple[0])
            to_return.append(dr_tuple[1])
        return to_return

    def to_unicode(self):

        deprel_list = []
        for drt in self.deprels:
            deprel_list.append(drt[0].to_unicode() + ':' + drt[1].to_unicode())        

        return u'Node(index_node:' + self.index_node.to_unicode() + ' << ' + ','.join(deprel_list) +' >> )'

class SetNode_Not(BaseNode):

    def __init__(self, setnode1):
        self.node_id = ''
        self.setnode1 = setnode1
        self.neg = True

    def get_kid_nodes(self):
        return [self.setnode1,]

    def to_unicode(self):
        return u'Node(NOT ' + self.setnode1.to_unicode() +')'

class DeprelNode(BaseNode):
    #Makes a single operation, and returns a single set
    def __init__(self, dep_restriction):
        self.node_id = ''
        self.dep_restriction = dep_restriction
        self.deprel = True

    def get_kid_nodes(self):
        return []

    def to_unicode(self):
        return u'DeprelNode(' + self.dep_restriction + u')'

class DeprelNode_And(BaseNode):

    def __init__(self, dnode1, dnode2):
        self.node_id = ''
        self.dnode1 = dnode1
        self.dnode2 = dnode2
        self.deprel = True

    def get_kid_nodes(self):
        return [self.dnode1, self.dnode2]

    def to_unicode(self):
        return u'DeprelNode(' + self.dnode1.to_unicode() + ' AND ' + self.dnode2.to_unicode() + ')'

class DeprelNode_Or(BaseNode):

    def __init__(self, dnode1, dnode2):
        self.node_id = ''
        self.dnode1 = dnode1
        self.dnode2 = dnode2
        self.deprel = True

    def get_kid_nodes(self):
        return [self.dnode1, self.dnode2]

    def to_unicode(self):
        return u'DeprelNode(' + self.dnode1.to_unicode() + ' OR ' + self.dnode2.to_unicode() + ')'


class DeprelNode_Not(BaseNode):

    def __init__(self, dnode1):
        self.node_id = '' 
        self.dnode1 = dnode1
        self.neg = True
        self.deprel = True

    def get_kid_nodes(self):
        return [self.dnode1]

    def to_unicode(self):
        return u'DeprelNode(NOT ' + self.dnode1.to_unicode() +')'


#########################
### The expression parser bit starts here

#Lexer - tokens

tokens=('REGEX',    #/..../
        'PROPLABEL', #@...
        'DEPOP',     #</nsubj/
        'LPAR',      #(
        'RPAR',      #)
        'NEG',       #!
        'AND',       #&
        'OR',        #|
        'ANYTOKEN')  #_

#Here's regular expressions for the tokens defined above

t_REGEX=ur"/[^/]+/"
t_PROPLABEL=ur"@[A-Z]+"
t_DEPOP=ur"(<|>)(/[^/]+/)?"
t_LPAR=ur"\("
t_RPAR=ur"\)"
t_NEG=ur"\!"
t_AND=ur"\&"
t_OR=ur"\|"
t_ANYTOKEN=ur"_"

t_ignore=u" \t"

def t_error(t):
    raise ExpressionError(u"Unexpected character '%s'\nHERE: '%s'..."%(t.value[0],t.value[:5]))


#......and here's where starts the CFG describing the expressions
# the grammar rules are the comment strings of the functions

#Main 
precedence = (('right','DEPOP'),('left','OR'),('left','AND'))

def p_error(t):
    if t==None:
        raise ExpressionError(u"Syntax error at the end of the expression. Perhaps you forgot to specify a target token? Forgot to close parentheses?")
    else:
        raise ExpressionError(u"Syntax error at the token '%s'\nHERE: '%s'..."%(t.value,t.lexer.lexdata[t.lexpos:t.lexpos+5]))

#TOP  search -> expression
def p_top(t):
    u'''search : setnode'''
    t[0]=t[1]   #t[0] is the result (left-hand side) and t[1] is the result of "expr"

# expression can be:

#  ( expression )
#  _
def p_exprp(t):
    u'''setnode : LPAR setnode RPAR
              | ANYTOKEN'''
    if len(t)==4: #the upper rule
        t[0]=t[2] #...just return the embedded expression
    elif len(t)==2:
        t[0]=SetNode_Token(t[1]) #hmm... - shouldn't I somehow fill this node?

def p_exprpd(t):
    u'''depnode : LPAR depnode RPAR
              | DEPOP'''
    if len(t)==4: #the upper rule
        t[0]=t[2] #...just return the embedded expression
    elif len(t)==2:
        t[0]=DeprelNode(t[1]) #hmm... - shouldn't I somehow fill this node?

def p_dn_and(t):
    u'''depnode : depnode AND depnode'''
    t[0] = DeprelNode_And(t[1], t[3])

def p_sn_and(t):
    u'''setnode : setnode AND setnode'''
    t[0] = SetNode_And(t[1], t[3])

def p_dn_or(t):
    u'''depnode : depnode OR depnode'''
    t[0] = DeprelNode_Or(t[1], t[3])

def p_sn_or(t):
    u'''setnode : setnode OR setnode'''
    t[0] = SetNode_Or(t[1], t[3])

def p_dn_not(t):
    u'''depnode : NEG depnode'''
    t[0] = DeprelNode_Not(t[2])
def p_sn_not(t):
    u'''setnode : NEG setnode'''
    t[0] = SetNode_Not(t[2])

#def p_sn_depres(t):
#    u'''setnode : setnode depnode setnode'''
#    t[0] = SetNode_Dep(t[1], t[3], t[2])

def p_sn_depres_ex(t):
    u'''setnode : setnode depres'''
    if isinstance(t[1], SetNode_Dep):
        t[1].deprels.append(t[2])
        t[0] = t[1]
    else:
        t[0] = SetNode_Dep(t[1], t[2][1], t[2][0])


def p_sn_depres_a(t):
    u'''depres : depnode setnode'''
    t[0] = (t[1], t[2])

#def p_sn_depres_ex(t):
#    u'''setnode : setnode depnode setnode'''
#    if isinstance(t[1], SetNode_Dep):
#        t[1].deprels.append((t[2], t[3]))
#        t[0] = t[1]
#    else:
#        t[0] = SetNode_Dep(t[1], t[3], t[2])

def p_n_sn(t):
    u'''setnode : REGEX
                | PROPLABEL REGEX'''
    if len(t) == 2:
        t[0] = SetNode_Token(t[1])
    elif len(t) == 3:
        t[0] = SetNode_Token(t[2])
        t[0].proplabel = t[1]


lex.lex(reflags=re.UNICODE)
yacc.yacc(write_tables=0)

 
if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Expression parser')
    parser.add_argument('expression', nargs='+', help='Training file name, or nothing for training on stdin')
    args = parser.parse_args()
    
    e_parser=yacc.yacc()
    for expression in args.expression:
        exp = e_parser.parse(expression)
        print exp.to_unicode()
        import pdb;pdb.set_trace()
    
