""" A module to implement the Bacterial Memory model for a primitive machine learning algorithm. """
#import argparse
import logging
#import threading
#import sys

logging.basicConfig(level=logging.INFO)

class BactMem():
    """ The Bacterial Memory Model implementation """
    memory_file_name = 'memory_string.txt'
    decision_file_name = 'decisions.txt'


    def __init__(self):
        self.memory = "" #the memory string
        self.decisions = {} # decision memory
        # load memory from file
        memory_file = open(BactMem.memory_file_name, 'r')
        for line in memory_file:
            self.memory += line.strip('\n')
        memory_file.close()
        # load decisions from file
        decision_file = open(BactMem.decision_file_name, 'r')
        for line in decision_file:
            vals = line.split()
            self.decisions[int(vals[0])] = [int(vals[1]), int(vals[2])]
        decision_file.close()


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


class Decision():
    """ A class to provide an organization for the decisions as a data structure. """

    def __init__(self, index, length, decision):
        self.end_position = index
        self.substr_len = length
        self.decision = decision
