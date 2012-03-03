# Letters and Numbers IRC bot

data = ''

larges = [100, 75, 50, 25]
smalls = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# numbers of vowels and consonants based off of a standard
# English Scrabble board
# TODO: remake this with percentages

vowels = []
consonants = []

for i in \
        """
        N R T 6
        S D L 4
        G 3
        V W P F C B M H Y 2
        K Q J X Z 1
        """.split('\n'):
    if i:
        for j in i[:-1].split():
            consonants += [j for x in xrange(int(i[-1]))]

for i in \
        """
        E 6
        I A 9
        O 8
        U 4
        """.split('\n'):
    if i:
        for j in i[:-1].split():
            vowels += [j for x in xrange(int(i[-1]))]

from IRC_LN_commands import *
from LN_process_commands import *
import time
import random   #Doesn't need seeding as this is done automatically
                #upon import
import re

players = []

game_state = {
    "game":{
        "letters":False,
        "numbers":False
        },
    "on_call":{
        "numbers":False,
        "letters":False
        },
    "numbers":{
        "gen_problem":False,
        "give_problem":False,
        "waiting":False,
        "nums_please":False,
        "results_please":False,
        "round":0
        },
    "letters":{
        "round":0,
        "gen_problem":False,
        "letters_please":False,
        "results_please":False,
        "letters":0,
        "max_letters":9,
        "waiting":False
        }
}

server = 'irc.freenode.net'
port = 6667
nick = 'LN_bot'
name = "Letters and Numbers bot"
channel = '##letters_and_numbers'
buf = 4096
call_time = int(time.time())
controllers = ['Sugarloaf0', 'patrick333']
timeouts = {
        "call":14,
        "game":60
        }
give_soln = True

# Connect to the server and join the channel
IRCsock = connect(server, port, nick, name)
join(IRCsock, channel)

