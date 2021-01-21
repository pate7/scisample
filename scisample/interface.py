"""
Interface definition for ``Sampler`` objects.
"""

import abc


class SamplerInterface(abc.ABC):
    """
    Abstract interface for sampler objects.
    """

    @property
    @abc.abstractmethod
    def data(self):
        """
        Sampler data from the configuration file.
        """

    @abc.abstractmethod
    def check_validity(self):
        """
        Check validity of the sampler. This will raise a
        `SamplingError` if the sampler is not valid, but return
        otherwise.
        """

    @abc.abstractmethod
    def get_samples(self):
        """
        Get samples from the sampler.

        This should return samples as a list of dictionaries, with the
        sample variables as the keys:

        .. code:: python

            [{'b': 0.89856, 'a': 1}, {'b': 0.923223, 'a': 1}, ... ]
        """

    @property
    @abc.abstractmethod
    def parameters(self):
        """
        Return a of list of the parameters being generated by the
        sampler.
        """

    @property
    @abc.abstractmethod
    def parameter_block(self):
        """
        Converts samples to parameter dictionary in a format convenient for ``maestrowf``
        """ # noqa
