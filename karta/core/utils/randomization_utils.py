from random import Random


def generate_next_composition_from_probability_map(probability_map: dict, random: Random) -> list[object]:
    chosen_objects = []

    if not probability_map or (len(probability_map) == 0):
        return chosen_objects

    for obj, probability in probability_map.items():
        if not isinstance(probability, float) or not (0.0 < probability <= 1.0):
            raise SyntaxError("probability needs to be an floating point value between 0-1")

        random_chance = random.uniform(0.0, 1.0)

        if (probability == 1) or (random_chance <= probability):
            chosen_objects.append(obj)

    return chosen_objects


def generate_next_mutex_composition_from_probability_map(probability_map: dict, random: Random) -> object:
    if not probability_map or (len(probability_map) == 0):
        return None

    probabilty_covered = 0.0
    random_chance = random.uniform(0.0, 1.0)

    return_value = None
    for obj, probability in probability_map.items():
        if not (0.0 < probability <= 1.0):
            raise SyntaxError("probability needs to be an floating point value between 0-1")
        if not return_value and (probabilty_covered <= random_chance <= probabilty_covered + probability):
            return_value = obj
        probabilty_covered += probability

    if round(probabilty_covered, 2) != 1.0:
        raise SyntaxError("probability total for mutex combination need to be 1.0f")

    return return_value


def generate_next_composition_from_objects(objects_with_probability: list[object], random: Random) -> list[object]:
    chosen_objects = []

    if not objects_with_probability or (len(objects_with_probability) == 0):
        return chosen_objects

    for obj in objects_with_probability:
        probability = obj.probability if hasattr(obj, 'probability') else 1.0
        if not isinstance(probability, float) or not (0.0 < probability <= 1.0):
            raise SyntaxError("probability needs to be an floating point value between 0-1")

        random_chance = random.uniform(0.0, 1.0)

        if (probability == 1) or (random_chance <= probability):
            chosen_objects.append(obj)

    return chosen_objects


def generate_next_mutex_composition_from_objects(objects_with_probability: list[object], random: Random) -> object:
    if not objects_with_probability or (len(objects_with_probability) == 0):
        return None

    probabilty_covered = 0.0
    random_chance = random.uniform(0.0, 1.0)

    return_value = None
    for obj in objects_with_probability:
        probability = obj.probability if hasattr(obj, 'probability') else 1.0
        if not (0.0 < probability <= 1.0):
            raise SyntaxError("probability needs to be an floating point value between 0-1")
        if not return_value and (probabilty_covered <= random_chance <= probabilty_covered + probability):
            return_value = obj
        probabilty_covered += probability

    if round(probabilty_covered, 2) != 1.0:
        raise SyntaxError("probability total for mutex combination need to be 1.0f")

    return return_value
