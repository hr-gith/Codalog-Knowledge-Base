import itertools
import copy
from BuiltIn import BuiltIn


class SemiNaive:
    def __init__(self):
        self.factEDB = []
        self.ruleList = []
        self.factIDB = []
        self.globalUnifierList = []


    def queryEvaluation(self, query):
        if ('fact' in query['query']):
            if ((query['query'] in self.factEDB) or (query['query'] in self.factIDB)):
                return 1
            else:
                return -1
        else:
            predicate = query['query'][0]
            allFacts = self.factIDB + self.factEDB
            unifierList = self.getLocalUnifier(predicate, allFacts)
            result = []
            for line in unifierList:
                fact = predicate['identifier'] + '('
                for arg in predicate['arguments']:
                    if(arg[0].isupper()):
                        for item in line:
                            if(item == arg):
                                fact += line[item]
                                fact += ','
                                break
                    else:
                        fact += arg
                        fact += ','
                fact = fact[:-1]
                fact += ')'
                result.append(fact)
            return result


    def getLocalUnifier(self, predicate, allFacts):
        localUnifier = []
        for fact in allFacts:
            isUnified = True
            tempUnifier = dict()
            if ((fact['fact']['identifier'] == predicate['identifier']) and \
                        (len(predicate['arguments']) == len(fact['fact']['arguments']))):
                for i in range(len(predicate['arguments'])):
                    if (predicate['arguments'][i][0].isupper()):
                        if (predicate['arguments'][i] in tempUnifier):
                            if (tempUnifier[predicate['arguments'][i]] != fact['fact']['arguments'][i]):
                                isUnified = False
                                break
                        else:
                            tempUnifier[predicate['arguments'][i]] = fact['fact']['arguments'][i]
                    elif (predicate['arguments'][i] != fact['fact']['arguments'][i]):
                        isUnified = False
                        break
            else:
                isUnified = False
            if (isUnified):
                localUnifier.append(tempUnifier)
        return localUnifier

    def getGlobalUnifier(self, rule, line):
        isUnified = True
        globalUnifier = dict()
        for localU in line:
            for item in localU:
                if (item in globalUnifier):
                    if (localU[item] != globalUnifier[item]):
                        isUnified = False
                        break
                else:
                    globalUnifier[item] = localU[item]
            if (not isUnified):
                break

        # BuiltIn Predicate
        largs = rule['rule']['body'][1:]

        for args in largs:
            if ('lArgument' in args):
                builtIn = BuiltIn(globalUnifier, rule)
                isUnified, newGlobalList = builtIn.callBuiltIn()
                globalUnifier.update(newGlobalList)
        if (isUnified):
            return globalUnifier
        else:
            return -1


    def run(self):
        if (self.factEDB != []):
            counter = 0
            isFixPoint = False
            tempList = []
            newFactList = []
            oldFactList = []
            while (not isFixPoint): # check fix point for semi-naive
                if (counter == 0):   # using only all existed facts in EDB as new facts
                    newFactList = self.factEDB
                    counter += 1
                elif (counter == 1):
                    oldFactList = self.factEDB
                    newFactList = copy.deepcopy(tempList)
                    tempList = []
                    counter += 1
                else:
                    self.factIDB = self.factIDB + newFactList
                    oldFactList = self.factEDB + self.factIDB
                    newFactList = copy.deepcopy(tempList)
                    tempList = []

                #finding new facts
                for rule in self.ruleList:
                    allNewPredicate = set().union((d['fact']['identifier'] for d in newFactList))
                    allOldPredicate = set().union((d['fact']['identifier'] for d in oldFactList))
                    allFactsPredicate = set.union (allNewPredicate | allOldPredicate)
                    allPredicateRule = set().union((p['identifier'] for p in rule['rule']['body'] if ('lArgument' not in p)))

                    # check if rule has at least one predicate matched with new facts
                    # check if all the rule's predicates are existed in old and new facts
                    if (([i for i in allNewPredicate if i in allPredicateRule] != []) and\
                                (len([i for i in allFactsPredicate if i in allPredicateRule]) == len(allPredicateRule))):
                        oldLocalUnifierList = []
                        newLocalUnifierList = []
                        # Local Unification using new facts
                        for item in rule['rule']['body']:
                            if ('identifier' in item):  # Is not a Built-in predicate
                                newLocalUnifierList.append( self.getLocalUnifier(item,newFactList))
                        # Local Unification using old facts
                        for item in rule['rule']['body']:
                            if ('identifier' in item):  # Is not a Built-in predicate
                                oldLocalUnifierList.append( self.getLocalUnifier(item,oldFactList))
                        # Filter local unification to avoid joining old facts with old facts
                        # join predicates using only new facts
                        # Global unification
                        #for line in self.product(*newLocalUnifierList):
                        for line in itertools.product(*newLocalUnifierList):
                            globalUnifier = self.getGlobalUnifier(rule, line)
                            if (globalUnifier == -1):
                                isUnified = False
                            else:
                                isUnified = True
                            # create a new fact by assigning value to the head variables
                            head = rule['rule']['head']
                            if (isUnified):
                                newFact = dict()
                                arguments = []
                                for var in head['arguments']:
                                    if (var[0].isupper()):  # if var in head is a constant
                                        for item in globalUnifier:
                                            if (item == var):
                                                arguments.append(globalUnifier[item])
                                                break
                                    else:
                                        arguments.append(var)
                                newFact['fact'] = dict()
                                newFact['fact']['identifier'] = head['identifier']
                                newFact['fact']['arguments'] = arguments
                                if ((newFact not in newFactList) and
                                        (newFact not in oldFactList) and
                                        (newFact not in tempList)):
                                    self.globalUnifierList.append(globalUnifier)
                                    tempList.append(newFact)
                        # join predicates using old facts and new facts
                        if (not (all(item == [] for item in oldLocalUnifierList))):
                            stuff = list(range(0, len(newLocalUnifierList)))
                            for i in range(0, len(stuff) + 1):
                                for subset in itertools.combinations(stuff, i):
                                    temp = copy.deepcopy(oldLocalUnifierList)
                                    for j in subset:
                                        temp[j] = newLocalUnifierList[j]
                                    if ([] not in temp):
                                        # Global unification
                                        for line in itertools.product(*temp):
                                            globalUnifier = self.getGlobalUnifier(rule,line)
                                            if (globalUnifier == -1):
                                                isUnified = False
                                            else:
                                                isUnified = True
                                            # create a new fact by assigning value to the head variables
                                            head = rule['rule']['head']
                                            if (isUnified):
                                                newFact = dict()
                                                arguments = []
                                                for var in head['arguments']:
                                                    if (var[0].isupper()):  # if var in head is a constant
                                                        for item in globalUnifier:
                                                            if (item == var):
                                                                arguments.append(globalUnifier[item])
                                                                break
                                                    else:
                                                        arguments.append(var)
                                                newFact['fact'] = dict()
                                                newFact['fact']['identifier'] = head['identifier']
                                                newFact['fact']['arguments'] = arguments
                                                if ((newFact not in newFactList) and
                                                        (newFact not in oldFactList) and
                                                        (newFact not in tempList)):
                                                    self.globalUnifierList.append(globalUnifier)
                                                    tempList.append(newFact)
                if (tempList == [] and counter != 1):
                    self.factIDB = self.factIDB + newFactList
                    isFixPoint = True


    def getConvertedFacts(self, factList):
        converted_facts = []
        for item in factList:
            fact = item['fact']['identifier'] + '('
            args = item['fact']['arguments']
            for arg in args:
                fact += arg
                fact += ','
            fact = fact[:-1]
            fact += ')'
            converted_facts.append(fact)
        return converted_facts


    def printFactsToFile(self):
        convertedEDB = self.getConvertedFacts(self.factEDB)
        convertedIDB = self.getConvertedFacts(self.factIDB)
        with open("Semi_NewFacts.txt", "w") as fOut:
            fOut.write("--------EDB: Old Facts--------\n")
            fOut.writelines("%s\n" % l for l in convertedEDB)
            fOut.write("--------IDB: New Facts--------\n")
            fOut.writelines("%s\n" % l for l in convertedIDB)


    def printUnifierToFile(self):
        with open("Semi_Naive_global_Unification.txt", "w") as fOut:
            fOut.write("List of global unification:\n")
            fOut.writelines("%s\n" % l for l in self.globalUnifierList)

