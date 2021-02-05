"""
Module defining the random sampler object.
"""

import logging
import random
import os
import sys
from contextlib import suppress

from scisample.base_sampler import BaseSampler
from scisample.utils import log_and_raise_exception

# @TODO: can this duplicate code be removed?
UQPIPELINE_SAMPLE = False
UQPIPELINE_SAMPLE_PATH = '/collab/usr/gapps/uq/UQPipeline/smplg_cmpnt'
if os.path.exists(UQPIPELINE_SAMPLE_PATH):
    sys.path.append('/collab/usr/gapps/uq/UQPipeline/smplg_cmpnt')
    with suppress(ModuleNotFoundError):
        import sampling.sampler as sampler
        UQPIPELINE_SAMPLE = True

LOG = logging.getLogger(__name__)

class UQPipelineSampler(BaseSampler):
    """
    Class which wraps UQPipeline sampling methods.

    .. code:: yaml

        sampler:
            type: uqpipeline
            uq_type: <UQPipeline Sampler keyword> 
                     cartesian_cross centered corners default_value geolhs 
                     list montecarlo moat multi_normal pdf quasi_rn rawsamplepoints 
                     samplepoints stdlhs uniform
                     <Also accepts class names>
            num_samples: 5      # uq_type accepts either
            num_points: 5       # uq_type accepts either
            <uqpipeline parameters>
            constants:
                X1: 20
            parameters:         # uq_type box and range are entered here
                X2:             # some uq_types accept range or list
                    min: 5
                    max: 10
                X3: [5, 10]     # some uq_types accept range or list

    A total of ``num_samples`` will be generated. Entries in the ``constants``
    dictionary will be added to all samples. Entries in the ``parameters``
    block will be selected from a range of ``min`` to ``max``.  The result of
    the above block would something like:

    .. code:: python

        [{X1: 20, X2: 5.632222227306036, X3: 6.633392173916806},
         {X1: 20, X2: 7.44369755967992, X3: 8.941266067294213}]
    """

    def __init__(self, data):
        """
        Initialize the sampler.

        :param data: Dictionary of sampler data.
        """
        super().__init__(data)
        self.check_validity()

    def check_validity(self):
        super().check_validity()
        self._check_variables()

        # @TODO: test that file exists and it contains the right parameters
        if 'previous_samples' in self.data.keys():
            log_and_raise_exception(
                "'previous_samples' is not yet supported.\n"
                "  Please contact Chris Krenn or Brian Daub for assistance.")

        # @TODO: add error check to schema
        for key, value in self.data["parameters"].items():
            try:
                float(value['min'])
            except ValueError:
                log_and_raise_exception(
                    f"Parameter ({key}) must have a numeric minimum.\n"
                    f"  Current minimum value is: {value}.")
            try:
                float(value['max'])
            except ValueError:
                log_and_raise_exception(
                    f"Parameter ({key}) must have a numeric maximum.\n"
                    f"  Current maximum value is: {value}.")

    @property
    def parameters(self):
        """
        Return a of list of the parameters being generated by the
        sampler.
        """
        return self._parameters_constants_parameters_only()

    def get_samples(self):
        """
        Get samples from the sampler.

        This returns samples as a list of dictionaries, with the
        sample variables as the keys:

        .. code:: python

            [{'b': 0.89856, 'a': 1}, {'b': 0.923223, 'a': 1}, ... ]
        """
        # yaml_text = """
        #     type: random
        #     num_samples: 5
        #     #previous_samples: samples.csv # optional
        #     constants:
        #         X1: 20
        #     parameters:
        #         X2:
        #             min: 5
        #             max: 10
        #         X3:
        #             min: 5
        #             max: 10
        #     """
        # LatinHyperCubeSampler = sampler.LatinHyperCubeSampler
        # points = LatinHyperCubeSampler.sample_points(num_points=10, box=[[0, 1], [0, 1]])
        # print(f"points: {points}")

        if self._samples is not None:
            return self._samples

        self._samples = []

        random_list = []
        min_dict = {}
        range_dict = {}
        box = []

        for key, value in self.data["parameters"].items():
            min_dict[key] = value["min"]
            range_dict[key] = value["max"] - value["min"]
            box.append([value["min"], value["max"]])

        for i in range(self.data["num_samples"]):
            random_dictionary = {}
            for key, value in self.data["parameters"].items():
                random_dictionary[key] = (
                    min_dict[key] + random.random() * range_dict[key])
            random_list.append(random_dictionary)
        print(f"CRK: random_list {random_list}")

        
        LatinHyperCubeSampler = sampler.LatinHyperCubeSampler
        points = LatinHyperCubeSampler.sample_points(
            num_points=self.data["num_samples"], 
            box=box)
        print(f"CRK: points {points}")

        random_list = []
        for i in range(self.data["num_samples"]):
            random_dictionary = {}
            j = 0
            for key, value in self.data["parameters"].items():
                random_dictionary[key] = points[i][j]
                j += 1
            random_list.append(random_dictionary)
        print(f"CRK: random_list_2 {random_list}")

        for i in range(len(random_list)):
            new_sample = {}

            with suppress(KeyError):
                new_sample.update(self.data['constants'])

            with suppress(KeyError):
                for key, value in random_list[i].items():
                    new_sample[key] = value

            self._samples.append(new_sample)

        return self._samples

