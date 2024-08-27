from lib.problems.problem import Problem
from lib.problems.environment_typing_problem import EnvironmentTypingProblem

#
# Factory class for creating CGM Clients, depending on the config.
#
class ProblemFactory():

    #
    # Creates an instance of a Problem.
    #
    @staticmethod
    def create(env_provider, config, crop_gen_job, cgm_relay_address, results_manager, memory_usage_tracker):
        if crop_gen_job.get_is_environment_typing_run():
            return EnvironmentTypingProblem(env_provider, config, crop_gen_job, cgm_relay_address, results_manager, memory_usage_tracker)
        else:
            return Problem(env_provider, config, crop_gen_job, cgm_relay_address, results_manager, memory_usage_tracker)
