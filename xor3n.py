"""
XOR3N: Three-Phase Synchronization with LCM Alignment

This module implements a three-phase synchronization system where each phase
trains on the XOR of the other two phases, creating a high-pass/novelty filter
effect over a hypergraph structure with periodic scheduling based on LCM cadences.
"""

import math
from typing import List, Tuple, Callable, Any
from functools import reduce


def lcm(a: int, b: int) -> int:
    """Calculate the Least Common Multiple of two integers."""
    return abs(a * b) // math.gcd(a, b)


def lcm_multiple(numbers: List[int]) -> int:
    """Calculate the LCM of multiple integers."""
    return reduce(lcm, numbers)


class Phase:
    """Represents a single phase in the XOR3N system."""
    
    def __init__(self, name: str, cadence: int, t0: int = 0):
        """
        Initialize a phase.
        
        Args:
            name: Phase identifier (e.g., 'A', 'B', 'C')
            cadence: The cadence/period for this phase (i, j, or k)
            t0: Initial time offset
        """
        self.name = name
        self.cadence = cadence
        self.t0 = t0
        self.signal_history: List[Any] = []
        self.training_history: List[Any] = []
    
    def is_active(self, t: int) -> bool:
        """Check if this phase is active at time t."""
        return (t - self.t0) % self.cadence == 0
    
    def get_signal(self, t: int) -> Any:
        """Get the signal value at time t."""
        if len(self.signal_history) > t:
            return self.signal_history[t]
        return 0
    
    def set_signal(self, t: int, value: Any):
        """Set the signal value at time t."""
        while len(self.signal_history) <= t:
            self.signal_history.append(0)
        self.signal_history[t] = value
    
    def record_training(self, t: int, value: Any):
        """Record a training value at time t."""
        while len(self.training_history) <= t:
            self.training_history.append(None)
        self.training_history[t] = value


