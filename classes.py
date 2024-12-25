import math
import pandas as pd
from itertools import product
from shared_functions import get_int_input
from sympy import symbols, solve_univariate_inequality, And
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap

class Game:
    def __init__(self):
        self.number_of_players = int(input("Please enter number of players: "))
        self.players_strategy_sets = {}
        self.number_of_tables = 1
        self.game_tables = {}
        self.list_of_players = [f"Player {i}" for i in range(1,self.number_of_players+1)]
        self.tables_names = []
        self.mode = "Terminal"
        self.strategy_profiles = []
        self.profiles_utilities = {}
        self.players = {}

        if self.mode == "Terminal":
            self.enter_player_strategies_terminal()

            if self.number_of_players == 2:
                self.show_table_input_gui()
            else:
                self.create_game_tables()
                self.enter_tables_data_terminal()

        self.create_players()
        self.calculate_strategy_profile()
        self.calculate_utility_for_strategy_profile()

    def enter_player_strategies_terminal(self):
        for count in range(self.number_of_players):
            i = count + 1
            strategies = input(f"\nPlease enter strategies for player {i} separated by commas(ex: A,B): ")
            strategies = strategies.strip()
            strategies = strategies.split(",")
            self.players_strategy_sets[f"Player {i}"] = strategies
        print(f"Successfully Created {self.players_strategy_sets}")

    def show_table_input_gui(self):
        app = QApplication([])
        gui = TableInputGUI(self.players_strategy_sets["Player 1"], self.players_strategy_sets["Player 2"], self)
        gui.show()
        app.exec_()

    def update_number_of_tables(self):
        if self.number_of_players > 2:
            stragies_sets = list(self.players_strategy_sets.values())
            stragies_sets.pop(0) # Remove Player 1
            stragies_sets.pop(0) # Remove Player 2
            sets_lengths = [len(strategy_set) for strategy_set in stragies_sets]
            self.number_of_tables = math.prod(sets_lengths)


    def create_game_tables(self):
        self.update_number_of_tables()

        self.game_tables = {}
        for i in range(1,self.number_of_tables+1): # Putting Tables Names in the dict
            self.game_tables[f"Table {i}"] = ""

        self.tables_names = list(self.game_tables.keys()) # [Table 1, Table 2, ...]

        for table in self.game_tables: # Construct empty table for P1 and P2
            row_names = self.players_strategy_sets["Player 1"]
            column_names = self.players_strategy_sets["Player 2"]

            df = pd.DataFrame(
                [[() for _ in column_names] for _ in row_names],
                columns=column_names,
                index=row_names
            )
            gameTable = GameTable(table,df)
            
            self.game_tables[table] = gameTable

        if self.number_of_players > 2: # Put corresponding strategy for each player
            players_to_be_set = self.list_of_players.copy()
            players_to_be_set.remove("Player 1")
            players_to_be_set.remove("Player 2")

            players_to_be_set_strategies = {} # Player 3: [E,F] , Player 4: [G,H] , ...

            for player in players_to_be_set:
                player_strategy = self.players_strategy_sets[player]
                players_to_be_set_strategies[player] = player_strategy
            
            strategies_sequences = [list(pair) for pair in product(*players_to_be_set_strategies.values())]
            # Strategies Sequences: [['E', 'G'], ['E', 'H'], ['F', 'G'], ['F', 'H']]

            for i,table in enumerate(self.tables_names): # Looping over tables names
                tableGame = self.game_tables[table] # get that table game
                current_sequence = strategies_sequences[i] # We are in table i so bring sequence i
                player_count = 3 # start from player 3
                for strategy in current_sequence: # for each strategy in the current sequence
                    tableGame.static_players_strategies[f"Player {player_count}"] = strategy # put it in order for the players
                    player_count = player_count + 1 # increase player count 

        self.print_all_tables()


    def enter_tables_data_terminal(self):
        for i in range(1, self.number_of_tables + 1):
            table_game = self.game_tables[f"Table {i}"]
            for row in table_game.p1_rows:
                for col in table_game.p2_columns:
                    table_game.table_df.at[row, col] = "I"
                    print("Currently the table format is: ")
                    table_game.print_table()
                    value = input(f"Enter the utilities values for strategies ({row}, {col}) in {table_game.table_name} (ex: 1,2): ")
                    value = value.strip()
                    value_tuple = tuple(map(int, value.split(',')))
                    table_game.table_df.at[row, col] = value_tuple
            print(f"Final Form of Table {i}")
            table_game.print_table()


    def create_players(self):
        for player_name in self.list_of_players:
            strategy = self.players_strategy_sets[player_name]
            player = Player(player_name,strategy)
            self.players[player_name] = player


    def take_mixed_strategy(self,uN=1,mixed_strategy=[]):
        if self.mode == "Terminal":
            uN = int(input("Enter the player number you want to enter the mixed strategy for: "))
            mixed_strategy = input(f"\nPlease enter the mixed strategies for these strategies (ex: 0.5,0.2,0.3): ")
            mixed_strategy = mixed_strategy.strip()
            mixed_strategy = mixed_strategy.split(",")
        player = self.players[f"Player {uN}"]
        player.set_mixed_strategy(mixed_strategy)


    def take_belief(self,uN=1,belief=[]):
        if self.mode == "Terminal":
            uN = int(input("Enter the player number you want to enter his belief: "))
        if self.number_of_players == 2:
            if uN==1:
                belief_about_player = 2
            else:
                belief_about_player = 1
            belief_on_strategies = self.players_strategy_sets[f"Player {belief_about_player}"]
        else:
            player_name = f"Player {uN}"
            # Extract keys, convert to lists, and drop the specific index
            belief_on_strategies = [list(key) for key in self.profiles_utilities.keys()]
            index_to_drop = uN - 1
            belief_on_strategies = [key[:index_to_drop] + key[index_to_drop + 1:] for key in belief_on_strategies]
            belief_on_strategies = [list(item) for item in set(tuple(sublist) for sublist in belief_on_strategies)]
        if self.mode == "Terminal":
            belief = input(f"\nPlease enter Player {uN} belief for these strategies in order {belief_on_strategies} separated by commas (ex: 0.5,0.2,0.3): ")
            belief = belief.strip()
            belief = belief.split(",")

        belief_dict = {}

        for i,strategy in enumerate(belief_on_strategies):
            if self.number_of_players == 2:
                belief_dict[strategy] = belief[i]
            else:
                belief_dict[tuple(strategy)] = belief[i]

        player = self.players[f"Player {uN}"]
        player.belief = belief
        player.belief_dict = belief_dict

        print(f"{player.player_name} Belief: ")
        print(player.belief)
        print(player.belief_dict)


    ################## CALCULATIONS FUNCTIONS ##################
    def print_all_calculations(self):
        self.calculate_strategy_profile()
        self.calculate_utility_for_strategy_profile()
        self.calculate_utility()


    def calculate_strategy_profile(self):
        # Extract player names and strategies
        strategies = list(self.players_strategy_sets.values())
        
        # Compute the cartesian product of strategies
        profiles = list(product(*strategies))
        
        self.strategy_profiles = profiles
        print("Strategy Profile: ")
        print(self.strategy_profiles)
        return self.strategy_profiles


    def calculate_utility(self,uN=1,strategies=None,mode="Terminal"):
        
        if mode == "Terminal":
            uN = int(input("Enter the player number you want to calculate the utility for: "))
            strategies = input(f"\nPlease enter strategies you want to get the utility for separated by commas (ex: A,C,F,G): ")
            strategies = strategies.strip()
            strategies = strategies.split(",")

        if self.number_of_players > 2:
            rest_players_strategies = {}
            for i,strategy in enumerate(strategies):
                if i == 0 or i == 1:
                    continue
                rest_players_strategies[f"Player {i+1}"] = strategy
            for game_table in self.game_tables.values():
                if game_table.static_players_strategies == rest_players_strategies:
                    table_name = game_table.table_name
            
            return 0
        else:
            table_name = "Table 1"
        
        my_table_game = self.game_tables[table_name]
        utility = my_table_game.table_df.at[strategies[0], strategies[1]] [uN-1]

        print(f"Utility of Player {uN} with strategies {strategies} = u{uN}{strategies} = {utility}")
        return utility


    def calculate_utility_for_strategy_profile(self):
        for strategy_profile in self.strategy_profiles:
            total_utility = []
            for i in range(1,self.number_of_players+1):
                utility = self.calculate_utility(i,strategy_profile,mode="Silent")
                total_utility.append(utility)
            self.profiles_utilities[strategy_profile] = total_utility
        print("Strategy Profiles Utilities: ")
        print(self.profiles_utilities)
        return self.profiles_utilities

    def get_expected_payoff(self):

        if self.number_of_players == 2:
            print("Which player do you want to calculate the utility for?")
            utility_for_player_number = get_int_input(1,self.number_of_players)
            player1 = self.players["Player 1"]
            player2 = self.players["Player 2"]
            p1_strategies = player1.strategy_set.copy()
            p2_strategies = player2.strategy_set.copy()
            if player1.mixed_strategy != 0:
                p1_strategies.append("Sigma1")
            if player2.mixed_strategy != 0:
                p2_strategies.append("Sigma2")
            if player1.belief != 0:
                p2_strategies.append("Theta2")
            if player2.belief != 0:
                p1_strategies.append("Theta1")
            flag = True
            while flag:
                print(f"These are Player 1 available strategies: {p1_strategies}")
                p1_strategy = input("What strategy do you want to choose for player 1: ")
                if p1_strategy in p1_strategies:
                    flag = False
                else:
                    print(f"Please choose one of the mentioned options in: {p1_strategies}")
            
            flag = True
            while flag:
                print(f"These are Player 2 available strategies: {p2_strategies}")
                p2_strategy = input("What strategy do you want to choose for player 2: ")
                if p2_strategy in p2_strategies:
                    flag = False
                else:
                    print(f"Please choose one of the mentioned options in: {p2_strategies}")
            
            print(f"Calculating u{utility_for_player_number}({p1_strategy,p2_strategy})")
            if p1_strategy!="Sigma1" and p1_strategy!="Theta1" and p2_strategy!="Sigma2" and p2_strategy!="Theta2":
                self.calculate_utility(uN=utility_for_player_number,strategies=[p1_strategy,p2_strategy],mode="Silent")
            if p1_strategy == "Sigma1" and p2_strategy!="Sigma2" and p2_strategy !="Theta2":
                mixed_strategy_dict = player1.mixed_strategy_dict
                expected_payoff = 0
                for cell,total_utility in self.profiles_utilities.items():
                    if cell[1]!=p2_strategy:
                        continue
                    utility_value = total_utility[utility_for_player_number-1]
                    utility_value = utility_value * float(mixed_strategy_dict[cell[0]])
                    expected_payoff = expected_payoff + float(utility_value)
            if p2_strategy == "Sigma2" and p1_strategy!="Sigma1" and p2_strategy !="Theta1":
                mixed_strategy_dict = player2.mixed_strategy_dict
                expected_payoff = 0
                for cell,total_utility in self.profiles_utilities.items():
                    if cell[0]!=p1_strategy:
                        continue
                    utility_value = total_utility[utility_for_player_number-1]
                    utility_value = utility_value * float(mixed_strategy_dict[cell[1]])
                    expected_payoff = expected_payoff + float(utility_value)

            if p1_strategy == "Theta1" and p2_strategy!="Sigma2" and p2_strategy !="Theta2":
                belief_dict = player2.belief_dict
                expected_payoff = 0
                for cell,total_utility in self.profiles_utilities.items():
                    if cell[1]!=p2_strategy:
                        continue
                    utility_value = total_utility[utility_for_player_number-1]
                    utility_value = utility_value * float(belief_dict[cell[0]])
                    expected_payoff = expected_payoff + float(utility_value)
            if p2_strategy == "Theta2" and p1_strategy!="Sigma1" and p2_strategy !="Theta1":
                belief_dict = player1.belief_dict
                print(belief_dict)
                expected_payoff = 0
                for cell,total_utility in self.profiles_utilities.items():
                    if cell[0]!=p1_strategy:
                        continue
                    utility_value = total_utility[utility_for_player_number-1]
                    utility_value = utility_value * float(belief_dict[cell[1]])
                    expected_payoff = expected_payoff + float(utility_value)

            if p1_strategy == "Sigma1" and p2_strategy == "Sigma2":
                mixed_strategy_dict_p1 = player1.mixed_strategy_dict
                mixed_strategy_dict_p2 = player2.mixed_strategy_dict
                expected_payoff = 0
                for cell, total_utility in self.profiles_utilities.items():
                    utility_value = total_utility[utility_for_player_number - 1]
                    utility_value *= float(mixed_strategy_dict_p1[cell[0]]) * float(mixed_strategy_dict_p2[cell[1]])
                    expected_payoff += utility_value

            if p1_strategy == "Theta1" and p2_strategy == "Theta2":
                belief_dict_p1 = player2.belief_dict
                belief_dict_p2 = player1.belief_dict
                expected_payoff = 0
                for cell, total_utility in self.profiles_utilities.items():
                    utility_value = total_utility[utility_for_player_number - 1]
                    utility_value *= float(belief_dict_p1[cell[0]]) * float(belief_dict_p2[cell[1]])
                    expected_payoff += utility_value

            if p1_strategy == "Sigma1" and p2_strategy == "Theta2":
                mixed_strategy_dict = player1.mixed_strategy_dict
                belief_dict = player1.belief_dict
                expected_payoff = 0
                for cell, total_utility in self.profiles_utilities.items():
                    utility_value = total_utility[utility_for_player_number - 1]
                    utility_value *= float(mixed_strategy_dict[cell[0]]) * float(belief_dict[cell[1]])
                    expected_payoff += utility_value

            if p1_strategy == "Theta1" and p2_strategy == "Sigma2":
                belief_dict = player2.belief_dict
                mixed_strategy_dict = player2.mixed_strategy_dict
                expected_payoff = 0
                for cell, total_utility in self.profiles_utilities.items():
                    utility_value = total_utility[utility_for_player_number - 1]
                    utility_value *= float(belief_dict[cell[0]]) * float(mixed_strategy_dict[cell[1]])
                    expected_payoff += utility_value
            
            print(f"Expected Payoff u{utility_for_player_number}({p1_strategy,p2_strategy}) = {expected_payoff}")
        else:  # More than 2 players
            print("There are more than 2 players. Please select a player whose belief you want to use:")

            chosen_player_number = get_int_input(1, self.number_of_players)
            chosen_player = self.players[f"Player {chosen_player_number}"]

            if chosen_player.belief == 0:
                print(f"Player {chosen_player_number} does not have a belief set.")
                return

            belief_dict = chosen_player.belief_dict
            print(f"Using belief of Player {chosen_player_number}: {belief_dict}")

            # Remove the chosen player's strategies from profiles_utilities keys
            chosen_player_index = chosen_player_number - 1
            reduced_profiles_utilities = {}
            for profile, utilities in self.profiles_utilities.items():
                reduced_profile = tuple(strategy for i, strategy in enumerate(profile) if i != chosen_player_index)
                reduced_profiles_utilities[reduced_profile] = utilities

            print(f"Reduced profiles_utilities: {reduced_profiles_utilities}")

            # Calculate expected payoff using belief_dict and reduced_profiles_utilities
            expected_payoff = 0
            for reduced_profile, utilities in reduced_profiles_utilities.items():
                if reduced_profile in belief_dict:
                    belief_value = float(belief_dict[reduced_profile])
                    utility_value = utilities[utility_for_player_number - 1]  # Utility for the player of interest
                    expected_payoff += utility_value * belief_value

            print(f"Expected Payoff u{utility_for_player_number}(Theta{chosen_player_number}) = {expected_payoff}")   

    def calculate_dominance(self):

        table = self.game_tables["Table 1"].table_df
        player1_strategies = table.index.tolist()  # Rows represent Player 1's strategies
        player2_strategies = table.columns.tolist()  # Columns represent Player 2's strategies

        dominance_results = {"Player 1": {}, "Player 2": {}}

        # Check dominance for Player 1
        for i, strategy_i in enumerate(player1_strategies):
            for j, strategy_j in enumerate(player1_strategies):
                if i == j:
                    continue

                strictly_dominates = True
                weakly_dominates = True
                for col in player2_strategies:
                    payoff_i = table.at[strategy_i, col][0]
                    payoff_j = table.at[strategy_j, col][0]

                    if payoff_i <= payoff_j:  # Not strictly better
                        strictly_dominates = False
                    if payoff_i < payoff_j:  # Not even weakly better
                        weakly_dominates = False

                if strictly_dominates:
                    dominance_results["Player 1"][strategy_j] = f"Strictly Dominated by {strategy_i}"
                elif weakly_dominates:
                    dominance_results["Player 1"][strategy_j] = f"Weakly Dominated by {strategy_i}"

        # Check dominance for Player 2
        for i, strategy_i in enumerate(player2_strategies):
            for j, strategy_j in enumerate(player2_strategies):
                if i == j:
                    continue

                strictly_dominates = True
                weakly_dominates = True
                for row in player1_strategies:
                    payoff_i = table.at[row, strategy_i][1]
                    payoff_j = table.at[row, strategy_j][1]

                    if payoff_i <= payoff_j:  # Not strictly better
                        strictly_dominates = False
                    if payoff_i < payoff_j:  # Not even weakly better
                        weakly_dominates = False

                if strictly_dominates:
                    dominance_results["Player 2"][strategy_j] = f"Strictly Dominated by {strategy_i}"
                elif weakly_dominates:
                    dominance_results["Player 2"][strategy_j] = f"Weakly Dominated by {strategy_i}"

        # Check mixed strategy dominance for Player 1
        player1 = self.players["Player 1"]
        if player1.mixed_strategy != 0:
            mixed_strategy_dict = player1.mixed_strategy_dict
            mixed_strategy_payoffs = {}

            for col in player2_strategies:
                expected_payoff = 0
                for row in player1_strategies:
                    payoff = table.at[row, col][0]
                    expected_payoff += float(mixed_strategy_dict[row]) * payoff
                mixed_strategy_payoffs[col] = expected_payoff

            for strategy in player1_strategies:
                strictly_dominated = True
                weakly_dominated = True
                for col in player2_strategies:
                    payoff_pure = table.at[strategy, col][0]
                    payoff_mixed = mixed_strategy_payoffs[col]

                    if payoff_pure >= payoff_mixed:  # Not strictly dominated
                        strictly_dominated = False
                    if payoff_pure > payoff_mixed:  # Not even weakly dominated
                        weakly_dominated = False

                if strictly_dominated:
                    dominance_results["Player 1"][strategy] = "Strictly Dominated by Mixed Strategy"
                elif weakly_dominated:
                    dominance_results["Player 1"][strategy] = "Weakly Dominated by Mixed Strategy"

        # Check mixed strategy dominance for Player 2
        player2 = self.players["Player 2"]
        if player2.mixed_strategy != 0:
            mixed_strategy_dict = player2.mixed_strategy_dict
            mixed_strategy_payoffs = {}

            for row in player1_strategies:
                expected_payoff = 0
                for col in player2_strategies:
                    payoff = table.at[row, col][1]
                    expected_payoff += float(mixed_strategy_dict[col]) * payoff
                mixed_strategy_payoffs[row] = expected_payoff

            for strategy in player2_strategies:
                strictly_dominated = True
                weakly_dominated = True
                for row in player1_strategies:
                    payoff_pure = table.at[row, strategy][1]
                    payoff_mixed = mixed_strategy_payoffs[row]

                    if payoff_pure >= payoff_mixed:  # Not strictly dominated
                        strictly_dominated = False
                    if payoff_pure > payoff_mixed:  # Not even weakly dominated
                        weakly_dominated = False

                if strictly_dominated:
                    dominance_results["Player 2"][strategy] = "Strictly Dominated by Mixed Strategy"
                elif weakly_dominated:
                    dominance_results["Player 2"][strategy] = "Weakly Dominated by Mixed Strategy"

        # Print results
        print("Dominance Results:")
        for player, results in dominance_results.items():
            print(f"{player}:")
            if results:
                for strategy, dominance_info in results.items():
                    print(f"  Strategy {strategy}: {dominance_info}")
            else:
                print("No dominated strategies.")              


    def calculate_best_response(self):
        player1 = self.players["Player 1"]
        player2 = self.players["Player 2"]

        best_response_results = {}

        # Check Best Response for Player 1
        if player1.belief != 0:  # Player 1 has a belief about Player 2
            belief_dict_p2 = {key: float(value) for key, value in player1.belief_dict.items()}  # Ensure float conversion
            p1_strategies = player1.strategy_set
            expected_payoffs = {}

            for strategy_p1 in p1_strategies:
                expected_payoff = 0
                for strategy_p2, belief in belief_dict_p2.items():
                    payoff = self.game_tables["Table 1"].table_df.at[strategy_p1, strategy_p2][0]
                    expected_payoff += payoff * belief
                expected_payoffs[strategy_p1] = expected_payoff

            max_payoff = max(expected_payoffs.values())
            best_responses_p1 = [strategy for strategy, payoff in expected_payoffs.items() if payoff == max_payoff]
            best_response_results["Player 1"] = {"Best Responses": best_responses_p1, "Payoff": max_payoff}

        # Check Best Response for Player 2
        if player2.belief != 0:  # Player 2 has a belief about Player 1
            belief_dict_p1 = {key: float(value) for key, value in player2.belief_dict.items()}  # Ensure float conversion
            p2_strategies = player2.strategy_set
            expected_payoffs = {}

            for strategy_p2 in p2_strategies:
                expected_payoff = 0
                for strategy_p1, belief in belief_dict_p1.items():
                    payoff = self.game_tables["Table 1"].table_df.at[strategy_p1, strategy_p2][1]
                    expected_payoff += payoff * belief
                expected_payoffs[strategy_p2] = expected_payoff

            max_payoff = max(expected_payoffs.values())
            best_responses_p2 = [strategy for strategy, payoff in expected_payoffs.items() if payoff == max_payoff]
            best_response_results["Player 2"] = {"Best Responses": best_responses_p2, "Payoff": max_payoff}

        # Print Results
        if "Player 1" in best_response_results:
            responses = ", ".join(best_response_results["Player 1"]["Best Responses"])
            print(f"Best Response of Player 1 to Theta2 BR1(Theta2) = {responses} with payoff {best_response_results['Player 1']['Payoff']:.6f}")
        if "Player 2" in best_response_results:
            responses = ", ".join(best_response_results["Player 2"]["Best Responses"])
            print(f"Best Response of Player 2 to Theta1 BR2(Theta1) = {responses} with payoff {best_response_results['Player 2']['Payoff']:.6f}")

        if not best_response_results:
            print("Neither player has a belief. Best response cannot be calculated.")


    def calculate_rationalizable_strategies(self):
        # Make a copy of the original game table
        current_table = self.game_tables["Table 1"].table_df.copy()
        rows_kept = current_table.index.tolist()
        cols_kept = current_table.columns.tolist()

        print("Initial Table:")
        print(current_table)

        while True:
            row_removed = False
            col_removed = False

            # Check dominance for Player 1 (rows)
            for i, strategy_i in enumerate(rows_kept):
                for j, strategy_j in enumerate(rows_kept):
                    if i == j:
                        continue

                    strictly_dominates = True
                    weakly_dominates = True
                    for col in cols_kept:
                        payoff_i = current_table.at[strategy_i, col][0]
                        payoff_j = current_table.at[strategy_j, col][0]

                        if payoff_i <= payoff_j:  # Not strictly better
                            strictly_dominates = False
                        if payoff_i < payoff_j:  # Not even weakly better
                            weakly_dominates = False

                    if strictly_dominates:
                        print(f"{strategy_j} is strictly dominated by {strategy_i}. Removing {strategy_j} row.")
                        current_table = current_table.drop(index=strategy_j)
                        rows_kept.remove(strategy_j)
                        row_removed = True
                        break
                    elif weakly_dominates:
                        print(f"{strategy_j} is weakly dominated by {strategy_i}. Removing {strategy_j} row.")
                        current_table = current_table.drop(index=strategy_j)
                        rows_kept.remove(strategy_j)
                        row_removed = True
                        break
                if row_removed:
                    break

            # Check mixed strategy dominance for Player 1
            player1 = self.players["Player 1"]
            if player1.mixed_strategy != 0:
                mixed_strategy_dict = player1.mixed_strategy_dict
                mixed_strategy_payoffs = {}

                for col in cols_kept:
                    expected_payoff = 0
                    for row in rows_kept:
                        payoff = current_table.at[row, col][0]
                        expected_payoff += float(mixed_strategy_dict[row]) * payoff
                    mixed_strategy_payoffs[col] = expected_payoff

                for strategy in rows_kept[:]:
                    strictly_dominated = True
                    weakly_dominated = True
                    for col in cols_kept:
                        payoff_pure = current_table.at[strategy, col][0]
                        payoff_mixed = mixed_strategy_payoffs[col]

                        if payoff_pure >= payoff_mixed:  # Not strictly dominated
                            strictly_dominated = False
                        if payoff_pure > payoff_mixed:  # Not even weakly dominated
                            weakly_dominated = False

                    if strictly_dominated:
                        print(f"{strategy} is strictly dominated by the mixed strategy of Player 1. Removing {strategy} row.")
                        current_table = current_table.drop(index=strategy)
                        rows_kept.remove(strategy)
                        row_removed = True
                    elif weakly_dominated:
                        print(f"{strategy} is weakly dominated by the mixed strategy of Player 1. Removing {strategy} row.")
                        current_table = current_table.drop(index=strategy)
                        rows_kept.remove(strategy)
                        row_removed = True

            # Check dominance for Player 2 (columns)
            for i, strategy_i in enumerate(cols_kept):
                for j, strategy_j in enumerate(cols_kept):
                    if i == j:
                        continue

                    strictly_dominates = True
                    weakly_dominates = True
                    for row in rows_kept:
                        payoff_i = current_table.at[row, strategy_i][1]
                        payoff_j = current_table.at[row, strategy_j][1]

                        if payoff_i <= payoff_j:  # Not strictly better
                            strictly_dominates = False
                        if payoff_i < payoff_j:  # Not even weakly better
                            weakly_dominates = False

                    if strictly_dominates:
                        print(f"{strategy_j} is strictly dominated by {strategy_i}. Removing {strategy_j} column.")
                        current_table = current_table.drop(columns=strategy_j)
                        cols_kept.remove(strategy_j)
                        col_removed = True
                        break
                    elif weakly_dominates:
                        print(f"{strategy_j} is weakly dominated by {strategy_i}. Removing {strategy_j} column.")
                        current_table = current_table.drop(columns=strategy_j)
                        cols_kept.remove(strategy_j)
                        col_removed = True
                        break
                if col_removed:
                    break

            # Check mixed strategy dominance for Player 2
            player2 = self.players["Player 2"]
            if player2.mixed_strategy != 0:
                mixed_strategy_dict = player2.mixed_strategy_dict
                mixed_strategy_payoffs = {}

                for row in rows_kept:
                    expected_payoff = 0
                    for col in cols_kept:
                        payoff = current_table.at[row, col][1]
                        expected_payoff += float(mixed_strategy_dict[col]) * payoff
                    mixed_strategy_payoffs[row] = expected_payoff

                for strategy in cols_kept[:]:
                    strictly_dominated = True
                    weakly_dominated = True
                    for row in rows_kept:
                        payoff_pure = current_table.at[row, strategy][1]
                        payoff_mixed = mixed_strategy_payoffs[row]

                        if payoff_pure >= payoff_mixed:  # Not strictly dominated
                            strictly_dominated = False
                        if payoff_pure > payoff_mixed:  # Not even weakly dominated
                            weakly_dominated = False

                    if strictly_dominated:
                        print(f"{strategy} is strictly dominated by the mixed strategy of Player 2. Removing {strategy} column.")
                        current_table = current_table.drop(columns=strategy)
                        cols_kept.remove(strategy)
                        col_removed = True
                    elif weakly_dominated:
                        print(f"{strategy} is weakly dominated by the mixed strategy of Player 2. Removing {strategy} column.")
                        current_table = current_table.drop(columns=strategy)
                        cols_kept.remove(strategy)
                        col_removed = True

            # If no rows or columns were removed, stop the iteration
            if not row_removed and not col_removed:
                break

            # Print the updated table after each iteration
            print("Updated Table:")
            print(current_table)

        # Print final rationalizable strategies
        print(f"Final Rationalizable Strategies:")
        print(f"R1 = {rows_kept}")
        print(f"R2 = {cols_kept}")



    def get_mixed_strategy_that_dominates(self, player_number=1, strategy_to_dominate=""):
        if strategy_to_dominate=="":
            print("Which player do you want to calculate the dominant mixed strategy for?")
            player_number = get_int_input(1,self.number_of_players)
            strategies = self.players_strategy_sets[f"Player {player_number}"]
            print(f"Which strategy do you want to dominate from these {strategies}?")
            strategy_to_dominate = input("Your choice of strategy: ")

        # Identify the player and their strategies
        player = self.players[f"Player {player_number}"]
        other_player_number = 2 if player_number == 1 else 1
        other_player = self.players[f"Player {other_player_number}"]

        player_strategies = player.strategy_set
        other_player_strategies = other_player.strategy_set

        if strategy_to_dominate not in player_strategies:
            print(f"Error: Strategy '{strategy_to_dominate}' is not in Player {player_number}'s strategy set.")
            return

        # Define the variable for the mixed strategy
        p = symbols("p")
        index_to_dominate = player_strategies.index(strategy_to_dominate)

        # Store constraints for the dominance condition
        constraints = []
        for other_strategy in other_player_strategies:
            payoff_mixed = 0
            for i, player_strategy in enumerate(player_strategies):
                if i == index_to_dominate:
                    continue
                weight = p if i == 0 else (1 - p)
                payoff = self.game_tables["Table 1"].table_df.at[player_strategy, other_strategy][player_number - 1]
                payoff_mixed += weight * payoff

            payoff_to_dominate = self.game_tables["Table 1"].table_df.at[strategy_to_dominate, other_strategy][player_number - 1]
            constraints.append(payoff_mixed > payoff_to_dominate)

        # Solve the constraints
        feasible_ranges = []
        for constraint in constraints:
            solution = solve_univariate_inequality(constraint, p, relational=True)
            feasible_ranges.append(solution)

        # Combine the feasible ranges
        if not feasible_ranges:
            print(f"No mixed strategy dominates '{strategy_to_dominate}' for Player {player_number}.")
            return

        # Determine the intersection of all ranges
        combined_interval = feasible_ranges[0]
        for interval in feasible_ranges[1:]:
            combined_interval = And(combined_interval, interval)

        if not combined_interval:
            print(f"No valid range for p to dominate '{strategy_to_dominate}' for Player {player_number}.")
            return

        # Extract the bounds from the combined interval
        lower_bound = combined_interval.args[0].rhs if combined_interval.args[0].rel_op == ">" else 0
        upper_bound = combined_interval.args[1].rhs if combined_interval.args[1].rel_op == "<" else 1

        # Choose a value for p within the range
        p_value = (lower_bound + upper_bound) / 2

        # Construct the mixed strategy
        mixed_strategy = [p_value if i == 0 else 1 - p_value if i == 1 else 0 for i in range(len(player_strategies))]

        # Output the results
        print(f"For mixed strategy (p, 1-p, 0):")
        print(f"{lower_bound} < p < {upper_bound}")
        print(f"Mixed strategy for Player {player_number} that dominates '{strategy_to_dominate}' is: {tuple(mixed_strategy)}")



    def print_all_tables(self):
        for table in self.game_tables:
            self.game_tables[table].print_table()


