from typing import List, Tuple

from amaranth import Signal, Module, Elaboratable
from amaranth.asserts import Assert, Cover

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util import main


class GoL3x3(Elaboratable):
    def __init__(self):
        self.in_cells = Signal(9)
        self.out_state = Signal()

    def elaborate(self, _) -> Module:
        m = Module()

        neighbors = Signal(9)
        middle = self.in_cells[4]

        m.d.comb += neighbors.eq(self.in_cells[0] +
                                 self.in_cells[1] +
                                 self.in_cells[2] +
                                 self.in_cells[3] +
                                 self.in_cells[5] +
                                 self.in_cells[6] +
                                 self.in_cells[7] +
                                 self.in_cells[8]
                                 )

        m.d.comb += self.out_state.eq(0)

        with m.If(middle & ((neighbors == 2) | (neighbors == 3))):
            m.d.comb += self.out_state.eq(1)

        with m.If(~middle & (neighbors == 3)):
            m.d.comb += self.out_state.eq(1)

        return m

    @classmethod
    def formal(cls) -> Tuple[Module, List[Signal]]:
        m = Module()
        m.submodules.dut = dut = cls()

        s = 0
        for n in range(9):
            if n != 4:
                s += dut.in_cells[n]

        with m.If(s == 3):
            m.d.comb += Assert(dut.out_state)
        with m.If(s == 2):
            m.d.comb += Assert(dut.out_state == dut.in_cells[4])

        return m, [dut.in_cells]


class GoL4x4(Elaboratable):
    def __init__(self):
        self.in_cells = Signal(16)
        self.out_state = Signal(4)

    def elaborate(self, _) -> Module:
        m = Module()

        tl = GoL3x3()
        m.d.comb += [
            tl.in_cells[0:].eq(self.in_cells[0:3]),
            tl.in_cells[3:].eq(self.in_cells[4:7]),
            tl.in_cells[6:].eq(self.in_cells[8:11]),
        ]
        tr = GoL3x3()
        m.d.comb += [
            tr.in_cells[0:].eq(self.in_cells[1:4]),
            tr.in_cells[3:].eq(self.in_cells[5:8]),
            tr.in_cells[6:].eq(self.in_cells[9:12]),
        ]
        bl = GoL3x3()
        m.d.comb += [
            bl.in_cells[0:].eq(self.in_cells[4:7]),
            bl.in_cells[3:].eq(self.in_cells[8:11]),
            bl.in_cells[6:].eq(self.in_cells[12:15]),
        ]
        br = GoL3x3()
        m.d.comb += [
            br.in_cells[0:].eq(self.in_cells[5:8]),
            br.in_cells[3:].eq(self.in_cells[9:12]),
            br.in_cells[6:].eq(self.in_cells[13:]),
        ]

        m.submodules += [tr, tl, br, bl]

        m.d.comb += [
            self.out_state[0].eq(tl.out_state),
            self.out_state[1].eq(tr.out_state),
            self.out_state[2].eq(bl.out_state),
            self.out_state[3].eq(br.out_state),
        ]

        return m

    @classmethod
    def formal(cls) -> Tuple[Module, List[Signal]]:
        m = Module()
        m.submodules.dut = dut = cls()

        m.d.comb += Cover(
            (dut.in_cells[5] == dut.out_state[0]) &
            (dut.in_cells[6] == dut.out_state[1]) &
            (dut.in_cells[9] == dut.out_state[2]) &
            (dut.in_cells[10] == dut.out_state[3]) &
            (dut.out_state > 0)
        )

        with m.If((dut.out_state.all()) &
                  (dut.in_cells[5:7].all()) &
                  (dut.in_cells[9:11].all())):
            m.d.comb += Assert(~dut.in_cells[0:5].all() &
                               ~dut.in_cells[11:16] &
                               ~dut.in_cells[7] &
                               ~dut.in_cells[8]
                               )
        return m, [dut.in_cells]


if __name__ == "__main__":
    # main(GoL3x3)
    main(GoL4x4)
