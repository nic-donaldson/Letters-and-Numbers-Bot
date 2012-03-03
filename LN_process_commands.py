import re
import random
import time
from IRC_LN_commands import *
NIL = (0, "")
random.seed(time.time())

num_pattern = re.compile(r'[0-6]*')
maths_pattern = re.compile(r'^[\(\) 0-9\*\+-/]*$')
accepted_num_pattern = re.compile(r'^[0-9]:[0-9]$')

word_list = []

for word in open("/usr/share/dict/words", 'rU'):
    if word[0].islower():
        word_list.append(word.lower().strip())

def primProcess(sock, msg):
    if msg.find("@LN BOT END") != -1:
        quitIRC(sock, "Leaving")
    if msg.find("PING") != -1:
        return (1, "PONG " + msg.split("PING")[-1])
    if msg.find("@LN DEFINE") != -1:
        return (2, msg)
    else:
        return NIL

def callCheck(msg):
    call_state = {"numbers":False,
                    "letters":False}

    if msg.find("@LN START NUMBERS") != -1:
        call_state["numbers"] = True
    if msg.find("@LN START LETTERS") != -1:
        call_state["letters"] = True

    return call_state     

# Function to see if any players
# have stated they are playing
def checkPlaying(msg):
    if msgGet(msg).strip().lower() == "playing":
        return {"playing":True, "player":getName(msg)}
    return {"playing":False}

def callOver(call_time, timeout):
    if int(time.time()) - call_time >= timeout:
        return True
    return False

# Games
# Numbers

def operate(x, y):
    if x % y == 0:
        operations = ["*", "/", "+", "-"]
    else:
        operations = ["*", '+', '-']

    random.shuffle(operations)
    return (eval(str(x) + ' ' + operations[0] + ' ' + str(y)), operations[0])

def makeSolution(nums, operators):
    soln = str(nums[0])
    operation = 0
    while len(nums) > 1:
        x = nums.pop(0)
        y = nums.pop(0)
        soln = '(' + soln + ' ' + operators[operation] + ' ' + str(y) +' )'
        z = eval(str(x) + operators[operation] + str(y))
        nums = [z] + nums
        operation += 1


    return soln

def makeTarget(numbers):
    random.shuffle(numbers)
    rand_nums = numbers
    operators = ['' for x in xrange(6)]
    operation = 0
    while len(numbers) > 1:
        x, y = numbers[0], numbers[1]
        z = 5000
        while z > 1000 or z < 1:
            z, operator = operate(x, y)
            operators[operation] = operator
        numbers = [z] + numbers[2:]
        operation += 1

    solution = makeSolution(rand_nums, operators)
    return (numbers[0], solution)

def pickFrom(nums, num):
    new_nums = []
    for i in xrange(num):
        random.shuffle(nums)
        new_nums.append(nums[0])
    return new_nums        

def makeProblem(large, small, larges, smalls):
    large_nums = pickFrom(larges, large)
    small_nums = pickFrom(smalls, small)

    target, solution = makeTarget(large_nums+small_nums)
    
    return (target, large_nums+small_nums, solution)

# def numsGiven(msg, chooser):
#     if getName(msg) == chooser:
#         if len(msgGet(msg).split(":")) == 2:
#             x, y = msgGet(msg).split(":")
#             if re.match(num_pattern, x) and re.match(num_pattern, y):
#                 if int(x) + int(y) == 6:
#                     return True
#                 
#     return False

def numsGiven(msg, chooser):
    if getName(msg) == chooser:
        if re.match(accepted_num_pattern, msgGet(msg)):
            x,y = msgGet(msg).split(":")
            if int(x) >=5 or int(y) >=5:
                return False
            if int(x)+int(y) == 6:
                return True
    return False


def gameTimeOut(game_time, timeout):
    if int(time.time()) - game_time >= timeout:
        return True
    return False

# function to make sure that a message only contains
# digits and spaces and brackets
def isMaths(msg):
    if re.match(maths_pattern, msg):
        return True
    return False

def numberSanity(numbers, answer):
    # cycle through each line of the given answer
    # and remove numbers from the number list
    # as they are encountered
    for i in answer:
        line = i.replace('(', ' ').replace(')', ' ').\
                replace('+', ' ').replace('-', ' ').\
                replace('*', ' ').replace('/', ' ')
        nums = [int(x) for x in line.strip().split()]
        for j in nums:
            try: numbers.remove(j)
            except ValueError: return False
    return True

def answerEquals(answer, target):
    cur = eval(answer.pop(0))
    while len(answer) > 0:
        cur = eval (str(cur) + ' ' + answer.pop(0))
    if cur == target:
        return True
    return False
    

# function to check if a player's answer
# is correct or not
def isCorrect(target, numbers, answer):
    # check that it uses the right numbers
    if numberSanity(numbers[:], answer[:]):
        if answerEquals(answer[:], target):
            return True
    return False

def isClear(msg):
    if msg.lower().strip().find('clear') != -1:
        return True
    return False

def isScrap(msg):
    if msg.lower().strip().find('scrap') != -1:
        return True
    return False

def letterGiven(msg, chooser):
    if getName(msg) == chooser:
        m = msgGet(msg).lower().strip()
        if m.find('vowel') != -1:
            return 'v'
        elif m.find('cons') != -1:
            return 'c'
    return False

def getVowel(vowels):
    random.shuffle(vowels) 
    return vowels[0]

def getConsonant(consonants):
    random.shuffle(consonants)
    return consonants[0]

def isLetters(msg, letters):
    for i in msg:
        try: letters.remove(i)
        except ValueError: return False
    return True

def isWord(msg):
    if msg in word_list:
        return True
    return False