class GameTable:
    def __init__(self, table_name, table_df):
        self.table_name = table_name
        self.table_df = table_df
        self.p1_rows = table_df.index.tolist()
        self.p2_columns = table_df.columns.tolist()
        self.static_players_strategies = {} #player 3 or 4 


    def print_table(self):
        print(self.table_name)
        print(self.table_df)
        if self.static_players_strategies != {}:
            for player, strategy in self.static_players_strategies.items():
                print(f"{player} Strategy: {strategy}")
        print("\n")


class Player:
    def __init__(self,player_name,strategy_set):
        self.player_name = player_name
        self.strategy_set = strategy_set
        self.player_number = int(player_name.split(" ")[1])
        self.mixed_strategy = 0
        self.belief = 0
        self.mixed_strategy_dict = {}
        self.belief_dict = {}

    def set_mixed_strategy(self,mixed_strategy):
        self.mixed_strategy = mixed_strategy
        for i,strategy in enumerate(self.strategy_set): # [L,M,R]
            self.mixed_strategy_dict[strategy] = self.mixed_strategy[i]
        # {L:0.5, M:0.4, R:0.1}
        print(f"{self.player_name} Mixed Strategy: ")
        print(self.mixed_strategy)
        print(self.mixed_strategy_dict)

    def print_mixed_strategy(self):
        print(f"Mixed Strategy for {self.player_name}: {self.mixed_strategy}")
        print(f"In Details: {self.mixed_strategy_dict}")

    def print_belief(self):
        print(f"Belief for {self.player_name} about other palyers: {self.belief}")
        print(f"In Details: {self.belief_dict}")
        
