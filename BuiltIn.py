class BuiltIn:

    def __init__(self,globalUnifier, rule):
        self.Ununified = False
        self.Notunified = False
        self.globalUnifier = globalUnifier
        self.rule = rule

    # def built(globalUnifier ,rule ):

    def equal(self  , builtinPredicate):
        self.Notunified = True
        # if one of the argument is constant
        if ('constant' in builtinPredicate):
            if (self.globalUnifier[builtinPredicate['lArgument']] == builtinPredicate['constant']):
                self.NotUnified = True
                self.globalUnifier[builtinPredicate['lArgument']] = builtinPredicate['constant']
            else:
                self.Notunified = False


        # if lArgumentand rArgument are Variables in the Builtin
        else:
            # if the argument is not in global unifier
            # add the argument to the global unifier along with the value
            if not (builtinPredicate['lArgument'] in self.globalUnifier):
                if ('rArgument' in builtinPredicate):
                    self.globalUnifier[builtinPredicate['lArgument']] = self.globalUnifier[builtinPredicate['rArgument']]
                    self.Notunified = True
                else:
                    self.globalUnifier[builtinPredicate['lArgument']] = builtinPredicate['constant']
                    self.Notunified = True

            elif (self.globalUnifier[builtinPredicate['lArgument']] == self.globalUnifier[builtinPredicate['rArgument']]):
                self.Notunified = True

            else:
                self.Notunified = False
        return self.Notunified

        # For the greater '>' builtin

    def greater(self  , builtinPredicate):
        self.NotUnified = True
        if 'constant' in builtinPredicate:
            if (int(self.globalUnifier[builtinPredicate['lArgument']]) > int(builtinPredicate['constant'])):
                self.NotUnified = True
            else:
                self.NotUnified = False
        else:
            if (int(self.globalUnifier[builtinPredicate['lArgument']]) > int(self.globalUnifier[builtinPredicate['rArgument']])):
                self.NotUnified = True
            else:
                self.NotUnified = False
        return self.NotUnified

        # For the less '<' builtin

    def lessThan(self  , builtinPredicate):
        self.NotUnified = True
        if 'constant' in builtinPredicate:

            if (int(self.globalUnifier[builtinPredicate['lArgument']]) < int(builtinPredicate['constant'])):
                self.NotUnified = True
            else:
                self.NotUnified = False
        else:
            if (int(self.globalUnifier[builtinPredicate['lArgument']]) < int(self.globalUnifier[
                builtinPredicate['rArgument']])):
                self.NotUnified = True
            else:
                self.NotUnified = False
        return self.NotUnified

        # For the lessThanEqual '<=' builtin

    def lessThanEqual(self , builtinPredicate):
        self.NotUnified = False
        if (self.lessThan(builtinPredicate) or self.equal(builtinPredicate)):
            self.NotUnified = True
        return self.NotUnified

        # For the greaterThanEqual '>=' builtin

    def greaterthanEqual(self  , builtinPredicate):
        self.NotUnified = False
        if (self.greater(builtinPredicate) or self.equal(builtinPredicate)):
            self.NotUnified = True
        return self.NotUnified

        # For the notequal '!=' builtin

    def notEqual(self  , builtinPredicate):
        self.NotUnified = False
        if not (self.equal(builtinPredicate)):
            self.NotUnified = True
        return self.NotUnified


        # swicth for different built-In operations
    def callBuiltIn(self):

        options = {'=': self.equal,
                   '>': self.greater,
                   '<': self.lessThan,
                   '<=':self.lessThanEqual,
                   '>=':self.greaterthanEqual,
                   '!=':self.notEqual
                   }  # To get the builtIn part of the rule
        largs = self.rule['rule']['body'][1:]
        for args in largs:
            if ('lArgument' in args):
                self.Ununified = options[args['operator']](args)
            if not(self.Ununified):
                break

        return self.Ununified , self.globalUnifier


