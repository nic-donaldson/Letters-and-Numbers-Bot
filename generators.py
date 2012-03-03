import random

class Generator:
    def __init__ (self):
        pass

    def happens(self, chance):
        return random.random() <= chance

class NumbersGenerator(Generator):
    def __init__ (self):
        self.solution = ""
        self.target = 0
        self.operators = ['+', '-', '/', '*']
        self.large_picks = []
        self.small_picks = []

    def generate(self, (large, small), larges, smalls):
        self.pick_numbers((large, small), larges, smalls)
        
    
    def pick_numbers(self, (large, small), larges, smalls):
        random.shuffle(larges)
        random.shuffle(smalls)

        larges = larges[:large]
        small_prob = [1.0 for x in xrange(len(smalls))]
        
        self.large_picks = larges
        self.small_picks = []
        for i in xrange(small):
            picked = False
            while not picked:
                pick = random.randint(0, len(smalls)-1)
                if self.happens(small_prob[pick]):
                    picked = True
                    self.small_picks.append(smalls[pick])
                    small_prob[pick] /= 4.0


