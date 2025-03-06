from random import Random

from framework.core.utils.randomization_utils import generate_next_composition, generate_next_mutex_composition

rng = Random()
# for i in range(100):
#     print(rng.uniform(0.0, 1.0))

# for i in range(100):
#     print(str(rng.randint(0, 1000000) / 1000000.0))

sample_size = 1000000

probability_map = {
    "value1": 0.5,
    "value2": 0.5,
    "value3": 0.5,
    "value4": 0.5,
}

generated_count_map = {
    "value1": 0,
    "value2": 0,
    "value3": 0,
    "value4": 0,
}

for i in range(sample_size):
    gen_values = generate_next_composition(probability_map, rng)
    for value in gen_values:
        generated_count_map[value] += 1
    for value in generated_count_map.keys():
        generated_count_map[value] = generated_count_map[value]

normal_composition_deviation_map = {value: int(abs(round(probability_map[value] - (count / sample_size), 2) * 100)) for
                                    (value, count) in
                                    generated_count_map.items()}

probability_map = {
    "value1": 0.1,
    "value2": 0.2,
    "value3": 0.3,
    "value4": 0.4,
}

generated_count_map = {
    "value1": 0,
    "value2": 0,
    "value3": 0,
    "value4": 0,
}

for i in range(sample_size):
    value = generate_next_mutex_composition(probability_map, rng)
    # print(value)
    generated_count_map[value] += 1
    for value in generated_count_map.keys():
        generated_count_map[value] = generated_count_map[value]

print("deviation for generate next composition with  % is ", str(normal_composition_deviation_map))
print("deviation for generate next mutex composition with  % is ",
      str({value: int(abs(round(probability_map[value] - (count / sample_size), 2) * 100)) for (value, count) in
           generated_count_map.items()}))
