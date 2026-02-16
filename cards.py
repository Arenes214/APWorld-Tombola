from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .world import APTombolaWorld

from collections import defaultdict


def generate_cards(world: APTombolaWorld):
    # Create and shuffle numbers
    sheet_columns = {
        0: list(range(1,10)),
        1: list(range(10,20)),
        2: list(range(20,30)),
        3: list(range(30, 40)),
        4: list(range(40, 50)),
        5: list(range(50, 60)),
        6: list(range(60, 70)),
        7: list(range(70, 80)),
        8: list(range(80, 91)), # Last columns includes 90
    }

    for i in sheet_columns:
        world.random.shuffle(sheet_columns[i])

    # Get the numbers for each card
    all_card_numbers = []

    # For each card get the first 9 numbers from each column to follow the "at least one per column" rule
    for card in range(6):
        card_numbers = []

        for col in range(9):
            n = sheet_columns[col].pop()
            card_numbers.append((col, n))
            # Column count is not needed here since it will be 1 for each column
        all_card_numbers.append(card_numbers)

    # Now we can take the remaining numbers to have 15 per Card

    force_first = 1

    for card_numbers in all_card_numbers:
        col_count = defaultdict(lambda:1) # Create the column count at 1 since there is guaranteed exact 1 per column

        # Avoid infinite loop by taking a number from the last column at start
        if force_first:
            n = sheet_columns[8].pop()
            card_numbers.append((col, n))
            col_count[8] += 1
            force_first = 0

        while (len(card_numbers) < 15):
            # Only take from columns that have 3 or more numbers, unless all of them don't have 3
            # This avoids an infinite loop
            takeable_col = []
            for col in range(9):
                if len(sheet_columns[col]) >= 3:
                    takeable_col.append(col)

            # At this point if takeable_col is empty, all columns are 2 or lower
            if not takeable_col:
                for i in range(9):
                    takeable_col.append(i)


            # Avoid recalculation the above, only retry this part
            while (True):
                col = world.random.choice(takeable_col)

                if col_count[col] >=3: # Don't take if we already have 3 in column
                    continue
                if not sheet_columns[col]: # And seriously don't try to take from an empty column
                    continue

                n = sheet_columns[col].pop()
                card_numbers.append((col, n))
                col_count[col] += 1
                break

    # Now that i have all of the cards' numbers, create the cards
    cards = []

    # And populate them
    for card_numbers in all_card_numbers:
        card = [[0] * 9 for _ in range (3)]
        row_count = [0,0,0] # Create the row count for the "5 per row" rule

        for (col, n) in card_numbers:
            # Place all of them dumbly first
            for row in range(3):
                if not card[row][col]:
                    card[row][col] = n
                    row_count[row] += 1
                    break

        # Then move them randomly in the columns until all of the rows are 5
        while (max(row_count) > 5):
            row_high = row_count.index(max(row_count))
            row_low = row_count.index(min(row_count))

            # Calculate the possible columns to make it easier
            # This should always give at least a column
            movable_col = [
                col for col in range(9)
                if card[row_high][col] != 0 and card[row_low][col] == 0
            ]

            col = world.random.choice(movable_col)

            card[row_low][col] = card[row_high][col]
            card[row_high][col] = 0

            row_count[row_high] -= 1
            row_count[row_low] += 1

        # After poplulating them, order the columns
        for col in range (9):
            col_sorted = [card[row][col] for row in range(3) if card[row][col] != 0]
            col_sorted.sort()

            i = 0 # index of col_sorted basically
            for row in range(3):
                if card[row][col] != 0:
                    card[row][col] = col_sorted[i]
                    i += 1
        # After doing everything add the card to cards
        cards.append(card)

    print(f"DEBUG: APTombola Cards: {cards}") # TODO TEST REMOVE DEBUG PRINT
    return cards