name = "latin_hypercube"
my_sampler = sampler.LatinHyperCubeSampler
points = my_sampler.sample_points(num_points=10, box=[[0, 1], [0, 1]])
print(f"\n{my_sampler.name} points:\n{points}")
print(f"\n{my_sampler.name} dir:\n{dir(my_sampler)}")
points = my_sampler.sample_points(num_points=200, box=[[-1,1],[0,2]], geo_degree=1.3, seed=42)
print(f"\n{my_sampler.name} points:\n{points}")

name = "cartesian_cross"
my_sampler = sampler.CartesianCrossSampler
points = my_sampler.sample_points(box=[[0,1],[0,1]], num_divisions=3)
print(f"\n{my_sampler.name} points:\n{points}")
# returns 9 points, with 3 divisions in each dimension
points = my_sampler.sample_points(box=[[0,1],[0,1]], num_divisions=[3,4])
print(f"\n{my_sampler.name} points:\n{points}")
# returns 12 points, with 3 divisions in the first dimension, and 4 divisions in the second
points = my_sampler.sample_points(box=[[0,1],[0,1]], num_divisions=[[.5,.75],[.3,.32]])
print(f"\n{my_sampler.name} points:\n{points}")
points = my_sampler.sample_points(
    num_divisions=[3,3], 
    box=[[-1,1],[]], 
    values=[[],['foo', 'bar', 'zzyzx']])
print(f"\n{my_sampler.name} points:\n{points}")

name = "monte_carlo"
my_sampler = sampler.MonteCarloSampler
points = my_sampler.sample_points(num_points=6, box=[[-1,1],[0,2]], seed=42)
print(f"\n{my_sampler.name} points:\n{points}")


name= "uniform"
my_sampler = sampler.UniformSampler
points = my_sampler.sample_points(num_points=5, box=[[-1,1],[0,2]])
print(f"\n{my_sampler.name} points:\n{points}")

name = "quasi_random"
my_sampler = sampler.QuasiRandomNumberSampler()
points = my_sampler.sample_points(num_points=6, box=[[-1,1],[0,2]], technique='sobol')
print(f"\n{my_sampler.name} points (sobol):\n{points}")

my_sampler = sampler.QuasiRandomNumberSampler()
points = my_sampler.sample_points(num_points=6, box=[[-1,1],[0,2]], technique='halton')
print(f"\n{my_sampler.name} points (halton):\n{points}")

name = "corners"
my_sampler = sampler.CornerSampler()
points = my_sampler.sample_points(num_points=4, box=[[-1,1],[0,2]])
print(f"\n{my_sampler.name} points (halton):\n{points}")

name = "centered"
my_sampler = sampler.CenteredSampler()
points = my_sampler.sample_points(
    num_divisions=3, box=[[-1,1],[0,2]], dim_indices=[0,1], default=[0.5,0.5])
print(f"\n{my_sampler.name} points:\n{points}")

points = my_sampler.sample_points(
    num_divisions=3, box=[[-1,1],[0,2]], dim_indices=[0,1], technique='lhs_vals', num_points=3, seed=42)
print(f"\n{my_sampler.name} points (latin hyper cube):\n{points}")

name = "one_at_a_time"
my_sampler = sampler.OneAtATimeSampler()
points = my_sampler.sample_points(
    box=[[-1,1],[0,2]], default=[.5,.5], do_oat=True, use_high=True, use_low=True, use_default=True)
print(f"\n{my_sampler.name} points:\n{points}")
print("MOAT name not set correctly")
points = my_sampler.sample_points(
    box=[[-1,1],[0,2]], default=[.5,.5], do_oat=True, use_high=False, use_low=False, use_default=True)
print(f"\n{my_sampler.name} points (no high or low):\n{points}")
print("MOAT name not set correctly")

name = "faces"
my_sampler = sampler.FaceSampler()
points = my_sampler.sample_points(num_divisions=3, box=[[-1,1],[0,2]])
print(f"\n{my_sampler.name} points:\n{points}")
