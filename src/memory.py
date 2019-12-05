""" A module to implement the Bacterial Memory model for a primitive machine learning algorithm. """
import logging
import random

#Comment out this line to turn off logging
logging.basicConfig(level=logging.INFO)

class BactMem():
    """ The Bacterial Memory Model implementation """
    memory_file_name = 'memory_string.txt'
    decision_file_name = 'decisions.txt'


    def __init__(self, mem_entry_len, update_mode):
        self.memory = "" #the memory string
        self.decisions = {} # decision memory
        self.mem_entry_len = mem_entry_len
        self.update_mode = update_mode
        # load memory from file
        try:
            with open(BactMem.memory_file_name, 'r') as mf:
                for line in mf:
                    self.memory += line.strip('\n')
        except IOError:
            logging.error("The memory file does not exist.")
        # load decisions from file
        try:
            with open(BactMem.decision_file_name, 'r') as df:
                for line in df:
                    vals = line.split()
                    self.decisions[int(vals[0])] = [int(vals[1]), int(vals[2])]
        except IOError:
            logging.error("The decision file does not exist.")


    def add_decision(self, decision):
        """ A method to add a Decision object to the object's decision dictionary. """
        if not decision.end_position in self.decisions:
            self.decisions[decision.end_position] = decision
        else:
            logging.info("Attempting to add duplicate decision")


    def update_memory(self, new_memory):
        """ Updates the internal memory representation with the newly produced data.
                new_memory: a string containing the memory. The format is determined
                (and enforced) by the client """
        self.memory += new_memory
        decision = -1
        if self.update_mode == "classify-on-update":
            decision = self.make_decision()
        return decision

    def find_substr(self, search_string, offset):
        """ Find the last (rightmost) occurrence of the given string in self.memory. """
        offset *= self.mem_entry_len
        return self.memory.rfind(search_string[offset:], 0, len(self.memory)-offset)

    def find_memory(self, search_string):
        """ Finds the largest suffix of search_string that occurred previously in the memory.
        It will return the last occurrence. """
        offset = 1
        index = self.find_substr(search_string, offset)
        while index == -1:
            offset += 1
            index = self.find_substr(search_string, offset)
        return index

    def make_decision(self):
        """ A system to decide whether the current memory-state is 'bad'.
        Finds the most recent relevant memory and investigates the decision made
        at that time. If no memory was made, it makes a random choice and enters
        that as the decision. """
        recent_memory = self.find_memory(self.memory)
        if recent_memory == -1:
            decision = Decision(len(self.memory) - 1, len(self.memory), random.randint(0, 1))
        else:
            prev_decision = self.decisions[recent_memory]
            decision = Decision(len(self.memory) - 1, prev_decision.length, prev_decision.decision)
        return decision

class Decision():
    """ A class to provide an organization for the decisions as a data structure. """

    def __init__(self, index, length, decision):
        self._end_position = index
        self._substr_len = length
        self._decision = decision

    @property
    def end_position(self):
        """ Get the end position in memory where this decision occurred. """
        return self._end_position

    @property
    def substr_len(self):
        """ Get the length of the substring associated with this decision. """
        return self._substr_len

    @property
    def decision(self):
        """ Get the decision for this memory. """
        return self._decision

    def update(self, updated_decision):
        """ Updates the decision to the provided integer value. """
        self._decision = updated_decision