class XOR3N:
    """
    Three-phase synchronization system with XOR-of-the-other-2 training.
    
    This implements a periodic scheduler over a hypergraph where:
    - Each phase has its own cadence (i, j, k)
    - Supercycle T = LCM(i, j, k) + t0
    - Each phase trains on XOR of the other two: A ← (B XOR C), etc.
    - Creates a high-pass/novelty filter effect
    """
    
    def __init__(self, cadence_a: int, cadence_b: int, cadence_c: int, t0: int = 0):
        """
        Initialize the XOR3N system.
        
        Args:
            cadence_a: Cadence for phase A (index i)
            cadence_b: Cadence for phase B (index j)
            cadence_c: Cadence for phase C (index k)
            t0: Initial time offset for the supercycle
        """
        self.phase_a = Phase('A', cadence_a, t0)
        self.phase_b = Phase('B', cadence_b, t0)
        self.phase_c = Phase('C', cadence_c, t0)
        self.phases = [self.phase_a, self.phase_b, self.phase_c]
        self.t0 = t0
        self.supercycle = self._calculate_supercycle()
    
    def _calculate_supercycle(self) -> int:
        """Calculate the supercycle T = LCM(i, j, k)."""
        cadences = [p.cadence for p in self.phases]
        return lcm_multiple(cadences)
    
    def get_supercycle_with_offset(self) -> int:
        """Get the full supercycle period including offset: T = LCM(i,j,k) + t0."""
        return self.supercycle + self.t0
    
    def xor_signals(self, signal1: Any, signal2: Any) -> Any:
        """
        Perform XOR operation on two signals.
        
        For numeric signals, uses bitwise XOR.
        Can be extended for other signal types.
        """
        if isinstance(signal1, (int, bool)) and isinstance(signal2, (int, bool)):
            return int(signal1) ^ int(signal2)
        elif isinstance(signal1, (list, tuple)) and isinstance(signal2, (list, tuple)):
            # Element-wise XOR for sequences
            return [self.xor_signals(s1, s2) for s1, s2 in zip(signal1, signal2)]
        else:
            # For other types, convert to int and XOR
            return int(signal1) ^ int(signal2)
    
    def compute_xor_training(self, t: int):
        """
        Compute XOR-of-the-other-2 training signals for all phases at time t.
        
        Training signals:
        - A trains on: B(t) XOR C(t)
        - B trains on: A(t) XOR C(t)
        - C trains on: A(t) XOR B(t)
        """
        # Get current signals from all phases
        a_t = self.phase_a.get_signal(t)
        b_t = self.phase_b.get_signal(t)
        c_t = self.phase_c.get_signal(t)
        
        # Compute XOR training signals
        train_a = self.xor_signals(b_t, c_t)  # A ← (B XOR C)
        train_b = self.xor_signals(a_t, c_t)  # B ← (A XOR C)
        train_c = self.xor_signals(a_t, b_t)  # C ← (A XOR B)
        
        # Record training signals
        self.phase_a.record_training(t, train_a)
        self.phase_b.record_training(t, train_b)
        self.phase_c.record_training(t, train_c)
        
        return train_a, train_b, train_c
    
    def step(self, t: int, signal_a: Any = None, signal_b: Any = None, signal_c: Any = None):
        """
        Execute one step of the XOR3N system at time t.
        
        Args:
            t: Current time step
            signal_a: Input signal for phase A (if active)
            signal_b: Input signal for phase B (if active)
            signal_c: Input signal for phase C (if active)
        """
        # Set signals for active phases
        if signal_a is not None:
            self.phase_a.set_signal(t, signal_a)
        if signal_b is not None:
            self.phase_b.set_signal(t, signal_b)
        if signal_c is not None:
            self.phase_c.set_signal(t, signal_c)
        
        # Compute XOR training for all phases
        self.compute_xor_training(t)
    
    def run_cycle(self, num_steps: int, signal_generator: Callable[[int, str], Any] = None):
        """
        Run the XOR3N system for a number of time steps.
        
        Args:
            num_steps: Number of time steps to simulate
            signal_generator: Optional function(t, phase_name) -> signal value
        """
        for t in range(num_steps):
            # Generate or get signals for each phase
            if signal_generator:
                sig_a = signal_generator(t, 'A') if self.phase_a.is_active(t) else self.phase_a.get_signal(t)
                sig_b = signal_generator(t, 'B') if self.phase_b.is_active(t) else self.phase_b.get_signal(t)
                sig_c = signal_generator(t, 'C') if self.phase_c.is_active(t) else self.phase_c.get_signal(t)
            else:
                sig_a = self.phase_a.get_signal(t)
                sig_b = self.phase_b.get_signal(t)
                sig_c = self.phase_c.get_signal(t)
            
            self.step(t, sig_a, sig_b, sig_c)
    
    def get_active_phases(self, t: int) -> List[Phase]:
        """Get list of phases that are active at time t."""
        return [phase for phase in self.phases if phase.is_active(t)]
    
    def get_schedule(self, num_steps: int) -> List[Tuple[int, List[str]]]:
        """
        Get the periodic schedule showing which phases are active at each time step.
        
        Args:
            num_steps: Number of time steps to generate schedule for
            
        Returns:
            List of (time, active_phase_names) tuples
        """
        schedule = []
        for t in range(num_steps):
            active = [phase.name for phase in self.get_active_phases(t)]
            schedule.append((t, active))
        return schedule
    
    def analyze_novelty_filter(self, num_steps: int) -> dict:
        """
        Analyze the high-pass/novelty filter behavior.
        
        Returns statistics about:
        - Persistent patterns (cancelled by XOR)
        - Fluctuating patterns (emphasized by XOR)
        """
        analysis = {
            'supercycle': self.supercycle,
            'cadences': {
                'A': self.phase_a.cadence,
                'B': self.phase_b.cadence,
                'C': self.phase_c.cadence
            },
            'active_counts': {
                'A': sum(1 for t in range(num_steps) if self.phase_a.is_active(t)),
                'B': sum(1 for t in range(num_steps) if self.phase_b.is_active(t)),
                'C': sum(1 for t in range(num_steps) if self.phase_c.is_active(t))
            },
            'schedule_pattern': self.get_schedule(min(num_steps, self.supercycle))
        }
        return analysis


def create_xor3n(cadence_a: int = 2, cadence_b: int = 3, cadence_c: int = 5, t0: int = 0) -> XOR3N:
    """
    Factory function to create an XOR3N system with specified cadences.
    
    Default cadences (2, 3, 5) create an interesting pattern with LCM = 30.
    
    Args:
        cadence_a: Cadence for phase A
        cadence_b: Cadence for phase B  
        cadence_c: Cadence for phase C
        t0: Initial time offset
        
    Returns:
        Configured XOR3N instance
    """
    return XOR3N(cadence_a, cadence_b, cadence_c, t0)
