#  Copyright (c) 2015, 2016 Rocky Bernstein
#  Copyright (c) 2005 by Dan Pascu <dan@windowmaker.org>
#  Copyright (c) 2000-2002 by hartmut Goebel <h.goebel@crazy-compilers.com>
#  Copyright (c) 1999 John Aycock
#
#  See LICENSE for license
"""
A spark grammar for Python 3.x.

However instead of terminal symbols being the usual ASCII text,
e.g. 5, myvariable, "for", etc.  they are CPython Bytecode tokens,
e.g. "LOAD_CONST 5", "STORE NAME myvariable", "SETUP_LOOP", etc.

If we succeed in creating a parse tree, then we have a Python program
that a later phase can turn into a sequence of ASCII text.
"""

from __future__ import print_function

from uncompyle6.parser import PythonParser, PythonParserSingle, nop_func
from uncompyle6.parsers.astnode import AST
from spark_parser import DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG

class Python3Parser(PythonParser):

    def __init__(self, debug_parser=PARSER_DEFAULT_DEBUG):
        self.added_rules = set()
        super(Python3Parser, self).__init__(AST, 'stmts', debug=debug_parser)
        self.new_rules = set()

    def p_comprehension3(self, args):
        """
        # Python3 scanner adds LOAD_LISTCOMP. Python3 does list comprehension like
        # other comprehensions (set, dictionary).

        # listcomp is a custom Python3 rule
        expr ::= listcomp

        # Our "continue" heuristic -  in two successive JUMP_BACKS, the first
        # one may be a continue - sometimes classifies a JUMP_BACK
        # as a CONTINUE. The two are kind of the same in a comprehension.

        comp_for ::= expr _for designator comp_iter CONTINUE

        list_for ::= expr FOR_ITER designator list_iter jb_or_c

        jb_or_c ::= JUMP_BACK
        jb_or_c ::= CONTINUE

        stmt ::= setcomp_func

        setcomp_func ::= BUILD_SET_0 LOAD_FAST FOR_ITER designator comp_iter
                JUMP_BACK RETURN_VALUE RETURN_LAST

        comp_body ::= dict_comp_body
        comp_body ::= set_comp_body
        dict_comp_body ::= expr expr MAP_ADD
        set_comp_body ::= expr SET_ADD

        # See also common Python p_list_comprehension
        """

    def p_dictcomp3(self, args):
        """"
        dictcomp ::= LOAD_DICTCOMP LOAD_CONST MAKE_FUNCTION_0 expr GET_ITER CALL_FUNCTION_1
        """

    def p_grammar(self, args):
        '''
        sstmt ::= stmt
        sstmt ::= ifelsestmtr
        sstmt ::= return_stmt RETURN_LAST

        return_if_stmts ::= return_if_stmt come_from_opt
        return_if_stmts ::= _stmts return_if_stmt
        return_if_stmt ::= ret_expr RETURN_END_IF

        stmt ::= break_stmt
        break_stmt ::= BREAK_LOOP

        stmt ::= continue_stmt
        continue_stmt ::= CONTINUE
        continue_stmt ::= CONTINUE_LOOP
        continue_stmts ::= _stmts lastl_stmt continue_stmt
        continue_stmts ::= lastl_stmt continue_stmt
        continue_stmts ::= continue_stmt

        stmt ::= raise_stmt0
        stmt ::= raise_stmt1
        stmt ::= raise_stmt2
        stmt ::= raise_stmt3

        raise_stmt0 ::= RAISE_VARARGS_0
        raise_stmt1 ::= expr RAISE_VARARGS_1
        raise_stmt2 ::= expr expr RAISE_VARARGS_2
        raise_stmt3 ::= expr expr expr RAISE_VARARGS_3

        del_stmt ::= delete_subscr
        delete_subscr ::= expr expr DELETE_SUBSCR
        del_stmt ::= expr DELETE_ATTR

        kwarg   ::= LOAD_CONST expr
        kwargs  ::= kwargs kwarg
        kwargs  ::=

        classdef ::= build_class designator

        # Python3 introduced LOAD_BUILD_CLASS
        # Other definitions are in a custom rule
        build_class ::= LOAD_BUILD_CLASS mkfunc expr call_function CALL_FUNCTION_3

        stmt ::= classdefdeco
        classdefdeco ::= classdefdeco1 designator
        classdefdeco1 ::= expr classdefdeco1 CALL_FUNCTION_1
        classdefdeco1 ::= expr classdefdeco2 CALL_FUNCTION_1

        assert ::= assert_expr jmp_true LOAD_ASSERT RAISE_VARARGS_1
        assert2 ::= assert_expr jmp_true LOAD_ASSERT expr CALL_FUNCTION_1 RAISE_VARARGS_1
        assert2 ::= assert_expr jmp_true LOAD_ASSERT expr RAISE_VARARGS_2

        assert_expr ::= expr
        assert_expr ::= assert_expr_or
        assert_expr ::= assert_expr_and
        assert_expr_or ::= assert_expr jmp_true expr
        assert_expr_and ::= assert_expr jmp_false expr

        ifstmt ::= testexpr _ifstmts_jump

        testexpr ::= testfalse
        testexpr ::= testtrue
        testfalse ::= expr jmp_false
        testtrue ::= expr jmp_true

        _ifstmts_jump ::= return_if_stmts
        _ifstmts_jump ::= c_stmts_opt JUMP_FORWARD COME_FROM

        iflaststmt ::= testexpr c_stmts_opt JUMP_ABSOLUTE

        iflaststmtl ::= testexpr c_stmts_opt JUMP_BACK
        iflaststmtl ::= testexpr c_stmts_opt JUMP_BACK COME_FROM_LOOP

        ifelsestmt ::= testexpr c_stmts_opt JUMP_FORWARD else_suite COME_FROM

        ifelsestmtc ::= testexpr c_stmts_opt JUMP_ABSOLUTE else_suitec

        ifelsestmtr ::= testexpr return_if_stmts return_stmts

        ifelsestmtl ::= testexpr c_stmts_opt JUMP_BACK else_suitel
        ifelsestmtl ::= testexpr c_stmts_opt JUMP_BACK else_suitel JUMP_BACK COME_FROM_LOOP
        ifelsestmtl ::= testexpr c_stmts_opt JUMP_BACK else_suitel COME_FROM_LOOP


        # FIXME: this feels like a hack. Is it just 1 or two
        # COME_FROMs?  the parsed tree for this and even with just the
        # one COME_FROM for Python 2.7 seems to associate the
        # COME_FROM targets from the wrong places

        trystmt        ::= SETUP_EXCEPT suite_stmts_opt POP_BLOCK
                           try_middle opt_come_from_except

        # this is nested inside a trystmt
        tryfinallystmt ::= SETUP_FINALLY suite_stmts_opt
                           POP_BLOCK LOAD_CONST
                           come_from_or_finally suite_stmts_opt END_FINALLY

        tryelsestmt    ::= SETUP_EXCEPT suite_stmts_opt POP_BLOCK
                           try_middle else_suite come_froms

        tryelsestmtc ::= SETUP_EXCEPT suite_stmts_opt POP_BLOCK
                         try_middle else_suitec COME_FROM

        tryelsestmtl ::= SETUP_EXCEPT suite_stmts_opt POP_BLOCK
                         try_middle else_suitel COME_FROM

        try_middle ::= jmp_abs COME_FROM except_stmts
                       END_FINALLY
        try_middle ::= jmp_abs COME_FROM_EXCEPT except_stmts
                       END_FINALLY

        # FIXME: remove this
        try_middle ::= JUMP_FORWARD COME_FROM except_stmts
                       END_FINALLY COME_FROM
        try_middle ::= JUMP_FORWARD COME_FROM except_stmts
                       END_FINALLY COME_FROM_EXCEPT

        except_stmts ::= except_stmts except_stmt
        except_stmts ::= except_stmt

        except_stmt ::= except_cond1 except_suite
        except_stmt ::= except_cond2 except_suite
        except_stmt ::= except_cond2 except_suite_finalize
        except_stmt ::= except

        ## FIXME: what's except_pop_except?
        except_stmt ::= except_pop_except

        # Python3 introduced POP_EXCEPT
        except_suite ::= c_stmts_opt POP_EXCEPT jump_except
        jump_except ::= JUMP_ABSOLUTE
        jump_except ::= JUMP_BACK
        jump_except ::= JUMP_FORWARD
        jump_except ::= CONTINUE

        # This is used in Python 3 in
        # "except ... as e" to remove 'e' after the c_stmts_opt finishes
        except_suite_finalize ::= SETUP_FINALLY c_stmts_opt except_var_finalize
                                  END_FINALLY _jump

        except_var_finalize ::= POP_BLOCK POP_EXCEPT LOAD_CONST come_from_or_finally
                                LOAD_CONST designator del_stmt

        except_suite ::= return_stmts

        except_cond1 ::= DUP_TOP expr COMPARE_OP
                jmp_false POP_TOP POP_TOP POP_TOP

        except_cond2 ::= DUP_TOP expr COMPARE_OP
                jmp_false POP_TOP designator POP_TOP

        except  ::=  POP_TOP POP_TOP POP_TOP c_stmts_opt POP_EXCEPT _jump
        except  ::=  POP_TOP POP_TOP POP_TOP return_stmts

        jmp_abs ::= JUMP_ABSOLUTE
        jmp_abs ::= JUMP_BACK

        withstmt ::= expr SETUP_WITH POP_TOP suite_stmts_opt
                POP_BLOCK LOAD_CONST COME_FROM_WITH
                WITH_CLEANUP END_FINALLY

        withasstmt ::= expr SETUP_WITH designator suite_stmts_opt
                POP_BLOCK LOAD_CONST COME_FROM_WITH
                WITH_CLEANUP END_FINALLY

        and ::= expr jmp_false expr COME_FROM
        or  ::= expr jmp_true  expr COME_FROM
        '''

    def p_misc3(self, args):
        """
        try_middle ::= JUMP_FORWARD COME_FROM_EXCEPT except_stmts END_FINALLY COME_FROM

        for_block ::= l_stmts_opt opt_come_from_loop JUMP_BACK
        for_block ::= l_stmts
        iflaststmtl ::= testexpr c_stmts_opt
        iflaststmt    ::= testexpr c_stmts_opt34
        c_stmts_opt34 ::= JUMP_BACK JUMP_ABSOLUTE c_stmts_opt
        """

    def p_come_from3(self, args):
        """
        opt_come_from_except ::= COME_FROM_EXCEPT
        opt_come_from_except ::= come_froms

        come_froms ::= come_froms COME_FROM
        come_froms ::=

        opt_come_from_loop ::= opt_come_from_loop COME_FROM_LOOP
        opt_come_from_loop ::=

        come_from_or_finally  ::= COME_FROM_FINALLY
        come_from_or_finally  ::= COME_FROM

        """

    def p_jump3(self, args):
        """
        jmp_false ::= POP_JUMP_IF_FALSE
        jmp_true  ::= POP_JUMP_IF_TRUE

        # FIXME: Common with 2.7
        ret_and  ::= expr JUMP_IF_FALSE_OR_POP ret_expr_or_cond COME_FROM
        ret_or   ::= expr JUMP_IF_TRUE_OR_POP ret_expr_or_cond COME_FROM
        ret_cond ::= expr POP_JUMP_IF_FALSE expr RETURN_END_IF ret_expr_or_cond
        ret_cond_not ::= expr POP_JUMP_IF_TRUE expr RETURN_END_IF ret_expr_or_cond

        or   ::= expr JUMP_IF_TRUE_OR_POP expr COME_FROM
        and  ::= expr JUMP_IF_FALSE_OR_POP expr COME_FROM

        cmp_list1 ::= expr DUP_TOP ROT_THREE
                COMPARE_OP JUMP_IF_FALSE_OR_POP
                cmp_list1 COME_FROM
        cmp_list1 ::= expr DUP_TOP ROT_THREE
                COMPARE_OP JUMP_IF_FALSE_OR_POP
                cmp_list2 COME_FROM
        """

    def p_stmt3(self, args):
        """
        stmt ::= LOAD_CLOSURE RETURN_VALUE RETURN_LAST
        stmt ::= whileTruestmt
        ifelsestmt ::= testexpr c_stmts_opt JUMP_FORWARD else_suite _come_from
        """

    def p_loop_stmt3(self, args):
        """
        forstmt           ::= SETUP_LOOP expr _for designator for_block POP_BLOCK
                              opt_come_from_loop
        forelsestmt       ::= SETUP_LOOP expr _for designator for_block POP_BLOCK else_suite
                              COME_FROM_LOOP

        forelselaststmt   ::= SETUP_LOOP expr _for designator for_block POP_BLOCK else_suitec
                              COME_FROM_LOOP

        forelselaststmtl  ::= SETUP_LOOP expr _for designator for_block POP_BLOCK else_suitel
                              COME_FROM_LOOP

        whilestmt         ::= SETUP_LOOP testexpr l_stmts_opt JUMP_BACK POP_BLOCK
                              COME_FROM_LOOP

        # The JUMP_ABSOLUTE below comes from escaping an "if" block which surrounds
        # the while. This is messy
        whilestmt         ::= SETUP_LOOP testexpr l_stmts_opt JUMP_BACK POP_BLOCK
                              JUMP_ABSOLUTE COME_FROM_LOOP

        whilestmt         ::= SETUP_LOOP testexpr return_stmts          POP_BLOCK
                              COME_FROM_LOOP

        whileelsestmt     ::= SETUP_LOOP testexpr l_stmts_opt JUMP_BACK POP_BLOCK
                              else_suite COME_FROM_LOOP
        while1elsestmt    ::= SETUP_LOOP          l_stmts     JUMP_BACK
                              else_suite COME_FROM_LOOP

        whileelselaststmt ::= SETUP_LOOP testexpr l_stmts_opt JUMP_BACK POP_BLOCK
                              else_suitec COME_FROM_LOOP
        whileTruestmt     ::= SETUP_LOOP l_stmts_opt          JUMP_BACK POP_BLOCK
                              COME_FROM_LOOP

        while1stmt        ::= SETUP_LOOP l_stmts

        # Python < 3.5 no POP BLOCK
        whileTruestmt     ::= SETUP_LOOP l_stmts_opt JUMP_BACK
                              COME_FROM_LOOP
        whileTruestmt     ::= SETUP_LOOP return_stmts
                              COME_FROM_LOOP

        # FIXME: investigate - can code really produce a NOP?
        whileTruestmt     ::= SETUP_LOOP l_stmts_opt JUMP_BACK NOP
                              COME_FROM_LOOP
        whileTruestmt     ::= SETUP_LOOP l_stmts_opt JUMP_BACK POP_BLOCK NOP
                              COME_FROM_LOOP
        whileTruestmt     ::= SETUP_LOOP l_stmts_opt JUMP_BACK POP_BLOCK NOP
                              COME_FROM_LOOP
        forstmt           ::= SETUP_LOOP expr _for designator for_block POP_BLOCK NOP
                              COME_FROM_LOOP
        """

    def p_genexpr3(self, args):
        '''
        load_genexpr ::= LOAD_GENEXPR
        load_genexpr ::= BUILD_TUPLE_1 LOAD_GENEXPR LOAD_CONST

        # Is there something general going on here?
        dictcomp ::= load_closure LOAD_DICTCOMP LOAD_CONST MAKE_CLOSURE_0 expr GET_ITER CALL_FUNCTION_1
        '''

    def p_expr3(self, args):
        '''
        expr ::= LOAD_CLASSNAME

        # Python 3.4+
        expr ::= LOAD_CLASSDEREF

        # Python3 drops slice0..slice3

        # In Python 2, DUP_TOP_TWO is DUP_TOPX_2
        binary_subscr2 ::= expr expr DUP_TOP_TWO BINARY_SUBSCR
        '''

    @staticmethod
    def call_fn_name(token):
        """Customize CALL_FUNCTION to add the number of positional arguments"""
        return '%s_%i' % (token.type, token.attr)

    def custom_build_class_rule(self, opname, i, token, tokens, customize):
        '''
        # Should the first rule be somehow folded into the 2nd one?
        build_class ::= LOAD_BUILD_CLASS mkfunc
                        LOAD_CLASSNAME {expr}^n-1 CALL_FUNCTION_n
                        LOAD_CONST CALL_FUNCTION_n
        build_class ::= LOAD_BUILD_CLASS mkfunc
                        expr
                        call_function
                        CALL_FUNCTION_3
         '''
        # FIXME: I bet this can be simplified
        # look for next MAKE_FUNCTION
        for i in range(i+1, len(tokens)):
            if tokens[i].type.startswith('MAKE_FUNCTION'):
                break
            elif tokens[i].type.startswith('MAKE_CLOSURE'):
                break
            pass
        assert i < len(tokens), "build_class needs to find MAKE_FUNCTION or MAKE_CLOSURE"
        assert tokens[i+1].type == 'LOAD_CONST', \
          "build_class expecting CONST after MAKE_FUNCTION/MAKE_CLOSURE"
        for i in range(i, len(tokens)):
            if tokens[i].type == 'CALL_FUNCTION':
                call_fn_tok = tokens[i]
                break
        assert call_fn_tok, "build_class custom rule needs to find CALL_FUNCTION"

        # customize build_class rule
        # FIXME: What's the deal with the two rules? Different Python versions?
        # Different situations? Note that the above rule is based on the CALL_FUNCTION
        # token found, while this one doesn't.
        call_function = self.call_fn_name(call_fn_tok)
        args_pos = call_fn_tok.attr & 0xff
        args_kw = (call_fn_tok.attr >> 8) & 0xff
        rule = ("build_class ::= LOAD_BUILD_CLASS mkfunc %s"
                "%s" % (('expr ' * (args_pos - 1) + ('kwarg ' * args_kw)),
                        call_function))
        self.add_unique_rule(rule, opname, token.attr, customize)
        return

    def custom_classfunc_rule(self, opname, token, customize):
        """
        call_function ::= expr {expr}^n CALL_FUNCTION_n
        call_function ::= expr {expr}^n CALL_FUNCTION_VAR_n POP_TOP
        call_function ::= expr {expr}^n CALL_FUNCTION_VAR_KW_n POP_TOP
        call_function ::= expr {expr}^n CALL_FUNCTION_KW_n POP_TOP

        classdefdeco2 ::= LOAD_BUILD_CLASS mkfunc {expr}^n-1 CALL_FUNCTION_n
        """
        # Low byte indicates number of positional paramters,
        # high byte number of positional parameters
        args_pos = token.attr & 0xff
        args_kw = (token.attr >> 8) & 0xff
        nak = ( len(opname)-len('CALL_FUNCTION') ) // 3
        token.type = self.call_fn_name(token)
        rule = ('call_function ::= expr '
                + ('pos_arg ' * args_pos)
                + ('kwarg ' * args_kw)
                + 'expr ' * nak + token.type)
        self.add_unique_rule(rule, token.type, args_pos, customize)
        rule = ('classdefdeco2 ::= LOAD_BUILD_CLASS mkfunc %s%s_%d'
                %  (('expr ' * (args_pos-1)), opname, args_pos))
        self.add_unique_rule(rule, token.type, args_pos, customize)

    def add_make_function_rule(self, rule, opname, attr, customize):
        """Python 3.3 added a an addtional LOAD_CONST before MAKE_FUNCTION and
        this has an effect on many rules.
        """
        new_rule = rule % (('LOAD_CONST ') * (1 if  self.version >= 3.3 else 0))
        self.add_unique_rule(new_rule, opname, attr, customize)

    def add_custom_rules(self, tokens, customize):
        """
        Special handling for opcodes such as those that take a variable number
        of arguments -- we add a new rule for each:

            unpack_list ::= UNPACK_LIST_n {expr}^n
            unpack      ::= UNPACK_TUPLE_n {expr}^n
            unpack      ::= UNPACK_SEQEUENCE_n {expr}^n
            unpack_ex ::=   UNPACK_EX_b_a {expr}^(a+b)

            # build_class (see load_build_class)

            build_list  ::= {expr}^n BUILD_LIST_n
            build_list  ::= {expr}^n BUILD_TUPLE_n

            load_closure  ::= {LOAD_CLOSURE}^n BUILD_TUPLE_n
            # call_function (see custom_classfunc_rule)

            # ------------
            # Python <= 3.2 omits LOAD_CONST before MAKE_
            # Note: are the below specific instances of a more general case?
            # ------------

            # Is there something more general than this? adding pos_arg?
            # Is there something corresponding using MAKE_CLOSURE?
            dictcomp ::= LOAD_DICTCOMP [LOAD_CONST] MAKE_FUNCTION_0 expr
                           GET_ITER CALL_FUNCTION_1

            genexpr  ::= {pos_arg}^n load_genexpr [LOAD_CONST] MAKE_FUNCTION_n expr
                           GET_ITER CALL_FUNCTION_1
            genexpr  ::= {expr}^n load_closure LOAD_GENEXPR [LOAD_CONST]
                          MAKE_CLOSURE_n expr GET_ITER CALL_FUNCTION_1
            listcomp ::= {pos_arg}^n LOAD_LISTCOMP [LOAD_CONST] MAKE_CLOSURE_n expr
                           GET_ITER CALL_FUNCTION_1
            listcomp ::= {pos_arg}^n load_closure LOAD_LISTCOMP [LOAD_CONST]
                           MAKE_CLOSURE_n expr GET_ITER CALL_FUNCTION_1

            # Is there something more general than this? adding pos_arg?
            # Is there something corresponding using MAKE_CLOSURE?
            For example:
            # setcomp ::= {pos_arg}^n LOAD_SETCOMP [LOAD_CONST] MAKE_CLOSURE_n
                        GET_ITER CALL_FUNCTION_1

            setcomp  ::= LOAD_SETCOMP [LOAD_CONST] MAKE_FUNCTION_0 expr
                           GET_ITER CALL_FUNCTION_1
            setcomp  ::= {pos_arg}^n load_closure LOAD_SETCOMP [LOAD_CONST]
                           MAKE_CLOSURE_n expr GET_ITER CALL_FUNCTION_1

            mkfunc   ::= {pos_arg}^n load_closure [LOAD_CONST] MAKE_FUNCTION_n
            mkfunc   ::= {pos_arg}^n load_closure [LOAD_CONST] MAKE_CLOSURE_n
            mkfunc   ::= {pos_arg}^n [LOAD_CONST] MAKE_FUNCTION_n
            mklambda ::= {pos_arg}^n LOAD_LAMBDA [LOAD_CONST] MAKE_FUNCTION_n

        For PYPY:
            load_attr ::= expr LOOKUP_METHOD
            call_function ::= expr CALL_METHOD
        """
        saw_format_value = False
        for i, token in enumerate(tokens):
            opname = token.type
            opname_base = opname[:opname.rfind('_')]

            if opname == 'PyPy':
                self.addRule("""
                    stmt ::= assign3_pypy
                    stmt ::= assign2_pypy
                    assign3_pypy ::= expr expr expr designator designator designator
                    assign2_pypy ::= expr expr designator designator
                """, nop_func)
                continue
            elif opname == 'FORMAT_VALUE':
                # Python 3.6+
                self.addRule("""
                    expr ::= fstring_expr
                    fstring_expr ::= expr FORMAT_VALUE
                """, nop_func)

            elif opname in ('CALL_FUNCTION', 'CALL_FUNCTION_VAR',
                            'CALL_FUNCTION_VAR_KW', 'CALL_FUNCTION_KW'):
                self.custom_classfunc_rule(opname, token, customize)
            elif opname == 'LOAD_DICTCOMP':
                rule_pat = ("dictcomp ::= LOAD_DICTCOMP %sMAKE_FUNCTION_0 expr "
                            "GET_ITER CALL_FUNCTION_1")
                self.add_make_function_rule(rule_pat, opname, token.attr, customize)
            elif opname == 'LOAD_SETCOMP':
                # Should this be generalized and put under MAKE_FUNCTION?
                rule_pat = ("setcomp ::= LOAD_SETCOMP %sMAKE_FUNCTION_0 expr "
                            "GET_ITER CALL_FUNCTION_1")
                self.add_make_function_rule(rule_pat, opname, token.attr, customize)
            elif opname == 'LOAD_BUILD_CLASS':
                self.custom_build_class_rule(opname, i, token, tokens, customize)
            elif opname_base in ('BUILD_LIST', 'BUILD_TUPLE', 'BUILD_SET'):
                v = token.attr
                rule = ('build_list ::= ' + 'expr1024 ' * int(v//1024) +
                                        'expr32 ' * int((v//32)%32) + 'expr '*(v%32) + opname)
                self.add_unique_rule(rule, opname, token.attr, customize)
                if opname_base == 'BUILD_TUPLE':
                    rule = ('load_closure ::= %s%s' % (('LOAD_CLOSURE ' * v), opname))
                    self.add_unique_rule(rule, opname, token.attr, customize)
                if opname_base == 'BUILD_LIST' and saw_format_value:
                    format_or_str_n = "formatted_value_or_str_%s" % v
                    self.addRule("""
                    expr ::= joined_str
                    joined_str ::=  LOAD_CONST LOAD_ATTR %s CALL_FUNCTION_1
                    %s ::= %s%s
                    """ % (format_or_str_n, format_or_str_n, ("formatted_value_or_str " *v), opname),
                                 nop_func)

            elif opname == 'LOOKUP_METHOD':
                # A PyPy speciality - DRY with parse2
                self.add_unique_rule("load_attr ::= expr LOOKUP_METHOD",
                                     opname, token.attr, customize)
                continue
            elif opname == 'JUMP_IF_NOT_DEBUG':
                self.add_unique_rule(
                    "stmt ::= assert_pypy", opname, v, customize)
                self.add_unique_rule(
                    "stmt ::= assert2_pypy", opname_base, v, customize)
                self.add_unique_rule(
                    "assert_pypy ::= JUMP_IF_NOT_DEBUG assert_expr jmp_true "
                    "LOAD_ASSERT RAISE_VARARGS_1 COME_FROM",
                    opname, token.attr, customize)
                self.add_unique_rule(
                    "assert2_pypy ::= JUMP_IF_NOT_DEBUG assert_expr jmp_true "
                    "LOAD_ASSERT expr CALL_FUNCTION_1 RAISE_VARARGS_1 COME_FROM",
                    opname_base, v, customize)
                continue
            elif opname_base == 'BUILD_MAP':
                kvlist_n = "kvlist_%s" % token.attr
                if opname == 'BUILD_MAP_n':
                    # PyPy sometimes has no count. Sigh.
                    rule = ('dictcomp_func ::= BUILD_MAP_n LOAD_FAST FOR_ITER designator '
                            'comp_iter JUMP_BACK RETURN_VALUE RETURN_LAST')
                    self.add_unique_rule(rule, 'dictomp_func', 1, customize)

                    kvlist_n = 'kvlist_n'
                    rule = 'kvlist_n ::=  kvlist_n kv3'
                    self.add_unique_rule(rule, 'kvlist_n', 0, customize)
                    rule = 'kvlist_n ::='
                    self.add_unique_rule(rule, 'kvlist_n', 1, customize)
                    rule = "mapexpr ::=  BUILD_MAP_n kvlist_n"
                elif self.version >= 3.5:
                    rule = kvlist_n + ' ::= ' + 'expr ' * (token.attr*2)
                    self.add_unique_rule(rule, opname, token.attr, customize)
                    rule = "mapexpr ::=  %s %s" % (kvlist_n, opname)
                else:
                    rule = kvlist_n + ' ::= ' + 'expr expr STORE_MAP ' * token.attr
                    self.add_unique_rule(rule, opname, token.attr, customize)
                    rule = "mapexpr ::=  %s %s" % (opname, kvlist_n)
                self.add_unique_rule(rule, opname, token.attr, customize)
            elif opname_base in ('UNPACK_EX'):
                before_count, after_count = token.attr
                rule = 'unpack ::= ' + opname + ' designator' * (before_count + after_count + 1)
                self.add_unique_rule(rule, opname, token.attr, customize)
            elif opname_base in ('UNPACK_TUPLE', 'UNPACK_SEQUENCE'):
                rule = 'unpack ::= ' + opname + ' designator' * token.attr
                self.add_unique_rule(rule, opname, token.attr, customize)
            elif opname_base == 'UNPACK_LIST':
                rule = 'unpack_list ::= ' + opname + ' designator' * token.attr
            elif opname_base.startswith('MAKE_FUNCTION'):
                # DRY with MAKE_CLOSURE
                args_pos, args_kw, annotate_args  = token.attr

                rule_pat = ("genexpr ::= %sload_genexpr %%s%s expr "
                            "GET_ITER CALL_FUNCTION_1" % ('pos_arg '* args_pos, opname))
                self.add_make_function_rule(rule_pat, opname, token.attr, customize)
                rule_pat = ('mklambda ::= %sLOAD_LAMBDA %%s%s' % ('pos_arg '* args_pos, opname))
                self.add_make_function_rule(rule_pat, opname, token.attr, customize)
                rule_pat  = ("listcomp ::= %sLOAD_LISTCOMP %%s%s expr "
                             "GET_ITER CALL_FUNCTION_1" % ('expr ' * args_pos, opname))
                self.add_make_function_rule(rule_pat, opname, token.attr, customize)

                if self.version == 3.3:
                    # positional args after keyword args
                    rule = ('mkfunc ::= kwargs %s%s %s' %
                            ('pos_arg ' * args_pos, 'LOAD_CONST '*2,
                             opname))
                elif self.version > 3.3:
                    # positional args before keyword args
                    rule = ('mkfunc ::= %skwargs %s %s' %
                            ('pos_arg ' * args_pos, 'LOAD_CONST '*2,
                             opname))
                else:
                    rule = ('mkfunc ::= kwargs %sexpr %s' %
                            ('pos_arg ' * args_pos, opname))
                self.add_unique_rule(rule, opname, token.attr, customize)
            elif opname_base == 'CALL_METHOD':
                # PyPy only - DRY with parse2

                # FIXME: The below argument parsing will be wrong when PyPy gets to 3.6
                args_pos = (token.attr & 0xff)          # positional parameters
                args_kw = (token.attr >> 8) & 0xff      # keyword parameters

                # number of apply equiv arguments:
                nak = ( len(opname_base)-len('CALL_METHOD') ) // 3
                rule = ('call_function ::= expr '
                        + ('pos_arg ' * args_pos)
                        + ('kwarg ' * args_kw)
                        + 'expr ' * nak + opname)
                self.add_unique_rule(rule, opname, token.attr, customize)
            elif opname.startswith('MAKE_CLOSURE'):
                # DRY with MAKE_FUNCTION
                # Note: this probably doesn't handle kwargs proprerly
                args_pos, args_kw, annotate_args  = token.attr

                rule_pat = ("genexpr ::= %sload_closure load_genexpr %%s%s expr "
                            "GET_ITER CALL_FUNCTION_1" % ('pos_arg '* args_pos, opname))
                self.add_make_function_rule(rule_pat, opname, token.attr, customize)
                rule_pat = ('mklambda ::= %sload_closure LOAD_LAMBDA %%s%s' %
                            ('pos_arg '* args_pos, opname))
                self.add_make_function_rule(rule_pat, opname, token.attr, customize)
                rule_pat = ('listcomp ::= %sload_closure LOAD_LISTCOMP %%s%s expr '
                            'GET_ITER CALL_FUNCTION_1' % ('pos_arg ' * args_pos, opname))
                self.add_make_function_rule(rule_pat, opname, token.attr, customize)
                rule_pat = ('setcomp ::= %sload_closure LOAD_SETCOMP %%s%s expr '
                            'GET_ITER CALL_FUNCTION_1' % ('pos_arg ' * args_pos, opname))
                self.add_make_function_rule(rule_pat, opname, token.attr, customize)

                self.add_unique_rule('dictcomp ::= %sload_closure LOAD_DICTCOMP %s '
                                     'expr GET_ITER CALL_FUNCTION_1' %
                                     ('pos_arg '* args_pos, opname),
                                     opname, token.attr, customize)

                # FIXME: kwarg processing is missing here.
                # Note order of kwargs and pos args changed between 3.3-3.4
                if self.version <= 3.2:
                    rule = ('mkfunc ::= kwargs %sload_closure LOAD_CONST kwargs %s'
                            % ('expr ' * args_pos, opname))
                elif self.version == 3.3:
                    rule = ('mkfunc ::= kwargs %sload_closure LOAD_CONST LOAD_CONST %s'
                            % ('expr ' * args_pos, opname))
                elif self.version >= 3.4:
                    rule = ('mkfunc ::= %skwargs load_closure LOAD_CONST LOAD_CONST %s'
                            % ('expr ' * args_pos, opname))

                self.add_unique_rule(rule, opname, token.attr, customize)
                rule = ('mkfunc ::= %sload_closure load_genexpr %s'
                        % ('pos_arg ' * args_pos, opname))
                self.add_unique_rule(rule, opname, token.attr, customize)
                rule = ('mkfunc ::= %sload_closure LOAD_CONST %s'
                        % ('expr ' * args_pos, opname))
                self.add_unique_rule(rule, opname, token.attr, customize)
        return


class Python31Parser(Python3Parser):

    def p_31(self, args):
        """
        # Store locals is only in Python 3.0 to 3.3
        stmt ::= store_locals
        store_locals ::= LOAD_FAST STORE_LOCALS
        """

class Python32Parser(Python3Parser):

    def p_32(self, args):
        """
        # Store locals is only in Python 3.0 to 3.3
        stmt ::= store_locals
        store_locals ::= LOAD_FAST STORE_LOCALS
        """

class Python33Parser(Python3Parser):
    def p_33(self, args):
        """
        # Store locals is only in Python 3.0 to 3.3
        stmt ::= store_locals
        store_locals ::= LOAD_FAST STORE_LOCALS

        # Python 3.3 adds yield from.
        expr ::= yield_from
        yield_from ::= expr expr YIELD_FROM
        """

class Python3ParserSingle(Python3Parser, PythonParserSingle):
    pass


class Python31ParserSingle(Python31Parser, PythonParserSingle):
    pass

class Python32ParserSingle(Python32Parser, PythonParserSingle):
    pass


class Python33ParserSingle(Python33Parser, PythonParserSingle):
    pass

def info(args):
    # Check grammar
    # Should also add a way to dump grammar
    p = Python3Parser()
    if len(args) > 0:
        arg = args[0]
        if arg == '3.5':
            from uncompyle6.parser.parse35 import Python35Parser
            p = Python35Parser()
        elif arg == '3.3':
            p = Python33Parser()
        elif arg == '3.2':
            p = Python32Parser()
    p.checkGrammar()


if __name__ == '__main__':
    import sys
    info(sys.argv)
