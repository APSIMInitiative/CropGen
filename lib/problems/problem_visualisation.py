from pymoo.optimize import minimize
import logging

from lib.server.final_result import FinalResult
from lib.problems.problem_factory import ProblemFactory
from lib.utils.algorithm_generator import AlgorithmGenerator
from lib.utils.constants import Constants

#
# Represents a Problem Visualisation
#
class ProblemVisualisation():

    #
    # Construct problem with the given dimensions and variable ranges
    #
    def __init__(self, config, crop_gen_job, cgm_relay_address, results_manager):
        self.config = config
        self.crop_gen_job = crop_gen_job
        self.cgm_relay_address = cgm_relay_address
        self.results_manager = results_manager

    #
    # Invokes the running of the problem.
    #
    def run(self):
        self.current_iteration_id = 1
        algorithm = AlgorithmGenerator.create_nsga2_algorithm(self.crop_gen_job.individuals)
        problem = ProblemFactory.create(self.config, self.crop_gen_job, self.cgm_relay_address, self.results_manager)

        # Run the optimisation algorithm on the defined problem. Note: framework only performs minimisation,
        # so problems must be framed such that each objective is minimised
        minimize_result = minimize(
            problem=problem,
            algorithm=algorithm,
            termination=(
                Constants.MINIMIZE_CONSTRAINT_NUMBER_OF_GENERATIONS,
                self.crop_gen_job.iterations
            ),
            save_history=True,
            verbose=False
        )

        # Now that everything has been evaluated, check for any run errors and only
        # continue if there aren't any.
        if problem.run_errors:
            logging.error(f'Problem did not run successfully - Errors: {problem.run_errors}')
            return
        
        # Variable values for non-dominated individuals in the last generation
        variable_values_non_dominated_individuals = minimize_result.X
        # Objective values for non-dominated individuals in the last generation
        objective_values_non_dominated_individuals = minimize_result.F

        final_results = FinalResult(
            self.crop_gen_job, 
            variable_values_non_dominated_individuals,
            objective_values_non_dominated_individuals,
            problem.is_multi_year,
            problem.processed_aggregated_outputs
        )

        # Store the final results.
        self.results_manager.add_final_result(final_results)