class TableInputGUI(QMainWindow):
    def __init__(self, row_strategies, col_strategies, game_instance):
        super().__init__()
        self.setWindowTitle("Enter Payoff Table")
        self.setGeometry(100, 100, 1000, 700)
        self.row_strategies = row_strategies
        self.col_strategies = col_strategies
        self.game_instance = game_instance

        self.init_ui()

    def init_ui(self):
        # Set Background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("Background/BG.png")))
        self.setPalette(palette)

        # Title Label
        title_label = QLabel("Payoff Table Input")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: white;")

        # Table Widget
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(len(self.row_strategies))
        self.table_widget.setColumnCount(len(self.col_strategies))
        self.table_widget.setHorizontalHeaderLabels(self.col_strategies)
        self.table_widget.setVerticalHeaderLabels(self.row_strategies)
        self.table_widget.setStyleSheet("""
    QTableWidget { 
        font-size: 18px; 
        border: 1px solid black; 
        background-color: rgba(0, 0, 0, 0.3); 
    }
    QTableWidget::item {
        color: white;
    }
    QHeaderView::section { 
        font-size: 18px;
        color: black; 
    }
""")
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
                            
        # Save Button
        self.save_button = QPushButton("Save Table")
        self.save_button.setFont(QFont("Arial", 14))
        self.save_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; padding: 10px 20px; border-radius: 5px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        self.save_button.clicked.connect(self.save_table)

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(self.table_widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def save_table(self):
        rows = self.row_strategies
        cols = self.col_strategies

        data = pd.DataFrame(
            [[() for _ in cols] for _ in rows],
            columns=cols,
            index=rows
        )

        for row in range(len(rows)):
            for col in range(len(cols)):
                item = self.table_widget.item(row, col)
                if item:
                    try:
                        value = tuple(map(int, item.text().strip().split(",")))
                        data.iloc[row, col] = value
                    except ValueError:
                        print(f"Invalid input at cell ({row}, {col}).")

        self.game_instance.game_tables = {"Table 1": GameTable("Table 1", data)}
        print("Table saved successfully!")
        self.table_widget.setDisabled(True)
        self.save_button.setDisabled(True)
        self.close()
