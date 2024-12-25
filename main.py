from classes import Game
from shared_functions import get_int_input
import traceback

game = Game()
game.print_all_tables()
flag = True
print()
while flag:
    print("Choose 1 to Add Input (Mixed Strategy, Belief)")
    print("Choose 2 to Get Info About Game (Strategy Profiles, Utilities, Print Tables, Mixed Strategies, Beliefs)")
    print("Choose 3 to Calculate Outputs (Expected Payoff, Dominance, Best Response, Rationalizable Strategies)")
    print("Choose 4 for Exit")
    print()
    try:
        choice = get_int_input(1,4)
        if choice == 1:
            print("Choose 1 to add Mixed Strategy")
            print("Choose 2 to add Belief")
            print("Choose 3 to Return Back")
            choice = get_int_input(1,3)
            if choice == 1:
                game.take_mixed_strategy()
            elif choice == 2:
                game.take_belief()
            elif choice == 3:
                print()
                pass

        elif choice == 2:
            print("Choose 1 to Print Game Tables")
            print("Choose 2 to Get Strategy Profiles")
            print("Choose 3 to Get Strategy Profiles Utilities")
            print("Choose 4 to Get Mixed Strategies for a player")
            print("Choose 5 to Get Belief of a player")
            print("Choose 6 to Return Back")
            choice = get_int_input(1,6)
            if choice == 1:
                game.print_all_tables()
            elif choice == 2:
                print(game.strategy_profiles)
            elif choice == 3:
                print(game.profiles_utilities)
            elif choice == 4:
                print("Which player do you want to get its mixed strategy")
                playerNumber = get_int_input(1,game.number_of_players)
                game.players[f"Player {playerNumber}"].print_mixed_strategy()
            elif choice == 5:
                print("Which player do you want to get its belief")
                playerNumber = get_int_input(1,game.number_of_players)
                game.players[f"Player {playerNumber}"].print_belief()
            elif choice == 6:
                print()
                pass

        elif choice == 3:
            print("Choose 1 to Calculate Expected Payoff")
            print("Choose 2 to Calculate Dominance")
            print("Choose 3 to Calculate Best Response")
            print("Choose 4 to Calculate Rationalizable Strategies")
            print("Choose 5 to Return Back")
            choice = get_int_input(1,4)
            if choice == 1:
                game.get_expected_payoff()
            elif choice == 2:
                game.calculate_dominance()
            elif choice == 3:
                game.calculate_best_response()
            elif choice == 4:
                game.calculate_rationalizable_strategies()
            elif choice == 5:
                print()
                pass
        elif choice == 4:
            flag = False
    except Exception as e:
        print("Your input was wrong, double check it please.")
        traceback.print_exc()
    print()
