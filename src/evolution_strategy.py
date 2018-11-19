import random
import sys
import yaml

from individual import Individual
from logger import get_logger

class EvolutionStrategy:
    '''
        Class containing attributes and methods regarding the ES(mu + lambda)
    '''

    def __init__(self, es_yaml='in/es.yaml', ind_yaml='in/individual.yaml'):
        '''
            EvolutionStrategy constructor.
        '''
        self.logger = get_logger(self.__class__.__name__)
        random.seed(0)

        # Using Python context manager
        with open(es_yaml, 'r') as es_cfg, open(ind_yaml, 'r') as ind_cfg:
            self.es_cfg = yaml.load(es_cfg)
            self.ind_cfg = yaml.load(ind_cfg)

        self.mu = self.es_cfg['mu']
        self.lambda_ = self.es_cfg['lambda']
        self.sigma = self.es_cfg['sigma']
        self.tau = self.es_cfg['tau']
        self.max_generation = self.es_cfg['max_generation']
        self.k = self.es_cfg['change_mutation']
        
        selection_op = self.es_cfg['selection_operator']
        if selection_op == 'plus':
            self.selection_operator = self.plus_selection_operator
        elif selection_op == 'comma':
            self.selection_operator = self.comma_selection_operator
        else:
            self.logger.error('invalid selection operator')
            sys.exit()

    def create_initial_population(self):
        '''
            Create the first population of μ individuals according to their configuration.
        '''
        self.logger.info('creating initial population')

        self.population = []
        for i in range(0, self.mu):
            self.population.append(Individual(self.ind_cfg['num_of_genes'], 
                                              None if 'pre_weights' not in self.ind_cfg else self.ind_cfg['pre_weights'],
                                              self.ind_cfg['obj_function']))

        self.logger.info('finished creating initial population')

    def create_new_population(self, parent):
        '''
            Create a new population of children that are at least as good
            as the chosen parent.
        '''

        self.logger.info('creating new population')

        new_population = [self.population[i] for i in range(0, self.mu)]

        for i in range(0, self.lambda_):
            new_individual = self.mutate(parent, self.sigma)
            new_population.append(new_individual)

        self.logger.info('finished created new population')

        return new_population

    def plus_selection_operator(self, population):
        '''
            Apply the + selection operator on the population: choose 
            the best μ individuals from a total of μ + λ individuals, 
            which means that both parents and children are competing 
            to be in the population.
        '''
        self.logger.info('applying plus selection operator')

        self.population = []
        for i in range(0, self.mu):
            fittest = max(population)
            self.population.append(fittest)
            population.remove(fittest)

        self.logger.debug(f'current population after + op:')
        self.logger.info('finished applying plus selection operator')

    def comma_selection_operator(self, population):
        '''
            Apply the , selection operator on the population: choose
            the best μ individuals from a total of λ individuals,
            which means that only the children are competing to be in
            the population.
        '''
        self.logger.info('applying comma selection operator')

       
        # Parent removal
        for i in range(0, self.mu):
            population.pop(i)

        self.population = []
        for i in range(0, self.mu):
            fittest = max(population)
            self.population.append(fittest)
            population.remove(fittest)

        self.logger.debug(f'current population after + op:')
        self.logger.info('finished applying comma selection operator')
  
 
    def evaluate_population(self, population):
        '''
        Evaluate the entire given population.
        '''
        self.logger.info('evaluating population')
        for i, individual in enumerate(population):
            self.logger.info(f'evaluating individual #{i}')
            individual.evaluate()

    def get_parent_for_mutation(self):
        '''
            Selects one individual to apply mutation from the 
            population of μ individuals.   
        '''
        self.logger.info('getting parent for mutation')
        return random.choice(self.population)

    def mutate(self, parent, sigma):
        '''
            Perform a Gaussian mutation on the chosen parent.
        '''
        self.logger.info('mutating individual')
        self.logger.debug(f'sigma: {sigma}')
        mutated = Individual(self.ind_cfg['num_of_genes'], 
                             list(map(lambda x,y=sigma: x + random.gauss(0, sigma), parent.chromosome)),
                             self.ind_cfg['obj_function'])
        return mutated

    def success_probability_counter(self, population):
        '''
            Count the number of successful individuals.
        '''
        children = [population[i] for i in range(0 + self.mu, self.mu + self.lambda_)]
        parents = [population[i] for i in range(0, self.mu)]

        num = sum(any(child > parent for parent in parents) for child in children)
        self.successful_individuals += num
        self.total_individuals += len(children)

    def get_best_individual(self):
        '''
            Return the best individual of the current generation.
        '''
        return max(self.population)

    def run_ES(self):
        '''
            Run the (μ + λ)-ES using Rechenberg's 1/5th Success Rule
        '''
        self.logger.info('started running (μ + λ)-ES')

        self.create_initial_population();
        self.evaluate_population(self.population)

        current_gen = 0
        self.successful_individuals = 0
        self.total_individuals = 0
        while current_gen < self.max_generation:
            self.logger.debug('current_gen:{}'.format(current_gen))
            
            # Change mutation every k generations according to Rechenberg's 1/5th rule
            if current_gen % self.k == 0 and current_gen != 0:
                success_probability = self.successful_individuals / self.total_individuals
                if success_probability > 0.2:
                    self.sigma /= self.tau
                elif success_probability < 0.2:
                    self.sigma *= self.tau
                elif success_probability == 0.2:
                    self.sigma = self.sigma

            parent = self.get_parent_for_mutation()
            new_population = self.create_new_population(parent)
            self.success_probability_counter(new_population)
            self.evaluate_population(new_population)
            self.selection_operator(new_population)

            self.logger.debug(f'best individual in generation {current_gen}: {self.get_best_individual()}')
            
            current_gen += 1

        self.logger.info('finished running (μ + λ)-ES')


if __name__ == '__main__':
    es = EvolutionStrategy()
    es.run_ES()
