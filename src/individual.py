import random
import sys
import yaml

from logger import get_logger
from misc import lambda_eval, run_function

class Individual(object):
    '''
        Individual which represents a possible set of weights.
    '''
    def __init__(self, num_of_genes, weights=None, obj_function=None):
        '''
            Individual constructor. 
        '''
        self.logger = get_logger(self.__class__.__name__)

        self.num_of_genes = num_of_genes

        if not weights:
            self.chromosome = [random.random() for i in range(self.num_of_genes)]
        else:
            self.chromosome = weights

        self.fitness = 0
        if obj_function == None:
            self.logger.error('missing objective function')
            sys.exit()
        obj_function = lambda_eval(obj_function)
        self.obj_function = eval(obj_function)
            
        self.logger.info('created individual instance')
        self.logger.debug(str(self))

    def __str__(self):
        return f'Individual: num_of_genes:{self.num_of_genes} fitness:{self.fitness} chromosome:[' + ', '.join([f'{gene:.3}' for gene in self.chromosome]) + f']'


    # Implementation of Python's rich comparison methods #####
    def __lt__(self, other):
        return self.fitness < other.fitness

    def __le__(self, other):
        return self.fitness <= other.fitness

    def __eq__(self, other):
        return self.fitness == other.fitness

    def __ne__(self, other):
        return self.fitness != other.fitness

    def __gt__(self, other):
        return self.fitness > other.fitness

    def __ge__(self, other):
        return self.fitness >= other.fitness

    def get_obj_function_args(self):
        '''
            This method should be modified according to the user needs.
        '''
        return self.chromosome

    def compute_fitness(self):
        '''
            Compute the fitness based on the objective function read in
            the input file.
        '''
        self.logger.info('computing the fitness')
        args = self.get_obj_function_args()
        self.fitness = self.obj_function(*args)
                
        self.logger.debug(f'fitness {self.fitness}')

    def evaluate(self):
        self.compute_fitness()