# Read data from the stream, process and respond
# appropriately
while 1:
    msg, data = msgRecv(IRCsock, buf, data)
    if len(msg): print msg

    # MESSAGE PROCESSING
    # ----------------------------------------
    # 1. PRIMITIVE
    # -----------
    # All messages must be checked to see if
    # they are end or PING commands. If so
    # they will be responded to appropriately.
    # This will be referred to as 'primitive'
    # processing

    response = primProcess(IRCsock, msg)
    if response[0] == 1:
        # If PING received
        msgSend(IRCsock, response[1])
    elif response[0] == 2:
        # if define received
        #IRCmsg(IRCsock, defineWord(msgGet(response[1])), channel)
        pass

    # 2. NUMBERS
    # ----------------------------------------
    # (i) The call
    # We need to check if a numbers game has
    # been called, if so, set the state to
    # respect that fact and then search for
    # players. At the moment, only the
    # controller can call.
    # 30 seconds after the call the only thing
    # we want to do is check for playing
    # and do primitive processing.

    if getName(msg) in controllers:
        response = callCheck(msg)
        if response["numbers"] == True and game_state["on_call"]\
                ["numbers"] == False and game_state["game"]\
                ["numbers"] == False:
            IRCmsg(IRCsock, "A numbers game has been called,"\
                           +" anyone who wishes to play "\
                           +"should type 'playing'. "\
                           +" The game will start in about "\
                           +str(timeouts["call"])+" seconds."\
                           , channel)
            game_state["on_call"]["numbers"] = True
            game_state["game"]["numbers"] = True
            IRCsock.settimeout(5.0)
            players = []
            call_time = int(time.time())

    # (ii) Playing
    # If a numbers game has been called we
    # are looking for players that are
    # 'playing', these will be added to a list
    # (iii) Call over
    # If all players have signed up or
    # a timeout has been reached the call is
    # over and the game should start

    if game_state["on_call"]["numbers"] == True:
        if callOver(call_time, timeouts["call"]):
            game_state["on_call"]["numbers"] = False
            game_state["numbers"]["round"] += 1 # Round 1
            IRCsock.settimeout(None)
            if len(players) <= 1:
                IRCmsg(IRCsock, "Not enough players, game will not start",\
                        channel)
                game_state["numbers"]["round"] -= 1
                
                players = []
            else:
                IRCmsg(IRCsock, "Players: " + ', '.join([x for x in players]), channel)
                game_state["numbers"]["gen_problem"] = True
        response = checkPlaying(msg)
        if response["playing"] == True and response["player"] not in players:
           players.append(response["player"])

    # (iv) Round X
    # NOW WE PLAY!!!! :D
    # Only does one round for now

    if game_state["game"]["numbers"] == True:
        if game_state["numbers"]["gen_problem"]:
            
            # Pick a player to choose the numbers
            random.shuffle(players)
            chooser = players[0]
            IRCmsg(IRCsock, chooser + " has been chosen to pick the numbers.", channel)
            IRCmsg(IRCsock, "Please give them in the format 'Large:Small' with your"\
                           +" next message. Total of 6 numbers required. Maximum of 4 of each kind.", channel)
            game_state["numbers"]["nums_please"] = True
            game_state["numbers"]["gen_problem"] = False
        elif game_state["numbers"]["nums_please"]:
            if numsGiven(msg, chooser):
                # If an appropriate split has been given
                # generate some numbers and a target
                numbars = msgGet(msg).split(":")
                num_large = int(numbars[0])
                num_small = int(numbars[1])
                IRCmsg(IRCsock, "Numbers are good, starting now.", channel)
                game_state["numbers"]["nums_please"] = False
                
                target, numbers, solution = makeProblem(num_large, num_small, larges, smalls)
                IRCmsg(IRCsock, "Your numbers are: " + ', '.join([str(x) for x in numbers])\
                        , channel)
                IRCmsg(IRCsock, "Your target is: " + str(target), channel)

                game_state["numbers"]["give_problem"] = False
                game_state["numbers"]["waiting"] = True        
                game_time = int(time.time())
                IRCsock.settimeout(5.0)

                # Initialise variables to track user answers
                answers = {}
                for i in players:
                    answers[i] = []

        elif game_state["numbers"]["waiting"]:
            if gameTimeOut(game_time, timeouts["game"]):
                IRCmsg(IRCsock, "Numbers game has timed out, no longer accepting answers."\
                        , channel)
                IRCsock.settimeout(None)
                if give_soln:
                    IRCmsg(IRCsock, "One solution was: " + solution, channel)
                game_state["numbers"]["results_please"] = True
                game_state["numbers"]["waiting"] = False

            elif getName(msg) in players and msg.split(":")[1].find("PRIVMSG LN_bot") != -1:
                print "Private message received from " + getName(msg)
                # Either looking for maths or a 'clear'/'scrap' message
                if isMaths(msgGet(msg)):
                    answers[getName(msg)].append(msgGet(msg)) ################### TEMPORARY ##############
                elif isClear(msgGet(msg)):
                    answers[getName(msg)] = []
                elif isScrap(msgGet(msg)):
                    if answers[getName(msg)] >= 1:
                        answers[getName(msg)].pop(-1)
        if game_state["numbers"]["results_please"]:
            game_state["game"]["numbers"] = False
            game_state["numbers"]["results_please"] = False
            # Check answers from people
            correct = []
            for i in answers:
                if len(answers[i]):
                    if isCorrect(target, numbers, answers[i]):
                        correct.append(i)

            if len(correct) == 0:
                IRCmsg(IRCsock, "What a shame, there were no correct solutions "\
                        +"submitted.", channel)
            elif len(correct) == 1:
                IRCmsg(IRCsock, "Congratulations to " + correct[0] + " for sub"\
                        +"mitting a correct solution.", channel)
            elif len(correct) > 1:
                IRCmsg(IRCsock, "Congratulations to " + ', '.join([x for \
                        x in correct]) + '. They submitted correct '\
                        +'solutions.', channel)
            # Game is over
            players = []

    # 3. LETTERS 
    # ----------------------------------------
    # (i) The call
    # We need to check if a letters game has
    # been called, if so, set the state to
    # respect that fact and then search for
    # players. At the moment, only the
    # controller can call.
    # 30 seconds after the call the only thing
    # we want to do is check for playing
    # and do primitive processing.

    if getName(msg) in controllers:
        response = callCheck(msg)
        if response["letters"] == True and game_state["on_call"]\
                ["letters"] == False and game_state["game"]\
                ["letters"] == False:
            IRCmsg(IRCsock, "A letters game has been called,"\
                           +" anyone who wishes to play "\
                           +"should type 'playing'. "\
                           +" The game will start in about "\
                           +str(timeouts["call"])+" seconds."\
                           , channel)
            game_state["on_call"]["letters"] = True
            game_state["game"]["letters"] = True
            game_state["letters"]["letters"] = 0
            IRCsock.settimeout(5.0)
            players = []
            call_time = int(time.time())

    # (ii) Playing
    # If a letters game has been called we
    # are looking for players that are
    # 'playing', these will be added to a list
    # (iii) Call over
    # If all players have signed up or
    # a timeout has been reached the call is
    # over and the game should start

    if game_state["on_call"]["letters"] == True:
        if callOver(call_time, timeouts["call"]):
            game_state["on_call"]["letters"] = False
            game_state["letters"]["round"] += 1 # Round 1
            IRCsock.settimeout(None)
            if len(players) <= 1:
                IRCmsg(IRCsock, "Not enough players, game will not start",\
                        channel)
                game_state["letters"]["round"] -= 1
                game_state["game"]["letters"] = False
                players = []
            else:
                IRCmsg(IRCsock, "Players: " + ', '.join([x for x in players]), channel)
                game_state["letters"]["gen_problem"] = True
        response = checkPlaying(msg)
        if response["playing"] == True and response["player"] not in players:
           players.append(response["player"])

    # (iv) Round X
    # Time to play 

    if game_state["game"]["letters"] == True:
        if game_state["letters"]["gen_problem"]:
            
            # Pick a player to choose the numbers
            random.shuffle(players)
            chooser = players[0]
            IRCmsg(IRCsock, chooser + " has been chosen to pick the letters.", channel)
            IRCmsg(IRCsock, "Please give vowel/cons(onant) one by one as appropriate.", channel)
            game_state["letters"]["letters_please"] = True
            game_state["letters"]["gen_problem"] = False
            letters = []

        elif game_state["letters"]["letters_please"]:
            if letterGiven(msg, chooser) == 'v':
                letters.append(getVowel(vowels))
                game_state["letters"]["letters"] += 1
                IRCmsg(IRCsock, "Letters: " + ' '.join([x for x in letters]), channel)
            elif letterGiven(msg, chooser) == 'c':
                letters.append(getConsonant(consonants))
                game_state["letters"]["letters"] += 1
                IRCmsg(IRCsock, "Letters: " + ' '.join([x for x in letters]), channel)
            if game_state["letters"]["letters"] >= game_state["letters"]["max_letters"]:
                # If letters have been given
                game_state["letters"]["letters_please"] = False            
                game_state["letters"]["waiting"] = True

                IRCmsg(IRCsock, "Game starts now, you have " + str(timeouts["game"]) + " seconds."\
                        , channel)

                game_time = int(time.time())
                IRCsock.settimeout(5.0)

                # Initialise variables to track user answers
                answers = {}
                for i in players:
                    answers[i] = []

        elif game_state["letters"]["waiting"]:
            if gameTimeOut(game_time, timeouts["game"]):
                IRCmsg(IRCsock, "Letters game has timed out, no longer accepting answers."\
                        , channel)
                IRCsock.settimeout(None)

                game_state["letters"]["results_please"] = True
                game_state["letters"]["waiting"] = False
            elif getName(msg) in players and msg.split(":")[1].find("PRIVMSG LN_bot") != -1:
                print "Private message received from " + getName(msg)
                # Looking for a letters message
                if isLetters(msgGet(msg.upper()), letters[:]) and isWord(msgGet(msg.lower())):                    
                    answers[getName(msg)].append(msgGet(msg))

        if game_state["letters"]["results_please"]:
            game_state["game"]["letters"] = False
            game_state["letters"]["results_please"] = False

            # Check answers from people
            # Accepted answers are already correct
            # Just print whoever had the longest
            
            # PRINT THE WINNER
            longest_w = 0

            # Find the length of the longest word
            for player in answers:
                for word in answers[player]:
                    if len(word) > longest_w:
                        longest_w = len(word)

            # Then find players with one of those words

            winners = {}
            for player in answers:
                for word in answers[player]:
                    if len(word) == longest_w:
                        winners[player] = word
            
            if len(winners) == 0:
                IRCmsg(IRCsock, "What a shame, nobody won.", channel)
            elif len(winners) == 1:
                IRCmsg(IRCsock, winners.keys()[0] + " had the longest word with: "\
                        +winners[winners.keys()[0]] + ".", channel)
            elif len(winners) >= 2:
                winrars = winners.keys()
                IRCmsg(IRCsock, "The winners were: " + ', '.join(winrars[:-1])\
                        +' and '+winrars[-1]+". With the words: "\
                        + ', '.join([winners[x] for x in winrars[:-1]])\
                        +" and " + winners[winrars[-1]]+".", channel)
                        

            # Game is over
            players = []
