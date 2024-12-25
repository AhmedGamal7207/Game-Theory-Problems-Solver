def get_int_input(low,high):
    flag = True
    while flag:
        try:
            choice = int(input(f"Your Choice ({low}-{high}): "))
            if choice<low or choice>high:
                print(f"Please enter an int between ({low}-{high})")
            else:
                return choice
        except:
            print(f"Please enter a valid int between ({low}-{high})")