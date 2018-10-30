class TestResult:
    def __init__(self, result, testName = "No Name Test"):
        self.__testName = testName
        self.__result = result

    def Name(self):
        return self.__testName

    def Result(self):
        return self.__result

class Tester:
    def __init__(self):
        self.__results = []

    def Assert(self, name, result):
        if not isinstance(result, bool):
            raise Exception("Invalid test result provided. {} is not bool".\
                            format(result))
        if not isinstance(name, str):
            raise Exception("Invalid test name provided. {} is not str"\
                            .format(name))
        self.__results.append(TestResult(result, name))

    def ShowResults(self):
        maxLen = 0
        for i in range(len(self.__results)):
            nameLen = len(self.__results[i].Name())
            if nameLen > maxLen:
                maxLen = nameLen

        numTests = len(self.__results)
        fails = 0
        print("Test Results: ")
        for i in range(numTests):
            numStr = str(i + 1) + ')' + ' '*(i + 1 < 10 and numTests >= 10)  # Don't feel like dealing with triple digits
            name = self.__results[i].Name()
            result = self.__results[i].Result()
            if not result: fails += 1 
            print("{} {} => {}".format(numStr, name + ' '*(maxLen - len(name)), result))

        print('')
        if fails == 0:
            print("ALL {} TESTS PASSED!!!".format(numTests))
        else:
            print("{}/{} TESTS FAILED".format(fails, numTests))



if __name__ == "__main__":
    t = Tester()

    # A few legitimate tests
    t.Assert("First test", 1 > 0)
    t.Assert("Second test", 1 > 2)
    t.Assert("First test", isinstance(1, int))
    t.ShowResults()

    # An invalid one - should throw exception
    t.Assert("First test", 1)
