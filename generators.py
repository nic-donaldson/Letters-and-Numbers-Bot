import random

class Generator:
    def __init__ (self):
        pass

    #Returns a true/false value based on the probability given
    def happens(self, chance):
        return random.random() <= chance

    def reset(self):
        self.__init__()

class NumbersGenerator(Generator):
    #Default values
    def __init__ (self):
        self.target = 0
        self.large = 2
        self.small = 4
        self.larges = [100, 75, 50, 25]
        self.smalls = [1,2,3,4,5,6,7,8,9,10]
        self.large_picks = []
        self.small_picks = []

    #Generates numbers and a target
    def generate(self):
        self.pick_numbers()
        self.target = random.randint(100, 999)

    def large_small(self, large, small):
        self.large = large
        self.small = small
        
    #Shuffles the large numbers and picks the first x,
    #no duplicates
    #Picks from the smalls given, duplicates are allowed
    #but are based on a probability system.
    #Each number starts off with 1.0 probability so they can
    #be picked with no problem.
    #After being picked, the probability gets quartered so
    #being successfully picked twice is unlikely.
    def pick_numbers(self):
        larges = self.larges
        smalls = self.smalls
        random.shuffle(larges)
        random.shuffle(smalls)

        larges = larges[:self.large]
        small_prob = [1.0 for x in xrange(len(smalls))]
        
        self.large_picks = larges
        self.small_picks = []
        for i in xrange(self.small):
            picked = False
            while not picked:
                pick = random.randint(0, len(smalls)-1)
                if self.happens(small_prob[pick]):
                    picked = True
                    self.small_picks.append(smalls[pick])
                    small_prob[pick] /= 4.0
