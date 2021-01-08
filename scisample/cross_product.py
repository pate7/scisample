"""
Module defining the cross product sampler object.
"""

import itertools
import logging

from contextlib import suppress

from scisample.base_sampler import (BaseSampler)

LOG = logging.getLogger(__name__)


class CrossProductSampler(BaseSampler):
    """
    Class defining cross-product sampling.

    Its sampler data takes two blocks, ``constants`` and ``parameters``:

    .. code:: yaml

        sampler:
            type: cross_product
            constants:
                X1: 20
            parameters:
                X2: [5, 10]
                X3: [5, 10]

    Entries in the ``constants`` dictionary will be added to all samples.
    Entries in the ``parameters`` block will have the cross product taken.
    The above entry sould result in the samples:

    .. code:: python

        [
            {X1: 20, X2: 5, X3: 5},
            {X1: 20, X2: 5, X3: 10},
            {X1: 20, X2: 10, X3: 5},
            {X1: 20, X2: 10, X3: 10}
        ]
    """

    def __init__(self, data):
        """
        Initialize the sampler.

        :param data: Dictionary of sampler data.
        """
        super().__init__(data)
        self.check_validity()

    def check_validity(self):
        self._check_variables_existence()
        self._check_variables_for_dups()

    @property
    def parameters(self):
        """
        Return a of list of the parameters being generated by the
        sampler.
        """
        parameters = []
        with suppress(KeyError):
            parameters.extend(list(self.data['constants'].keys()))
        with suppress(KeyError):
            parameters.extend(list(self.data['parameters'].keys()))

        return parameters

    def get_samples(self):
        """
        Get samples from the sampler.

        This returns samples as a list of dictionaries, with the
        sample variables as the keys:

        .. code:: python

            [{'b': 0.89856, 'a': 1}, {'b': 0.923223, 'a': 1}, ... ]
        """

        if self._samples is not None:
            return self._samples

        product_list = []

        with suppress(KeyError):
            product_list.extend(
                [[value] for key, value in self.data['constants'].items()]
            )

        with suppress(KeyError):
            product_list.extend(
                [value for key, value in self.data['parameters'].items()]
            )

        sample_list = itertools.product(*product_list)

        self._samples = []

        for sample in sample_list:
            new_sample = {}
            for i, key in enumerate(self.parameters):
                new_sample[key] = sample[i]
            self._samples.append(new_sample)

        return self._samples
