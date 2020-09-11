def yn_input(message):
    while True:
        y_or_n = input("{} [y/n]")
        yn_tf_mapper = {"y":True, "n":False}
        if y_or_n in ["y", "n"]:
            return yn_tf_mapper[y_or_n]
        else:
            print("Answer 'y' or 'n'")