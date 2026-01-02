"""
XOR3N: Three-Phase Synchronization with LCM Alignment

A sophisticated synchronization system implementing three-phase periodic scheduling
with XOR-of-the-other-2 training over a hypergraph structure.
"""

from .xor3n import (
    XOR3N,
    Phase,
    lcm,
    lcm_multiple,
    create_xor3n
)

__version__ = '1.0.0'
__all__ = [
    'XOR3N',
    'Phase',
    'lcm',
    'lcm_multiple',
    'create_xor3n'
]
