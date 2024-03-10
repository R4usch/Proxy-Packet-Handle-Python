import socket
import select
import os

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

src = "127.0.0.1:4510"
dst = "26.4.185.33:4510"

BUFFER_SIZE = 2 ** 10

def ip_to_tuple(ip):
    ip, port = ip.split(':')
    return (ip, int(port))

def find_pattern(byte_string, pattern):
    pattern_length = len(pattern)
    byte_length = len(byte_string)
    
    for i in range(byte_length - pattern_length + 1):
        match = True
        for j in range(pattern_length):
            if pattern[j] is not None and byte_string[i+j] != pattern[j]:
                match = False
                break
        if match:
            return match
    return False

def parse_pattern(pattern_string):
    pattern_list = pattern_string.split(" ")  # Dividir a string pelos separadores ","
    
    pattern = []
    for item in pattern_list:
        item = item.strip().upper()  # Converter para maiúsculas
        if item == "NONE":
            pattern.append(None)
        else:
            # Remover o prefixo "0X" e converter o valor hexadecimal para inteiro
            if item.startswith("0X"):
                item = item[2:]
            pattern.append(int(item, 16))
            
    return pattern

def parse_pattern_to_bytes(pattern_string):
    pattern_list = pattern_string.split(" ")  # Dividir a string pelos separadores ","
    
    pattern = b''  # Inicializar um objeto de bytes vazio
    for item in pattern_list:
        item = item.strip().upper()  # Converter para maiúsculas
        if item == "NONE":
            pattern += b'\x00'  # Adicionar um byte nulo
        else:
            # Remover o prefixo "0X" e converter o valor hexadecimal para um byte
            if item.startswith("0X"):
                item = item[2:]
            pattern += bytes.fromhex(item)
            
    return pattern


def tcp_proxy(src, dst, timeout):

    sockets = []
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(ip_to_tuple(src))
    s.listen(1)
    s.settimeout(timeout)

    print("Waiting connections...")
    s_src, _ = s.accept()

    print("Connection received.")
    
    s_dst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Connecting to " + dst)
    s_dst.connect(ip_to_tuple(dst)) 

    sockets.append(s_src)
    sockets.append(s_dst)
    
    while True:
        s_read, _, _ = select.select(sockets, [], [])

        for s in s_read:
            data = s.recv(BUFFER_SIZE)

            if not data: 
                print("Connection closed. Reopenning...")
                s_src.close()
                s_dst.close()
                tcp_proxy(src,dst, 10)
                return

            if s == s_src:
                hex_string = "[CLIENT]" + ' '.join([f'0x{byte:02X}' for byte in data])
                print(hex_string)

                files = os.listdir("patterns_source")

                s_dst.sendall(data)
            elif s == s_dst:
                hex_string = "[SERVER]" + ' '.join([f'0x{byte:02X}' for byte in data])
                print(hex_string)

                files = os.listdir("patterns_destination")
                match = False
                pattern_filename = ""

                for file in files:
                    if file.endswith("find.txt"):
                        with open("./patterns_destination/" + file, "r") as f:
                            match = find_pattern(data, parse_pattern(f.read()))

                            if match:
                                pattern_filename = file
                                break
                
                if match:
                    print(f"[SERVER] Pattern {pattern_filename.replace(".txt", "")} detected")
                    with open("./patterns_destination/" + pattern_filename.replace("_find", "_value"), "r") as f:
                        data = parse_pattern_to_bytes(f.read())
                    print("[SERVER] NEW DATA :" + f'{data}')
                    
                s_src.sendall(data)

tcp_proxy(src, dst, 300)