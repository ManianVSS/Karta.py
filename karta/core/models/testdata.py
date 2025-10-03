from random import Random
from typing import Optional

from pydantic import BaseModel

from karta.core.utils import randomization_utils


class DataValue(BaseModel):
    """
    DataValue is a base class that represents a randomly generated random value or object.
    It can be used to generate random values based on the provided parameters.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __hash__(self):
        return id(self)

    def generate_next_value(self, random: Random) -> Optional[object]:
        """
        Generates the next random value based on the provided parameters.
        This method should be overridden by subclasses to provide specific randomization logic.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class IntegerRangeValue(DataValue):
    """
    RangeValue is a subclass of DataValue that represents a range of values.
    It can be used to generate random values within the specified range.
    """
    min: Optional[int] = None
    max: Optional[int] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_next_value(self, random: Random) -> int:
        if self.min is None or self.max is None:
            raise ValueError("Minimum and maximum values must be provided.")
        if self.min > self.max:
            raise ValueError("Minimum value cannot be greater than maximum value.")
        return random.randint(self.min, self.max)


class FloatRangeValue(DataValue):
    """
    RangeValue is a subclass of DataValue that represents a range of values.
    It can be used to generate random values within the specified range.
    """
    min: Optional[float] = None
    max: Optional[float] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_next_value(self, random: Random) -> float:
        if self.min is None or self.max is None:
            raise ValueError("Minimum and maximum values must be provided.")
        if self.min > self.max:
            raise ValueError("Minimum value cannot be greater than maximum value.")
        return random.uniform(self.min, self.max)


class RandomStringValue(DataValue):
    """
    RandomStringValue is a subclass of DataValue that represents a random string value.
    It can be used to generate random strings based on the provided parameters.
    """
    length: Optional[int] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_next_value(self, random: Random) -> str:
        """ Generates a random string of the specified length. """
        if self.length <= 0:
            raise ValueError("Length must be a positive integer.")
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=self.length))


class OneSelectedFromListValue(DataValue):
    """
    OneSelectedFromListValue is a subclass of DataValue that represents a random value selected from an array.
    It can be used to generate random values based on the provided array.
    """
    values: Optional[list] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_next_value(self, random: Random) -> object:
        if not self.values:
            raise ValueError("The values list is empty.")
        generated_object = random.choice(self.values)
        if isinstance(generated_object, DataValue):
            generated_object = generated_object.generate_next_value(random)
        return generated_object


class SomeSelectedFromListValue(DataValue):
    """
    SomeSelectedFromListValue is a subclass of DataValue that represents some random value selected from an array.
    It can be used to generate random values based on the provided array.
    """
    values: Optional[list] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_next_value(self, random: Random) -> list:
        if not self.values:
            raise ValueError("The values list is empty.")
        generated_objects = random.sample(self.values, k=random.randint(1, len(self.values)))
        processed_objects = []
        for generated_object in generated_objects:
            if isinstance(generated_object, DataValue):
                processed_objects.append(generated_object.generate_next_value(random))
            else:
                processed_objects.append(generated_object)
        return processed_objects


class ListDataValue(DataValue):
    """
    ListDataValue is a subclass of DataValue that represents a list of random values.
    It can be used to generate random lists based on the provided parameters.
    """
    values: Optional[list] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_next_value(self, random: Random) -> list:
        if not self.values:
            raise ValueError("The values list is empty.")
        generated_objects = []
        for value in self.values:
            if isinstance(value, DataValue):
                generated_objects.append(value.generate_next_value(random))
            else:
                generated_objects.append(value)
        return generated_objects


class ProbabilityMapOneValue(DataValue):
    """
    ProbabilityMapOneValue is a subclass of DataValue that represents a random value selected from a probability map.
    It can be used to generate random values based on the provided probability map.
    """
    probability_map: Optional[dict[object, float]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_next_value(self, random: Random) -> object:
        if not self.probability_map:
            raise ValueError("The values list is empty.")
        generated_object = randomization_utils.generate_next_mutex_composition_from_probability_map(
            self.probability_map, random)
        if isinstance(generated_object, DataValue):
            generated_object = generated_object.generate_next_value(random)
        return generated_object


class ProbabilityMapSomeValue(DataValue):
    """
    ProbabilityMapSomeValue is a subclass of DataValue that represents some random value selected from a probability map.
    It can be used to generate random values based on the provided probability map.
    """
    probability_map: Optional[dict[object, float]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_next_value(self, random: Random) -> list:
        if not self.probability_map:
            raise ValueError("The values list is empty.")
        generated_objects = randomization_utils.generate_next_composition_from_probability_map(
            self.probability_map, random)
        processed_objects = []
        for generated_object in generated_objects:
            if isinstance(generated_object, DataValue):
                processed_objects.append(generated_object.generate_next_value(random))
            else:
                processed_objects.append(generated_object)
        return processed_objects


class GeneratedObjectValue(DataValue):
    """
    GeneratedObjectValue is a subclass of DataValue that represents a random generated object value.
    It can be used to generate random objects based on the provided parameters.
    """
    fields_dict: Optional[dict[str, object]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_next_value(self, random: Random) -> object:
        if not self.fields_dict:
            return None
        data = {}
        for field_name, field_value in self.fields_dict.items():
            if isinstance(field_value, DataValue):
                data[field_name] = field_value.generate_next_value(random)
            else:
                data[field_name] = field_value
        return data
