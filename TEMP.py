
def main():

    transform = input("Select transform direction (CF) or (FC): ").upper()

    try:
        input_temp = float(input("Input temperature: "))
    except:
        print("Not valid input")
        exit()

    if transform == "CF":
        print("{} C = {} F".format(input_temp, t_transform(input_temp, 'c')))

    if transform == "FC":
        print("{} F = {} C".format(input_temp, t_transform(input_temp, 'f')))


def t_transform(temp, type):

    if type == 'c':
        return float(temp * 9/5 + 32)
    if type == 'f':
        return float((temp-32) * 5/9)

    return None


if __name__ == "__main__":
    main()