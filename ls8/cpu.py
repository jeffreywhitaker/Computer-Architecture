"""CPU functionality."""

import sys

# set OP codes
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b1000110
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101
CMP = 0b10100111

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # initialize the 8 registers, and PC
        self.register = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.flag = 0

        # implement branchtable
        self.branchtable = {
            HLT: self.HLT,
            MUL: self.alu,
            ADD: self.alu,
            PUSH: self.PUSH,
            POP: self.POP,
            LDI: self.LDI,
            PRN: self.PRN,
            JMP: self.JMP,
            JNE: self.JNE,
            JEQ: self.JEQ,
            CMP: self.alu
        }

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
        # reg_a = int(reg_a)
        # reg_b = int(reg_b)

        if op == ADD:
            self.register[reg_a] += self.register[reg_b]
            self.pc += 3
        elif op == MUL:
            self.register[reg_a] *= self.register[reg_b]
            self.pc += 3
        elif op == CMP:
            '''
            * If they are equal, set the Equal `E` flag to 1, otherwise set it to 0.

            * If registerA is less than registerB, set the Less-than `L` flag to 1,
            otherwise set it to 0.

            * If registerA is greater than registerB, set the Greater-than `G` flag
            to 1, otherwise set it to 0.
            '''
            if self.register[reg_a] == self.register[reg_b]:
                self.flag = 0b00000001
            if self.register[reg_a] < self.register[reg_b]:
                self.flag = 0b00000010
            if self.register[reg_a] > self.register[reg_b]:
                self.flag = 0b00000100
            self.pc += 3
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

            if op in self.branchtable:
                if op in [ADD, MUL, CMP]:
                    self.branchtable[op](op, operand_a, operand_b)
                elif op >> 6 == 0:
                    self.branchtable[op]()
                elif op >> 6 == 1:
                    self.branchtable[op](operand_a)
                elif op >> 6 == 2:
                    self.branchtable[op](operand_a, operand_b)
            else:
                print(f"Unknown instruction: {op}")
                sys.exit(1)

    # set register at op_a to value of op_b
    def LDI(self, operand_a, operand_b):
        self.register[operand_a] = operand_b
        self.pc += 3
    
    # print op_a
    def PRN(self, operand_a):
        print(self.register[operand_a])
        self.pc += 2

    # copy register value to ram, decrement sp
    def PUSH(self, register_a):
        self.register[7] -= 1
        self.ram[self.register[7]] = self.register[register_a]
        self.pc += 2

    # copy ram to register, increment sp
    def POP(self, register_a):
        self.register[register_a] = self.ram[self.register[7]]
        self.register[7] += 1
        self.pc += 2

    # stop with okay exit code
    def HLT(self):
        sys.exit(0)

    # Set the `PC` to the address stored in the given register
    def JMP(self, register_a):
        self.pc = self.register[register_a]

    # If `equal` flag is set (true), jump to the address stored in the given register.
    def JEQ(self, register_a):
        # less, greater, equal
        if self.flag == 0b00000001:
            self.JMP(register_a)
        else:
            self.pc += 2

    # If `E` flag is clear (false, 0), jump to the address stored in the given register.
    def JNE(self, register_a):
        if self.flag == 0b00000010 or self.flag == 0b00000100:
            self.JMP(register_a)
        else:
            self.pc += 2

    
