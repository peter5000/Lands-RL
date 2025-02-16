from itertools import combinations_with_replacement

combinations = list(combinations_with_replacement(range(5), 3)) + list(combinations_with_replacement(range(5), 2)) + list(combinations_with_replacement(range(5), 1))
combination_to_idx = {}
idx_to_combination = {}

for i, combination in enumerate(combinations):
    combination_to_idx[combination] = i
    idx_to_combination[i] = combination

print(combination_to_idx)
print(idx_to_combination)