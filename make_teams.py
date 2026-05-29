import pandas as pd
import random
from collections import defaultdict


TEAM_COLORS = [
    "ROSSO", "VERDE", "BLU", "GIALLO", "ARANCIONE", "VIOLA",
    "ROSA", "AZZURRO", "MARRONE", "GRIGIO", "BIANCO", "NERO",
    "TURCHESE", "INDACO", "MAGENTA", "CORALLO", "SMERALDO", "AMBRA",
]

def make_teams(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)

    # Determine team sizes: as many teams of 4 as possible,
    # with up to 3 teams of 3 for the remainder.
    remainder = n % 4
    if remainder == 0:
        sizes = [4] * (n // 4)
    elif remainder == 1:
        # e.g. 9 people → 2×3 + 1×3? No: 9 = 2×3 + 1×3. Actually 9 = 3×3.
        # General rule: subtract enough teams-of-4 to make remainder divisible by 3,
        # then replace those with teams-of-3.
        # remainder 1 → need 3 threes instead of removing 1 four (1 four = 4, 3 threes = 9, diff = 5 → doesn't work cleanly)
        # Correct approach: find k (0≤k≤3) such that (n - 3k) % 4 == 0
        k = next(k for k in range(4) if (n - 3 * k) % 4 == 0)
        fours = (n - 3 * k) // 4
        sizes = [4] * fours + [3] * k
    elif remainder == 2:
        k = next(k for k in range(4) if (n - 3 * k) % 4 == 0)
        fours = (n - 3 * k) // 4
        sizes = [4] * fours + [3] * k
    else:  # remainder == 3
        fours = (n - 3) // 4
        sizes = [4] * fours + [3]

    assert sum(sizes) == n, f"Size mismatch: {sum(sizes)} != {n}"
    assert all(3 <= s <= 4 for s in sizes), "Invalid team size"
    assert sizes.count(3) <= 3, "Too many teams of 3"

    num_teams = len(sizes)
    assert num_teams <= len(TEAM_COLORS), "Not enough color names"

    colors = TEAM_COLORS[:num_teams]
    random.shuffle(colors)

    # Group indices by tipologia
    tipo_to_indices = defaultdict(list)
    for i, tipo in enumerate(df["Tipologia biglietto"]):
        tipo_to_indices[tipo].append(i)

    # Shuffle each group
    for lst in tipo_to_indices.values():
        random.shuffle(lst)

    # Build teams greedily:
    # For each slot in each team, pick from the most-represented unused tipologia
    # that isn't already in the team.
    teams = [[] for _ in range(num_teams)]  # list of (original_index,) per team
    team_tipos = [set() for _ in range(num_teams)]  # tipologie already in team i
    remaining = {t: list(idxs) for t, idxs in tipo_to_indices.items()}

    def available_tipos_for(team_idx):
        return [t for t, lst in remaining.items() if lst and t not in team_tipos[team_idx]]

    # Iterate filling team slots
    for t_idx, size in enumerate(sizes):
        for _ in range(size):
            avail = available_tipos_for(t_idx)
            if not avail:
                # Fallback: pick from any remaining tipologia (diversity constraint relaxed)
                avail = [t for t, lst in remaining.items() if lst]
            if not avail:
                raise RuntimeError("Ran out of participants unexpectedly")
            # Pick the tipologia with the most remaining members (greedy balance)
            chosen_tipo = max(avail, key=lambda t: len(remaining[t]))
            person_idx = remaining[chosen_tipo].pop()
            if not remaining[chosen_tipo]:
                del remaining[chosen_tipo]
            teams[t_idx].append(person_idx)
            team_tipos[t_idx].add(chosen_tipo)

    # Write results back to dataframe
    assignment = [""] * n
    for t_idx, members in enumerate(teams):
        for person_idx in members:
            assignment[person_idx] = colors[t_idx]

    df["squadra"] = assignment
    return df, teams, colors, sizes

