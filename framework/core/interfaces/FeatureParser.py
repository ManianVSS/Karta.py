import abc


class FeatureParser(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def parse_feature(self, feature_source: str):
        raise NotImplementedError
