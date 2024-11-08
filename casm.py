import sys

if len(sys.argv) != 2:
    print("Usage: python casm.py <file path to casm code>")
    exit()

# ----------------------------------------------------------------
file = open(sys.argv[1], "r")
code_lines = [x for x in file.read().split("\n") if len(x) != 0]
for i in range(len(code_lines)):
    curr_line = code_lines[i]
    comment_index = curr_line.find(";")
    if comment_index != -1:
        curr_line = curr_line[:comment_index]
    code_lines[i] = curr_line
file.close()

code_lines = [[y for y in x.split(" ") if len(y) != 0] for x in code_lines]
code_lines = [x for x in code_lines if len(x) != 0]

# ----------------------------------------------------------------
funcs_code = {
    "mov": [1, 2, 3, 4, 5],
    "add":  6, "sub":  7, "and":  8, "or":   9,
    "neg": 10, "xor": 11, "ceq": 12, "cne": 13,
    "cgt": 14, "cge": 15, "clt": 16, "cle": 17,
    "jmn": 18, "jmz": 19, "jmp": 20, "uof": 21
}
funcs_count = 21

bytes = [0 for x in range(8)]
data_bytes = []
code_bytes = []
byte_pos = 0

labels_poses = {}
labels_to_place = {}

for cmd in code_lines:
    if cmd[0][0] == ".":
        if cmd[0] == ".memory":
            data_bytes = [0 for x in range(int(cmd[1]))]
        continue
    elif cmd[0][-1] == ":":
        labels_poses[cmd[0][:-1]] = byte_pos
        continue

    code_bytes.append(funcs_code[cmd[0]])
    if cmd[0] == "mov":
        if cmd[1][0] == "#" and cmd[2][0] == "#":
            code_bytes[-1] = 1
        elif cmd[1][0] == "#" and cmd[2][0] == "*":
            code_bytes[-1] = 2
        elif cmd[1][0] == "*" and cmd[2][0] == "#":
            code_bytes[-1] = 3
        elif cmd[1][0] == "*" and cmd[2][0] == "*":
            code_bytes[-1] = 4
        else:
            code_bytes[-1] = 5
    byte_pos += 1

    for i in range(1, len(cmd)):
        if cmd[i][0] in "#*":
            code_bytes.append(int(cmd[i][3:5], 16))
            code_bytes.append(int(cmd[i][1:3], 16))
            byte_pos += 2
        elif cmd[i].isdigit():
            code_bytes.append(int(cmd[i]))
            byte_pos += 1
        else:
            code_bytes.append(0)
            code_bytes.append(0)
            if cmd[0] in ["jmn", "jmz", "jmp"]:
                if not cmd[i] in labels_to_place.keys():
                    labels_to_place[cmd[i]] = []
                labels_to_place[cmd[i]].append(byte_pos)
            byte_pos += 2

code_shift = len(bytes) + len(data_bytes)

for label, poses in labels_to_place.items():
    for pos in poses:
        code_bytes[pos] = (labels_poses[label] + code_shift) & 0xff
        code_bytes[pos+1] = (labels_poses[label] + code_shift)>>8 & 0xff

code_bytes.append(0)

# ----------------------------------------------------------------
bytes += data_bytes
bytes += code_bytes
bytes += [0 for x in range(funcs_count*8)]

bytes[0] = (len(bytes)) & 0xff
bytes[1] = (len(bytes)>>8) & 0xff
bytes[2] = (len(data_bytes)) & 0xff
bytes[3] = (len(data_bytes)>>8) & 0xff

result = "u8 l0[] = {\n"
for i, a in enumerate(bytes):
    result += "0b{0:0>8b}, ".format(a)
    if (i+1) % 8 == 0:
        result += "\n"
if result[-1] != "\n":
    result += "\n"
result += "};"

file = open(sys.argv[1] + ".txt", "w")
file.write(result)
file.close()
