
def convert_pattern_0x(pattern):
    pattern = pattern.upper()
    bytes_list = pattern.split()
    formatted_bytes = ['0x' + byte for byte in bytes_list] 
    return (' '.join(formatted_bytes))

while True:
    print("Enter the pattern name")
    pattern_name = input("> ")

    print("Enter the pattern to be found")
    pattern_find = input("> ")

    if pattern_find.find("0x") == -1:
        pattern_find = convert_pattern_0x(pattern_find)

    print("Enter the packet to be replaced")
    pattern_value = input("> ")
    if pattern_value.find("0x") == -1:
        pattern_value = convert_pattern_0x(pattern_value)

    print("Choose the origin")
    print("[1] Source")
    print("[2] Destination")
    path = input("> ")

    path_string = ""

    if path == "1" :
        path_string = "source"
    elif(path == "2"):
        path_string = "destination"
    else:
        exit()

    with open("./patterns_" + path_string + "/" + pattern_name + "_find.txt", "w") as f:
        f.write(pattern_find)

    with open("./patterns_" + path_string + "/" + pattern_name + "_value.txt", "w") as f:
        f.write(pattern_value)
    #f_value.write(pattern_value)

    print("Pattern created with success!")



