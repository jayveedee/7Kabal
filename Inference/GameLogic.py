def variable_check(card_number, unknowns):
    card_number_string = str(card_number)
    if card_number < 10:
        card_number_string = "0" + card_number_string
    if unknowns == -1:
        scan = "NO"
    else:
        scan = "YES"
    return card_number_string, scan


def check_how_many_cards_to_move(move_from_list, moved_card, tableau_pile_moved_from, tableau_pile_moved_to):
    for i in range(len(tableau_pile_moved_from) - 1, -1, -1):
        if tableau_pile_moved_from[i] == moved_card:
            move_from_list = True
        if move_from_list:
            tableau_pile_moved_to.append(tableau_pile_moved_from[i])
            tableau_pile_moved_from.pop(i)


class GameLogic:

    def __init__(self, logic_waste_card, logic_tableau_card_piles, logic_foundation_card_piles):
        self.logicWasteCardPile = []
        self.logicTableauCardPiles = {}
        self.logicFoundationCardPiles = {}
        self.unknownWaste = 0
        self.loseCounter = 0
        self.unknownTableau = []
        self.allUnknownWasteFound = False
        self.unknownWasteCounter = 25
        self.reset = True
        self.result = []
        self.update_logic_scan(logic_waste_card, logic_tableau_card_piles, logic_foundation_card_piles)

    def update_logic_scan(self, logic_waste_card=None, logic_tableau_card_piles=None, logic_foundation_card_piles=None):
        if (self.logicTableauCardPiles is None and self.logicFoundationCardPiles is None and self.logicWasteCardPile is None) or (self.reset is True):
            if logic_waste_card is not None:
                self.logicWasteCardPile = logic_waste_card
            if logic_tableau_card_piles is not None:
                self.logicTableauCardPiles = logic_tableau_card_piles
            else: self.logicTableauCardPiles = {0:[],1:[],2:[],3:[],4:[],5:[],6:[]}
            if logic_foundation_card_piles is not None:
                self.logicFoundationCardPiles = logic_foundation_card_piles
            else: self.logicFoundationCardPiles = {0:[],1:[],2:[],3:[]}
            self.unknownWaste = 24
            self.unknownTableau.clear()
            for i in range(7):
                counter = 0
                for j in range(i):
                    counter += 1
                self.unknownTableau.append(counter)
            self.reset = False

        else:
            if logic_waste_card is not None:
                if logic_waste_card not in self.logicWasteCardPile:
                    self.unknownWaste -= 1
                    if self.unknownWaste == 0:
                        self.allUnknownWasteFound = True
                    self.logicWasteCardPile.append(logic_waste_card)

            if logic_tableau_card_piles is not None:
                self.check_list_consistency(logic_tableau_card_piles, self.logicTableauCardPiles)

            if logic_foundation_card_piles is not None:
                self.check_list_consistency(logic_foundation_card_piles, self.logicFoundationCardPiles)

        return self.logicWasteCardPile, self.logicTableauCardPiles, self.logicFoundationCardPiles

    def update_logic_move(self, move):

        self.result = []

        if move[0] != "NA" and move[0] != "WIN":

            move_from_list = False

            moved_card = move[0] + " " + move[1]
            card_pile_moved_from = int(move[2])
            card_pile_moved_to = int(move[3])
            card_placement = move[4]
            move_type = move[5]
            scan = move[6]

            if scan == "YES" and move_type == "T":
                self.unknownTableau[card_pile_moved_from] -= 1

            if card_placement == "T":
                return self.handle_update_tableau_and_moved_pile(card_pile_moved_from, card_pile_moved_to, move_from_list, moved_card)
            if card_placement == "F":
                return self.handle_update_foundation_and_moved_pile(card_pile_moved_from, card_pile_moved_to, moved_card)

        self.handle_update_reversed_waste_pile()

        return ["NA", "NA", "NA", "NA", "NA"]

    def calculate_move(self):
        if self.check_win_condition():
            return self.result
        elif self.check_lose_condition():
            return self.result

        for i in range(len(self.logicTableauCardPiles)):
            current_pile = self.logicTableauCardPiles.get(i)

            if len(current_pile) > 0:

                card_number, card_type, _ = self.define_card(i, 0, "T")

                for j in range(len(self.logicTableauCardPiles)):
                    neighbor_pile = self.logicTableauCardPiles.get(j)

                    unknowns = self.check_unknown_cards(i)

                    empty_space = self.check_empty_spaces(card_number, card_type, current_pile, i, j, neighbor_pile, unknowns)
                    if empty_space is "King":
                        return self.result
                    elif empty_space is False:
                        if current_pile[0] != neighbor_pile[0]:

                            next_card_number, next_card_type, _ = self.define_card(j, 0, "T")

                            if current_pile[0] is not None:
                                for k in range(len(current_pile) - 1, 0, -1):

                                    sub_card_number, sub_card_type, _ = self.define_card(i, k, "T")

                                    if self.check_sub_pile_placement(current_pile, i, j, k, next_card_number, next_card_type, sub_card_number, sub_card_type):
                                        return self.result

                            if self.check_tableau_placement(card_number, card_type, current_pile, i, j, next_card_number, next_card_type):
                                return self.result

        return self.check_waste_card_placement()

    def check_tableau_placement(self, card_number, card_type, current_pile, i, j, next_card_number, next_card_type):
        unknowns = self.check_unknown_cards(i)
        if len(current_pile) > 1:
            unknowns = -1
        if len(current_pile) > 1:
            above_card_number, _, _ = self.define_card(i, 1, "T")
            if above_card_number != next_card_number:
                if self.check_card_placement(i, card_number, card_type, j, next_card_number, next_card_type, False, unknowns, "T"):
                    return True
        else:
            if self.check_card_placement(i, card_number, card_type, j, next_card_number, next_card_type, False, unknowns, "T"):
                return True
        return False

    def check_sub_pile_placement(self, current_pile, i, j, k, next_number, next_type, sub_number, sub_type):
        if k == len(current_pile) - 1:
            unknowns = self.check_unknown_cards(i)
        else:
            unknowns = -1

        if len(current_pile) > 1 and k != len(current_pile) - 1:
            above_card_number, _, _ = self.define_card(i, k + 1, "T")
            if above_card_number != next_number:
                if self.check_card_placement(i, sub_number, sub_type, j, next_number, next_type, True, unknowns, "T"):
                    return True
        else:
            if sub_number != 13:
                if self.check_card_placement(i, sub_number, sub_type, j, next_number, next_type, True, unknowns, "T"):
                    return True
        return False

    def check_empty_spaces(self, card_number, card_type, current_pile, i, j, neighbor_pile, unknowns):
        if len(neighbor_pile) == 0:
            if self.unknownTableau[j] == 0:
                if self.check_card_placement(i, card_number, card_type, j, -1, "-1", False, unknowns, "T"):
                    return "King"
                last_index = len(current_pile) - 1
                if current_pile[last_index] == "13 d" or current_pile[last_index] == "13 c" or \
                        current_pile[last_index] == "13 s" or current_pile[last_index] == "13 h":
                    king_card_number, king_card_type, _ = self.define_card(i, last_index, "T")
                    if self.check_card_placement(i, king_card_number, king_card_type, j, -1, "-1", True, unknowns, "T"):
                        return "King"
            return True
        else:
            return False

    def check_list_consistency(self, new_scanned_pile, old_scanned_pile):
        for i in range(0, len(new_scanned_pile)):
            current_new_scanned_pile = new_scanned_pile.get(i)
            current_old_scanned_pile = old_scanned_pile.get(i)
            if len(current_new_scanned_pile) != len(current_old_scanned_pile):
                if len(current_new_scanned_pile) != 0:
                    if len(current_old_scanned_pile) == 0:
                        old_scanned_pile[i] = current_new_scanned_pile
                    else:
                        if current_new_scanned_pile[0] not in current_old_scanned_pile:
                            current_old_scanned_pile.append(current_new_scanned_pile[0])
                            if old_scanned_pile == self.logicTableauCardPiles:
                                current_old_scanned_pile.sort(reverse=False)
                            else:
                                current_old_scanned_pile.sort(reverse=True)
            elif len(current_new_scanned_pile) != 0 and len(current_old_scanned_pile) != 0:
                if current_new_scanned_pile[0] != current_old_scanned_pile[0]:
                    if current_new_scanned_pile[0] not in current_old_scanned_pile:
                        current_old_scanned_pile.append(current_new_scanned_pile[0])
                        if old_scanned_pile == self.logicTableauCardPiles:
                            current_old_scanned_pile.sort(reverse=False)
                        else:
                            current_old_scanned_pile.sort(reverse=True)
        return old_scanned_pile

    def handle_update_reversed_waste_pile(self):
        if self.allUnknownWasteFound:
            if len(self.logicWasteCardPile) - 1 == self.unknownWasteCounter:
                self.unknownWasteCounter = 0
            else:
                self.unknownWasteCounter += 1

    def handle_update_tableau_and_moved_pile(self, card_pile_moved_from, card_pile_moved_to, move_from_list, moved_card):
        tableau_pile_moved_to = self.logicTableauCardPiles.get(card_pile_moved_to)
        if card_pile_moved_from != -1:
            tableau_pile_moved_from = self.logicTableauCardPiles.get(card_pile_moved_from)
            check_how_many_cards_to_move(move_from_list, moved_card, tableau_pile_moved_from, tableau_pile_moved_to)
        else:
            waste_card = self.check_how_many_waste_found()
            tableau_pile_moved_to.append(waste_card)
            self.logicWasteCardPile.remove(waste_card)
        tableau_pile_moved_to.sort(reverse=False)
        return tableau_pile_moved_to

    def handle_update_foundation_and_moved_pile(self, card_pile_moved_from, card_pile_moved_to, moved_card):
        foundation_pile_moved_to = self.logicFoundationCardPiles.get(card_pile_moved_to)
        if card_pile_moved_from != -1:
            tableau_pile_moved_from = self.logicTableauCardPiles.get(card_pile_moved_from)
            if tableau_pile_moved_from[0] == moved_card:
                foundation_pile_moved_to.append(tableau_pile_moved_from[0])
                tableau_pile_moved_from.pop(0)
        else:
            waste_card = self.check_how_many_waste_found()
            foundation_pile_moved_to.append(waste_card)
            self.logicWasteCardPile.remove(waste_card)
        foundation_pile_moved_to.sort(reverse=True)
        return foundation_pile_moved_to

    def check_how_many_waste_found(self):
        if self.allUnknownWasteFound:
            _, _, waste_card = self.define_card(self.unknownWasteCounter, 0, "W")
            if self.unknownWasteCounter == 0:
                self.unknownWasteCounter = -1
            elif 0 < self.unknownWasteCounter < len(self.logicWasteCardPile) - 1:
                self.unknownWasteCounter -= 1
        else:
            _, _, waste_card = self.define_card(len(self.logicWasteCardPile) - 1, 0, "W")
        return waste_card

    def check_unknown_cards(self, i):
        if i != -1:
            unknowns = self.unknownTableau[i]
            if unknowns == 0:
                unknowns = -1
        else:
            unknowns = self.unknownWaste
            if unknowns == 0:
                unknowns = -1
        return unknowns

    def check_waste_card_placement(self):
        if self.logicWasteCardPile is not None:
            if len(self.logicWasteCardPile) != 0:
                if self.unknownWasteCounter != -1:

                    waste_card_number, waste_card_type = self.check_if_all_waste_cards_found()
                    unknowns = self.check_unknown_cards(-1)

                    for i in range(len(self.logicTableauCardPiles)):

                        if len(self.logicTableauCardPiles.get(i)) > 0:

                            next_card_number, next_card_type, _ = self.define_card(i, 0, "T")

                            if self.check_card_placement(-1, waste_card_number, waste_card_type, i, next_card_number, next_card_type, False, unknowns, "W"):
                                return self.result

                        elif len(self.logicTableauCardPiles.get(i)) == 0 and waste_card_number == 13:
                            if self.check_card_placement(-1, waste_card_number, waste_card_type, i, -1, "-1", False, unknowns, "W"):
                                return self.result
        if self.unknownWaste != 0:
            return ["NA", "NA", "NA", "NA", "NA", "W", "YES"]
        else:
            self.loseCounter += 1
            return ["NA", "NA", "NA", "NA", "NA", "W", "NO"]

    def check_if_all_waste_cards_found(self):
        if self.allUnknownWasteFound:
            if self.unknownWasteCounter > len(self.logicWasteCardPile) - 1:
                self.unknownWasteCounter = len(self.logicWasteCardPile) - 1
            waste_card_number, waste_card_type, _ = self.define_card(self.unknownWasteCounter, 0, "W")
        else:
            waste_card_number, waste_card_type, _ = self.define_card(len(self.logicWasteCardPile) - 1, 0, "W")
        return waste_card_number, waste_card_type

    def check_card_placement(self, i, card_number, card_type, j, neighbor_card_number, neighbor_card_type, is_sub_card, unknowns=0, move_type=""):
        card_number_string, scan = variable_check(card_number, unknowns)

        if card_number <= 13:

            exists_in_foundation = self.check_foundation_card_pile(card_number, card_type)

            if not is_sub_card:
                if exists_in_foundation > -1:
                    self.create_move(card_number_string, card_type, i, exists_in_foundation, "F", move_type, scan)
                    return True

            if neighbor_card_type == "-1" and neighbor_card_number == -1 and card_number == 13 and (
                    unknowns > 0 or move_type == "W"):
                self.create_move(card_number_string, card_type, i, j, "T", move_type, scan)
                return True

            if neighbor_card_number > 0:

                if ((card_type == "d" or card_type == "h") and (neighbor_card_type == "c" or neighbor_card_type == "s")) or \
                        ((card_type == "c" or card_type == "s") and (neighbor_card_type == "d" or neighbor_card_type == "h")):

                    if neighbor_card_number - 1 == card_number:
                        self.create_move(card_number_string, card_type, i, j, "T", move_type, scan)
                        return True

        return False

    def define_card(self, i, k, pile_type):
        if pile_type == "T" or pile_type == "F":
            if pile_type == "T":
                card_pile = self.logicTableauCardPiles.get(i)[k]
            else:
                card_pile = self.logicFoundationCardPiles.get(i)[k]
        else:
            card_pile = self.logicWasteCardPile[i]
        current_card = card_pile.split()
        current_card_number = int(current_card[0])
        current_card_type = current_card[1]
        return current_card_number, current_card_type, card_pile

    def create_move(self, card_number_string, card_type, i, j, move_from, move_type, scan):
        self.loseCounter = 0

        self.result.append(card_number_string)
        self.result.append(card_type)
        self.result.append(str(i))
        self.result.append(str(j))
        self.result.append(move_from)
        self.result.append(move_type)
        self.result.append(scan)

    def check_foundation_card_pile(self, card_number, card_type):
        for i in range(4):
            if len(self.logicFoundationCardPiles.get(i)) != 0:

                foundation_card_number, foundation_card_type, _ = self.define_card(i, 0, "F")

                if foundation_card_type == card_type and foundation_card_number + 1 == card_number:
                    return i

            else:
                if card_number == 1:
                    return i
        return -1

    def check_win_condition(self):
        foundation_one = len(self.logicFoundationCardPiles.get(0))
        foundation_two = len(self.logicFoundationCardPiles.get(1))
        foundation_three = len(self.logicFoundationCardPiles.get(2))
        foundation_four = len(self.logicFoundationCardPiles.get(3))

        if foundation_one + foundation_two + foundation_three + foundation_four == 52:
            for i in range(7):
                self.result.append("WIN")
            return True
        return False

    def check_lose_condition(self):
        if self.loseCounter > len(self.logicWasteCardPile) and self.unknownWaste == 0:
            for i in range(7):
                self.result.append("LOSE")
            return True
        return False

    def reset_logic(self, logic_waste_card, logic_tableau_card_piles, logic_foundation_card_piles):
        self.reset = True
        return self.update_logic_scan(logic_waste_card, logic_tableau_card_piles, logic_foundation_card_piles)

    def get_piles(self):
        return self.logicTableauCardPiles, self.logicFoundationCardPiles, self.logicWasteCardPile

