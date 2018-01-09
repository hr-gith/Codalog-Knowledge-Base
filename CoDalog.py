from ParserDatalog import Parser
from NaiveEngineDatalog import Naive
from SemiNaiveEngineDatalog import SemiNaive
#from memory_profiler import profile
import time


#fp = open('memory_profiler.log', 'w')
#@profile(stream=fp)

def main():

    dlParser = Parser()
    with open("graph10.pl", "r") as inF:
        text = enumerate(inF)
        timestart = time.time()
        dlParser.parse(text)
        print("The Parser Time")
        print('%s Seconds' % (time.time() - timestart))

    print("     Menu     ")
    print("--------------")
    print("1. Naive")
    print("2. Semi-Naive")

    choiceEngine = input("Select a type for evaluation (1 or 2): ")
    choiceLogFile = input("Would you like to save list of errors in a file?(y/n)")
    choiceFactFile = input("Would you like to save list of facts in a file?(y/n)")

    # Write the result in related files
    if(choiceLogFile == 'y'):
        dlParser.printLogFile()
    if (choiceEngine == "1"):
        dlNaive = Naive()
        dlNaive.ruleList = dlParser.ruleList
        dlNaive.factEDB = dlParser.factList
        timestart = time.time()
        dlNaive.run()
        print("Naive is taking")
        print('%s Seconds' % (time.time() - timestart))
        dlNaive.printFactsToFile()


        if(choiceFactFile == 'y'):
            dlNaive.printFactsToFile()
            dlNaive.printUnifierToFile()
        print("Successfully done!\n\n")
        print("    QUERY EVALUATION")
        print("-------------------------")
        while (True):
            print("Enter '-1' to exit.")
            query = input("Enter a query (start with '?-'): ")
            if (query == '-1'):
                break
            text = enumerate([query])
            dlParser.parse(text)
            if (dlParser.queryList != []):
                # print ("parsed")
                query_result = dlNaive.queryEvaluation(dlParser.queryList)
                if ( query_result == 1): # the query is a valid fact
                    print("True")
                elif( query_result == -1): # the query is not a valid fact
                    print("False")
                else:
                    toFile = input("Do you like to save the result in the 'query_result' file?(y/n)")
                    if (toFile == 'y'):
                        with open("query_result.txt", "w") as fOut:
                            fOut.write("Query result:\n")
                            fOut.writelines("%s\n" % l for l in query_result)
                        print("Result has been saved to the file successfully")
                    else:
                        print(query_result)
            else:
                print("Syntax Error")
    elif(choiceEngine == "2"):
        dlSemiNaive = SemiNaive()
        dlSemiNaive.ruleList = dlParser.ruleList
        dlSemiNaive.factEDB = dlParser.factList
        timestart = time.time()
        dlSemiNaive.run()
        print("Semi Naive is taking")
        print('%s Seconds' % (time.time() - timestart))

        if (choiceFactFile == 'y'):
            dlSemiNaive.printFactsToFile()
            dlSemiNaive.printUnifierToFile()
        print("Successfully done!\n\n")
        print("----QUERY EVALUATION----")
        while (True):
            print("Enter '-1' to exit.")
            query = input("Enter a query (start with '?-'): ")
            if (query == '-1'):
                break
            text = enumerate([query])
            dlParser.parse(text)
            if (dlParser.queryList != []):
                # print ("parsed")
                query_result = dlSemiNaive.queryEvaluation(dlParser.queryList)
                if (query_result == 1):  # the query is a valid fact
                    print("True")
                elif (query_result == -1):  # the query is not a valid fact
                    print("False")
                else:
                    toFile = input("Do you like to save the result in the 'query_result' file?(y/n)")
                    if (toFile == 'y'):
                        with open("query_result.txt", "w") as fOut:
                            fOut.write("Query result:\n")
                            fOut.writelines("%s\n" % l for l in query_result)
                    else:
                        print(query_result)
            else:
                print("Syntax Error")
    else:
        print("The choice is not valid")


if __name__ == '__main__':
    main()
