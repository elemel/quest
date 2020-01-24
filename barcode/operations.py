from enum import Enum
from fractions import Fraction as Q

from barcode.register import Register

IR = Register.INSTRUCTION.value - 1
SR = Register.STACK.value - 1
FR = Register.FRAME.value - 1

MNEMONIC_TO_OPCODE = {}
OPCODE_TO_OPERATION = {}


class BlockedError(Exception):
    pass


class TerminatedError(Exception):
    pass


def operation(opcode, mnemonic=None):
    def decorate(func):
        nonlocal mnemonic
        mnemonic = mnemonic or func.__name__

        if opcode in OPCODE_TO_OPERATION:
            raise ValueError(f'Duplicate opcode: {opcode}')

        if mnemonic in MNEMONIC_TO_OPCODE:
            raise ValueError(f'Duplicate mnemonic: {mnemonic}')

        OPCODE_TO_OPERATION[opcode] = func
        MNEMONIC_TO_OPCODE[mnemonic] = opcode
        return func

    return decorate


@operation(81)
def add(process):
    process.push(process.pop() + process.pop())


@operation(33)
def new(process):
    process.push(process.new())


@operation(164, 'cal')
def call(process):
    address = process.pop()

    process.push(process.registers[IR]) # return address
    process.push(process.registers[FR])

    process.registers[IR] = address - 1
    process.registers[FR] = process.registers[SR]


@operation(9, 'dec')
def decrement(process):
    process.push(process.pop() - 1)


@operation(211, 'del')
def delete(process):
    process.delete(process.pop())


@operation(171, 'den')
def denominator(process):
    process.push(Q(process.pop().denominator))


@operation(223, 'dis')
def discard(process):
    count = process.memory[process.registers[IR]].numerator
    process.registers[SR] -= count


@operation(76, 'div')
def divide(process):
    process.push(process.pop() / process.pop())


@operation(236, 'dup')
def duplicate(process):
    value = process.pop()

    process.push(value)
    process.push(value)


@operation(255, 'hcf')
def halt(process):
    raise TerminatedError()


@operation(143, 'inc')
def increment(process):
    process.push(process.pop() + 1)


@operation(49, 'inv')
def invert(process):
    process.push(1 / process.pop())


@operation(199, 'jmp')
def jump(process):
    process.registers[IR] = process.pop() - 1


@operation(252, 'jeq')
def jump_equal(process):
    address = process.pop()

    if not process.pop():
        process.registers[IR] = address - 1


@operation(1, 'ldi')
def load_integer(process):
    process.push(Q(process.memory[process.registers[IR]].numerator))


@operation(239, 'ldl')
def load_local(process):
    index = process.memory[process.registers[IR]].numerator
    process.push(process.memory[process.registers[FR] + (index - 1)])


@operation(18, 'ldm')
def load_memory(process):
    address = process.pop()
    process.push(process.memory[address])


@operation(241, 'ldp')
def load_parameter(process):
    index = process.memory[process.registers[IR]].numerator
    process.push(process.memory[process.registers[FR] - (index + 2)])


@operation(227, 'ldr')
def load_register(process):
    index = process.memory[process.registers[IR]].numerator
    process.push(process.memory[index - 1])


@operation(214, 'lds')
def load_stream(process):
    handle = process.pop()
    stream = process.streams[handle]

    if not stream:
        raise BlockedError()

    process.push(stream.popleft())


@operation(107, 'mul')
def multiply(process):
    process.push(process.pop() * process.pop())


@operation(147, 'neg')
def negate(process):
    process.push(-process.pop())


@operation(222, 'num')
def numerator(process):
    process.push(Q(process.pop().numerator))


@operation(193, 'ret')
def return_(process):
    process.registers[SR] = process.registers[FR]
    process.registers[FR] = process.pop()
    process.registers[IR] = process.pop()


@operation(251, 'stl')
def store_local(process):
    index = process.memory[process.registers[IR]].numerator
    process.memory[process.registers[FR] + (index - 1)] = process.pop()


@operation(125, 'stm')
def store_memory(process):
    address = process.pop()
    process.memory[address] = process.pop()


@operation(233, 'stp')
def store_parameter(process):
    index = process.memory[process.registers[IR]].numerator
    process.memory[process.registers[FR] - (index + 2)] = process.pop()


@operation(229, 'str')
def store_register(process):
    index = process.memory[process.registers[IR]].numerator
    process.registers[index - 1] = process.pop()


@operation(245, 'sts')
def store_stream(process):
    handle = process.pop()
    stream = process.streams[handle]
    stream.append(process.pop())


@operation(183, 'sub')
def subtract(process):
    process.push(process.pop() - process.pop())


@operation(3, 'swp')
def swap(process):
    a = process.pop()
    b = process.pop()

    process.push(a)
    process.push(b)
