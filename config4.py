import struct
import xml.etree.ElementTree as ET
import sys


def code_num(num):
    binnum = bin(num)[2:]
    binnum = '0' * (18 - len(binnum)) + binnum
    return int(binnum[:8], 2), int(binnum[8:], 2)
    
def decode_num(a, b):
    return int(bin(a)[2:] + bin(b)[2:], 2)

def assembler(inputpath, binpath, logpath):
    with open(inputpath, 'r') as inputfile:
        bindata = []
        logdata = []
        for line in inputfile:
            line = line.strip().split()
            match line[0]:
                case "LOAD":
                    a, b = code_num(int(line[1]))
                    bindata.append(struct.pack('BBH', 237, a, b))
                    logdata.append(f"A=237, B={line[1]}")
                case "READ":
                    bindata.append(struct.pack('B', 120))
                    logdata.append(f"A=120")
                case "WRITE":
                    bindata.append(struct.pack('B', 133))
                    logdata.append(f"A=133")
                case "EQUAL":
                    bindata.append(struct.pack('<BH', 74, int(line[1])))
                    logdata.append(f"A=74, B={line[1]}")
                case _:
                    print(f'No such command: {line[0]}')

    with open(binpath, 'wb') as binfile:
        for line in bindata:
            binfile.write(line)

    logroot = ET.Element("Logfile")
    for elem in logdata:
        node = ET.SubElement(logroot, "logrecord")
        node.text = elem
    ET.ElementTree(logroot).write(logpath, encoding ='utf-8', xml_declaration = True)

def interpreter(binarypath, outputpath, a, b):
    memory = [0] * 1024
    stack = []
    with open(binarypath, 'rb') as bf:
        data = bf.read()
    pointer = 0
    while pointer < len(data):
        match data[pointer]:
            case 237:
                _, a, b = struct.unpack('BBH', data[pointer:pointer+4])
                stack.append(decode_num(a, b))
                pointer += 4
            case 120:
                stack.append(memory[stack.pop()])
                pointer += 1
            case 133:
                elem = stack.pop()
                memory[elem] = elem
                pointer += 1
            case 74:
                _, b = struct.unpack('<BH', data[pointer:pointer+3])
                elem = stack.pop()
                memory[elem] = int(elem == memory[b])
                pointer += 3
            case _:
                print(f'no such command: {data[pointer]}')
                
    outroot = ET.Element("Output")
    for i, elem in enumerate(memory[a:b+1]):
        node = ET.SubElement(outroot, 'index_' + str(i))
        node.text = str(elem)
    ET.ElementTree(outroot).write(outputpath, encoding ='utf-8', xml_declaration = True)

def main():
    inputpath, binarypath, minindex, maxindex = sys.argv[1:5]
    if len(sys.argv) == 6:
        logpath = sys.argv[5]
    else:
        logpath = 'log.xml'
    outputpath = 'result.xml'
    assembler(inputpath, binarypath, logpath)
    interpreter(binarypath, outputpath, minindex, maxindex)

if __name__ == '__main__':
    main()



