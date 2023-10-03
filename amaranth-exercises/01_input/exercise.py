from typing import List, Tuple

from amaranth import Signal, Module, Elaboratable
from amaranth.asserts import Cover

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util import main


class PennyCounter(Elaboratable):
    def __init__(self):
        self.in_pennies = Signal(8)
        self.in_nickels = Signal(4)
        self.in_dimes = Signal(4)
        self.in_quarters = Signal(4)
        self.in_dollars = Signal(4)

        self.out_pennies = Signal(12)

    def elaborate(self, _) -> Module:
        m = Module()

        m.d.comb += self.out_pennies.eq(self.in_pennies +
                                        self.in_nickels * 5 +
                                        self.in_dimes * 10 +
                                        self.in_quarters * 25 +
                                        self.in_dollars * 100)
        return m

    @classmethod
    def formal(cls) -> Tuple[Module, List[Signal]]:
        m = Module()
        m.submodules.dut = dut = cls()

        # Cover the case where the inputs are: 37 pennies, 3 nickels, 10 dimes, 5 quarters, and 2 dollars.
        m.d.comb += Cover((dut.in_pennies == 37) &
                          (dut.in_nickels == 3) &
                          (dut.in_dimes == 10) &
                          (dut.in_quarters == 5) &
                          (dut.in_dollars == 2))

        # Cover the case where the output is 548 pennies.
        m.d.comb += Cover(dut.out_pennies == 548)

        # Cover the case where the output is 64 pennies, and there are twice as many nickels as there are dimes, and there is at least one dime.
        m.d.comb += Cover((dut.out_pennies == 64) &
                          (dut.in_nickels == dut.in_dimes * 2) &
                          (dut.in_dimes > 0)
                          )

        # Prove that if there are no input pennies, then the number of output pennies is always a multiple of 5.
        m.d.comb += Cover((dut.in_pennies == 0) & (dut.out_pennies % 5 == 0))

        # Prove that the number of output pennies, modulo 5, will always equal the number of input pennies, modulo 5, regardless of the other inputs.
        m.d.comb += Cover((dut.out_pennies % 5) == (dut.in_pennies % 5))

        return m, [
            dut.in_pennies,
            dut.in_nickels,
            dut.in_dimes,
            dut.in_quarters,
            dut.in_dollars,
        ]


if __name__ == "__main__":
    main(PennyCounter)
