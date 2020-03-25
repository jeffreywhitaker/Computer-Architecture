"""CPU functionality."""

import sys

# set OP codes
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
ADD = 0b10100000

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # initialize the 8 registers, and PC
        self.register = [0] * 8
        self.ram = [0] * 256
        self.pc = 0

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        try:
            with open(filename) as f:
                for line in f:
                    # ignore ## comments
                    comments_removed = line.split("#")
                    # remove whitespace
                    num = comments_removed[0].strip()

                    # ignore blank lines
                    if num == '':
                        continue

                    # convert to integer
                    value = int(num, 2)

                    # write and increment
                    self.ram_write(address, value)
                    address += 1

        except FileNotFoundError:
            print(f" {sys.argv[0]}: {filename} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        reg_a = int(reg_a)
        reg_b = int(reg_b)

        if op == ADD:
            self.register[reg_a] += self.register[reg_b]
            self.pc += 3
        #elif op == "SUB": etc
        elif op == MUL:
            self.register[reg_a] *= self.register[reg_b]
            self.pc += 3
        # if op == "LDI":
        #     ram_write(register[0], 8)
        else:
            raise Exception("Unsupported ALU operation")
    
    def ram_read(self, address_to_read):
        return self.ram[address_to_read]

    def ram_write(self, address_to_write, value):
        self.ram[address_to_write] = value

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while True:
            # read memory address stored in pc, set that to ir, read command
            ir = self.pc
            op = self.ram_read(ir)

            # get operand_a and _b in case we need them
            operand_a = self.ram_read(ir + 1)
            operand_b = self.ram_read(ir + 2)

            # make the if else loop
            if op == HLT:
                break
            elif op == LDI:
                # self.ram_write(int(operand_a), operand_b)
                self.register[operand_a] = operand_b
                self.pc += 3
            elif op == PRN:
                print(self.register[operand_a])
                # code_to_print = self.ram_read(operand_a)
                # print(int(code_to_print))
                self.pc += 2
            # if marked as such, run the ALU
            elif op == MUL:
                self.alu(op, operand_a, operand_b)
            else:
                print(f"Unknown instruction: {op}")
                sys.exit(1)

