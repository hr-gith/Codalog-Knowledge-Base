import pyparsing as pp


class Parser:
    def __init__(self):
        self.factList = []
        self.ruleList = []
        self.errorList = []
        self.warningList = []
        self.queryList = []
        self.queryErrorList = []

        colonDash = pp.Literal(":-")
        integer = pp.Word(pp.nums)
        decimal = pp.Combine(pp.Word(pp.nums) + "." + pp.Word(pp.nums))
        number = decimal | integer

        # TODO: special characters should be tested
        string = pp.Literal('\"').suppress() + pp.Word(pp.printables + ' ', excludeChars='\'') + pp.Literal('\"').suppress()
        self.comment = pp.Group(pp.Literal('%')+ pp.Word(pp.printables + ' ', excludeChars='\''))

        # Identifier is a word started with a lower case letter
        identifier = pp.Word(pp.alphas.lower(), pp.alphanums + '_')

        constant = string | number | identifier
        constantList = pp.delimitedList(constant)

        variable = pp.Word(pp.alphas.upper(), pp.alphanums + '_')
        variableList = pp.delimitedList(variable)

        argumentList = pp.ZeroOrMore(constant + pp.Literal(",").suppress()) + \
                       variableList + \
                       pp.Optional(pp.Literal(",").suppress() + pp.delimitedList(constant | variable))

        # Built-in predicate
        operator = pp.oneOf("< <= > >= = !=")

        builtInPredicate = pp.Group(
             (variable.setResultsName('lArgument') + \
              operator.setResultsName('operator') +\
                (constant).setResultsName('constant')) | \
            (constant.setResultsName('constant') + \
             operator.setResultsName('operator') +\
                variable.setResultsName('rArgument')) |
             (variable.setResultsName('lArgument') + \
              operator.setResultsName('operator') +\
              variable.setResultsName('rArgument')))

        # predicate => argumentList has at least one variable inside
        predicate = pp.Group(
            identifier.setResultsName('identifier') + "(" + pp.Group(argumentList).setResultsName('arguments') + ")")

        self.fact = pp.Group(
            identifier.setResultsName('identifier') + "(" + pp.Group(constantList).setResultsName('arguments') + \
            ")" + pp.Literal(".").suppress() + \
            pp.Optional(self.comment.suppress())).setResultsName('fact')

        self.rule = pp.Group(predicate.setResultsName('head') + colonDash + \
                        pp.Group(pp.delimitedList(predicate | builtInPredicate | self.fact)) \
                        .setResultsName('body') + pp.Literal(".").suppress()+ \
                        pp.Optional(self.comment.suppress())).setResultsName('rule')

        self.query = pp.Group(pp.Literal("?").suppress()+ pp.Literal("-").suppress()+\
                    ((predicate+pp.Literal('.').suppress())|self.fact)).setResultsName('query')

    def checkSafety(self,newRule,lineNo):
        #self.warningList.append(tokens['head']['arguments'])
        headVariables = []
        bodyNormalVars = []
        builtInPredicates = []
        for arg in newRule['rule']['head']['arguments']:
            if (arg[0].isupper()):
                headVariables.append(arg)
        for item in newRule['rule']['body']:
            if ('arguments' in item):
                for arg in item['arguments']:
                    if (arg[0].isupper()):
                        bodyNormalVars.append(arg)
            else:
                builtInPredicates.append(item)
        # Change bodyVariables and headVariables to a unique set to remove duplicate variables
        bodyNormalVars = set(bodyNormalVars)
        headVariables = set(headVariables)
        # Safety type 1: head variables should be appeared on the normal predicate body
        #                or in an equality built-in predicate with constant or a normal predicate's variable
        safeT1 = True
        for var in headVariables:
            safe = True
            if (not (var in bodyNormalVars)):
                safe = False
                for btPredicate in builtInPredicates:
                    if (btPredicate['operator'] == '='):
                        if (('lArgument' in btPredicate) and var == btPredicate['lArgument']):
                            if (('rArgument' in btPredicate) and (btPredicate['rArgument'] in bodyNormalVars)):
                                safe = True
                            elif (('constant' in btPredicate)):
                                safe = True
                        elif (('rArgument' in btPredicate) and var == btPredicate['rArgument']):
                            if (('lArgument' in btPredicate) and (btPredicate['lArgument'] in bodyNormalVars)):
                                safe = True
                            elif (('constant' in btPredicate)):
                                safe = True
            if (not safe):
                self.warningList.append("line {} : variable {} is not safe".format(lineNo + 1, var))
            safeT1 = (safeT1 and safe)
        #Safety type2: Variables in built-in predicates should be bounded
        safeT2 = True
        for btPredicate in builtInPredicates:
            safe = False
            if (btPredicate['operator'] != '='):
                # Non equality built-in predicate
                if ('constant' in btPredicate):
                    if (('lArgument' in btPredicate) and\
                        (btPredicate['lArgument'] in bodyNormalVars)):
                        safe = True
                    elif (('rArgument' in btPredicate) and \
                          (btPredicate['rArgument'] in bodyNormalVars)):
                        safe = True
                else:
                    if (all (x in bodyNormalVars for x in [btPredicate['lArgument'],btPredicate['rArgument']])):
                        safe = True
            else: # Equality built-in predicate
                if ('constant' in btPredicate):
                    if (('lArgument' in btPredicate) and\
                        ((btPredicate['lArgument'] in bodyNormalVars) or\
                                 (btPredicate['lArgument'] in headVariables))):
                        safe = True
                    elif (('rArgument' in btPredicate) and\
                        ((btPredicate['rArgument'] in bodyNormalVars) or\
                                 (btPredicate['rArgument'] in headVariables))):
                        safe = True
                else:
                    if (all (x in bodyNormalVars for x in [btPredicate['lArgument'],btPredicate['rArgument']])):
                        safe = True
                    elif (((btPredicate['lArgument'] in bodyNormalVars) and\
                        (btPredicate['rArgument'] in headVariables)) or \
                        ((btPredicate['rArgument'] in bodyNormalVars) and\
                        (btPredicate['lArgument'] in headVariables))):
                        safe = True
            if (not safe):
                self.warningList.append("line {} : variables in built-in predicate is not bounded: {}".format(lineNo + 1,btPredicate))
            safeT2 = (safeT2 and safe)
        return (safeT2 and safeT1)


    def parse(self,text):
        for i, line in text:
            if (line != '\n'):
                try:
                    comment = self.comment.parseString(line)
                except pp.ParseException as commentError:
                    try:
                        newQuery = self.query.parseString(line).asDict()
                        self.queryList = newQuery
                    except pp.ParseException as queryError:
                        try:
                            newFact = self.fact.parseString(line).asDict()
                            if (not self.isExisted(newFact, self.factList)):
                                self.factList.append(newFact)
                        except pp.ParseException as factError:
                            try:
                                newRule = self.rule.parseString(line).asDict()
                                if (self.checkSafety(newRule,i)):
                                    if (not self.isExisted(newRule, self.ruleList)):
                                        self.ruleList.append(newRule)
                            except pp.ParseException as ruleError:
                                self.errorList.append("line {}: It is not non of fact, rule, nor query ".format(i+1))
                                self.errorList.append("         Error for being a fact => {}".format(factError))
                                self.errorList.append("         Error for being a rule => {}".format(ruleError))
                                self.errorList.append("         Error for being a query => {}".format(queryError))

    def isExisted(self, item, list):
        if (item in list):
            return True
        elif ('fact' in item):
            for x in list:
                if (item['fact']['identifier'] == x['fact']['identifier']):
                    if (len(item['fact']['arguments']) != len(x['fact']['arguments'])):
                        return True
            return False

    def printLogFile(self):
        with open("log.txt", "w") as fOut:
            fOut.write("List of Errors:\n")
            fOut.writelines("%s\n" % l for l in self.errorList)
            fOut.write("\n\nList of Warnings:\n")
            fOut.writelines("%s\n" % l for l in self.warningList)


    def printParsedFacts(self):
        with open("facts.txt", "w") as fOut:
            fOut.write("EDB: List of Facts:\n")
            fOut.writelines("%s\n" % l for l in self.factList)


    def printParsedRules(self):
        with open("rules.txt", "w") as fOut:
            fOut.write("List of Rules:\n")
            fOut.writelines("%s\n" % l for l in self.ruleList)



