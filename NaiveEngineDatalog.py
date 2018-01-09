import itertools
from BuiltIn import BuiltIn

class Naive:
    def __init__(self):
        self.factEDB = []
        self.factIDB = []
        self.ruleList = []
        self.globalUnifierList = []


    def queryEvaluation(self, query):
        if ('fact' in query['query']):
            if ((query['query'] in self.factEDB) or (query['query'] in self.factIDB)):
                return 1
            else:
                return -1
        else:
            predicate = query['query'][0]
            unifierList = self.getLocalUnifier(predicate)
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


    def getLocalUnifier(self, predicate):
        localUnifier = []
        allFacts = self.factIDB + self.factEDB
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


    def run(self):
        if (self.factEDB != []):
            isFixPoint = False
            while (not isFixPoint): # check fix point for Naive
                allFacts = []
                newFactNum = 0

                # finding new facts
                for rule in self.ruleList:
                    allFacts = self.factIDB + self.factEDB
                    localUnifierList = []
                    for item in rule['rule']['body']:
                        if ('identifier' in item):  # Is not a Built-in predicate
                            localUnifierList.append(self.getLocalUnifier(item))
                    # print (localUnifierList)
                    # Global unification
                    head = rule['rule']['head']
                    for line in itertools.product(*localUnifierList):
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

                        #To Handle if there are any built-In predicate in the body of the rule
                        #To get the builtIn part of the rule
                        largs = rule['rule']['body'][1:]

                        for args in largs:
                            if ('lArgument' in args):

                                builtIn = BuiltIn(globalUnifier, rule)
                                isUnified, newGlobalList = builtIn.callBuiltIn()
                                globalUnifier.update(newGlobalList)


                        if (isUnified):
                            # print(globalUnifier)
                            newFact = dict()
                            arguments = []
                            for var in head['arguments']:
                                if (var[0].isupper()):  # if var in head is a constant
                                    for item in globalUnifier:
                                        if (item == var):
                                            arguments.append(globalUnifier[item])
                                else:
                                    arguments.append(var)

                            newFact['fact'] = dict()
                            newFact['fact']['identifier'] = head['identifier']
                            newFact['fact']['arguments'] = arguments
                            # print (newFact)
                            if (newFact not in self.factIDB):
                                self.factIDB.append(newFact)
                                self.globalUnifierList.append(globalUnifier)
                                newFactNum += 1
                if (newFactNum == 0):
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
        with open("Naive_NewFacts.txt", "w") as fOut:
            fOut.write("--------EDB: Old Facts--------\n")
            fOut.writelines("%s\n" % l for l in convertedEDB)
            fOut.write("--------IDB: New Facts--------\n")
            fOut.writelines("%s\n" % l for l in convertedIDB)


    def printUnifierToFile(self):
        with open("Naive_global_Unification.txt", "w") as fOut:
            fOut.write("List of global unification:\n")
            fOut.writelines("%s\n" % l for l in self.globalUnifierList)
