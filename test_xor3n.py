"""
Unit tests for the XOR3N synchronization system.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xor3n import XOR3N, Phase, lcm, lcm_multiple, create_xor3n


class TestLCM(unittest.TestCase):
    """Test LCM calculation utilities."""
    
    def test_lcm_two_numbers(self):
        """Test LCM of two numbers."""
        self.assertEqual(lcm(4, 6), 12)
        self.assertEqual(lcm(2, 3), 6)
        self.assertEqual(lcm(5, 7), 35)
        self.assertEqual(lcm(12, 18), 36)
    
    def test_lcm_multiple_numbers(self):
        """Test LCM of multiple numbers."""
        self.assertEqual(lcm_multiple([2, 3, 5]), 30)
        self.assertEqual(lcm_multiple([4, 6, 8]), 24)
        self.assertEqual(lcm_multiple([3, 5, 7]), 105)
        self.assertEqual(lcm_multiple([2, 4, 8]), 8)


class TestPhase(unittest.TestCase):
    """Test Phase class."""
    
    def test_phase_initialization(self):
        """Test phase initialization."""
        phase = Phase('A', cadence=3, t0=0)
        self.assertEqual(phase.name, 'A')
        self.assertEqual(phase.cadence, 3)
        self.assertEqual(phase.t0, 0)
    
    def test_phase_is_active(self):
        """Test phase activity at different time steps."""
        phase = Phase('A', cadence=3, t0=0)
        self.assertTrue(phase.is_active(0))
        self.assertFalse(phase.is_active(1))
        self.assertFalse(phase.is_active(2))
        self.assertTrue(phase.is_active(3))
        self.assertTrue(phase.is_active(6))
        self.assertTrue(phase.is_active(9))
    
    def test_phase_with_offset(self):
        """Test phase with time offset."""
        phase = Phase('B', cadence=2, t0=1)
        self.assertFalse(phase.is_active(0))
        self.assertTrue(phase.is_active(1))
        self.assertFalse(phase.is_active(2))
        self.assertTrue(phase.is_active(3))
    
    def test_signal_get_set(self):
        """Test signal getting and setting."""
        phase = Phase('A', cadence=2)
        phase.set_signal(0, 1)
        phase.set_signal(1, 0)
        phase.set_signal(2, 1)
        self.assertEqual(phase.get_signal(0), 1)
        self.assertEqual(phase.get_signal(1), 0)
        self.assertEqual(phase.get_signal(2), 1)


class TestXOR3N(unittest.TestCase):
    """Test XOR3N system."""
    
    def test_initialization(self):
        """Test XOR3N initialization."""
        xor3n = XOR3N(2, 3, 5, t0=0)
        self.assertEqual(xor3n.phase_a.cadence, 2)
        self.assertEqual(xor3n.phase_b.cadence, 3)
        self.assertEqual(xor3n.phase_c.cadence, 5)
        self.assertEqual(xor3n.t0, 0)
    
    def test_supercycle_calculation(self):
        """Test supercycle calculation."""
        xor3n = XOR3N(2, 3, 5)
        self.assertEqual(xor3n.supercycle, 30)  # LCM(2, 3, 5) = 30
        
        xor3n2 = XOR3N(4, 6, 8)
        self.assertEqual(xor3n2.supercycle, 24)  # LCM(4, 6, 8) = 24
    
    def test_supercycle_with_offset(self):
        """Test supercycle with time offset."""
        xor3n = XOR3N(2, 3, 5, t0=5)
        self.assertEqual(xor3n.get_supercycle_with_offset(), 35)  # 30 + 5
    
    def test_xor_signals_integers(self):
        """Test XOR operation on integer signals."""
        xor3n = XOR3N(2, 3, 5)
        self.assertEqual(xor3n.xor_signals(0, 0), 0)
        self.assertEqual(xor3n.xor_signals(0, 1), 1)
        self.assertEqual(xor3n.xor_signals(1, 0), 1)
        self.assertEqual(xor3n.xor_signals(1, 1), 0)
        self.assertEqual(xor3n.xor_signals(5, 3), 6)  # 101 XOR 011 = 110
    
    def test_xor_signals_lists(self):
        """Test XOR operation on list signals."""
        xor3n = XOR3N(2, 3, 5)
        result = xor3n.xor_signals([1, 0, 1], [0, 1, 1])
        self.assertEqual(result, [1, 1, 0])
    
    def test_compute_xor_training(self):
        """Test XOR training computation."""
        xor3n = XOR3N(2, 3, 5)
        
        # Set signals at time t=0
        xor3n.phase_a.set_signal(0, 1)
        xor3n.phase_b.set_signal(0, 0)
        xor3n.phase_c.set_signal(0, 1)
        
        # Compute training
        train_a, train_b, train_c = xor3n.compute_xor_training(0)
        
        # A should train on B XOR C = 0 XOR 1 = 1
        self.assertEqual(train_a, 1)
        # B should train on A XOR C = 1 XOR 1 = 0
        self.assertEqual(train_b, 0)
        # C should train on A XOR B = 1 XOR 0 = 1
        self.assertEqual(train_c, 1)
    
    def test_step(self):
        """Test single step execution."""
        xor3n = XOR3N(2, 3, 5)
        xor3n.step(0, signal_a=1, signal_b=0, signal_c=1)
        
        self.assertEqual(xor3n.phase_a.get_signal(0), 1)
        self.assertEqual(xor3n.phase_b.get_signal(0), 0)
        self.assertEqual(xor3n.phase_c.get_signal(0), 1)
        
        # Check training signals were computed
        self.assertEqual(xor3n.phase_a.training_history[0], 1)  # 0 XOR 1
        self.assertEqual(xor3n.phase_b.training_history[0], 0)  # 1 XOR 1
        self.assertEqual(xor3n.phase_c.training_history[0], 1)  # 1 XOR 0
    
    def test_get_active_phases(self):
        """Test getting active phases at different times."""
        xor3n = XOR3N(2, 3, 5)
        
        # At t=0: all phases active (0 % n == 0 for all n)
        active_t0 = xor3n.get_active_phases(0)
        self.assertEqual(len(active_t0), 3)
        
        # At t=1: none active
        active_t1 = xor3n.get_active_phases(1)
        self.assertEqual(len(active_t1), 0)
        
        # At t=2: only A active (cadence 2)
        active_t2 = xor3n.get_active_phases(2)
        self.assertEqual(len(active_t2), 1)
        self.assertEqual(active_t2[0].name, 'A')
        
        # At t=6: A and B active (2 and 3 divide 6)
        active_t6 = xor3n.get_active_phases(6)
        self.assertEqual(len(active_t6), 2)
        active_names = {p.name for p in active_t6}
        self.assertEqual(active_names, {'A', 'B'})
    
    def test_get_schedule(self):
        """Test schedule generation."""
        xor3n = XOR3N(2, 3, 5)
        schedule = xor3n.get_schedule(10)
        
        self.assertEqual(len(schedule), 10)
        self.assertEqual(schedule[0][0], 0)
        self.assertEqual(set(schedule[0][1]), {'A', 'B', 'C'})  # All active at t=0
        self.assertEqual(schedule[1][1], [])  # None active at t=1
        self.assertEqual(schedule[2][1], ['A'])  # Only A at t=2
    
    def test_run_cycle(self):
        """Test running multiple cycles."""
        xor3n = XOR3N(2, 3, 5)
        
        # Simple signal generator
        def signal_gen(t, phase):
            return t % 2  # Alternating 0, 1, 0, 1...
        
        xor3n.run_cycle(10, signal_gen)
        
        # Check that signals were set
        self.assertGreater(len(xor3n.phase_a.signal_history), 0)
        self.assertGreater(len(xor3n.phase_b.signal_history), 0)
        self.assertGreater(len(xor3n.phase_c.signal_history), 0)
    
    def test_analyze_novelty_filter(self):
        """Test novelty filter analysis."""
        xor3n = XOR3N(2, 3, 5)
        analysis = xor3n.analyze_novelty_filter(30)
        
        self.assertEqual(analysis['supercycle'], 30)
        self.assertEqual(analysis['cadences']['A'], 2)
        self.assertEqual(analysis['cadences']['B'], 3)
        self.assertEqual(analysis['cadences']['C'], 5)
        
        # Check active counts (how many times each phase activates in 30 steps)
        self.assertEqual(analysis['active_counts']['A'], 15)  # 30/2
        self.assertEqual(analysis['active_counts']['B'], 10)  # 30/3
        self.assertEqual(analysis['active_counts']['C'], 6)   # 30/5
    
    def test_factory_function(self):
        """Test create_xor3n factory function."""
        xor3n = create_xor3n()
        self.assertEqual(xor3n.phase_a.cadence, 2)
        self.assertEqual(xor3n.phase_b.cadence, 3)
        self.assertEqual(xor3n.phase_c.cadence, 5)
        self.assertEqual(xor3n.supercycle, 30)
        
        xor3n_custom = create_xor3n(4, 6, 10, t0=2)
        self.assertEqual(xor3n_custom.supercycle, 60)
        self.assertEqual(xor3n_custom.t0, 2)


class TestNoveltyFilterBehavior(unittest.TestCase):
    """Test the high-pass/novelty filter behavior."""
    
    def test_persistent_signal_cancellation(self):
        """Test that persistent common signals get cancelled by XOR."""
        xor3n = XOR3N(2, 3, 5)
        
        # All phases have the same persistent signal (1)
        xor3n.step(0, signal_a=1, signal_b=1, signal_c=1)
        
        # XOR of identical signals should be 0 (cancelled)
        # A trains on B XOR C = 1 XOR 1 = 0
        self.assertEqual(xor3n.phase_a.training_history[0], 0)
        # B trains on A XOR C = 1 XOR 1 = 0
        self.assertEqual(xor3n.phase_b.training_history[0], 0)
        # C trains on A XOR B = 1 XOR 1 = 0
        self.assertEqual(xor3n.phase_c.training_history[0], 0)
    
    def test_phase_specific_signal_emphasis(self):
        """Test that phase-specific signals are emphasized."""
        xor3n = XOR3N(2, 3, 5)
        
        # Only phase A has signal, others are 0
        xor3n.step(0, signal_a=1, signal_b=0, signal_c=0)
        
        # A trains on B XOR C = 0 XOR 0 = 0 (no novelty from others)
        self.assertEqual(xor3n.phase_a.training_history[0], 0)
        # B trains on A XOR C = 1 XOR 0 = 1 (novelty detected!)
        self.assertEqual(xor3n.phase_b.training_history[0], 1)
        # C trains on A XOR B = 1 XOR 0 = 1 (novelty detected!)
        self.assertEqual(xor3n.phase_c.training_history[0], 1)
    
    def test_fluctuating_pattern_detection(self):
        """Test detection of fluctuating patterns."""
        xor3n = XOR3N(2, 3, 5)
        
        # Different signals create fluctuation
        xor3n.step(0, signal_a=1, signal_b=0, signal_c=1)
        
        # Training signals will reflect the differences
        self.assertEqual(xor3n.phase_a.training_history[0], 1)  # 0 XOR 1 = 1
        self.assertEqual(xor3n.phase_b.training_history[0], 0)  # 1 XOR 1 = 0
        self.assertEqual(xor3n.phase_c.training_history[0], 1)  # 1 XOR 0 = 1


if __name__ == '__main__':
    unittest.main()
