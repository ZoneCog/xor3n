"""
Example demonstrations of the XOR3N synchronization system.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xor3n import XOR3N, create_xor3n


def demo_basic_usage():
    """Demonstrate basic XOR3N usage."""
    print("=" * 60)
    print("DEMO 1: Basic XOR3N Usage")
    print("=" * 60)
    
    # Create XOR3N system with cadences 2, 3, 5
    xor3n = create_xor3n(cadence_a=2, cadence_b=3, cadence_c=5)
    
    print(f"\nPhase cadences:")
    print(f"  Phase A: {xor3n.phase_a.cadence}")
    print(f"  Phase B: {xor3n.phase_b.cadence}")
    print(f"  Phase C: {xor3n.phase_c.cadence}")
    print(f"\nSupercycle T = LCM(2, 3, 5) = {xor3n.supercycle}")
    
    # Show schedule for one supercycle
    print(f"\nPhase schedule over one supercycle:")
    schedule = xor3n.get_schedule(xor3n.supercycle)
    for t, active in schedule[:15]:  # Show first 15 steps
        active_str = ", ".join(active) if active else "none"
        print(f"  t={t:2d}: {active_str}")
    print("  ...")
    
    print()


def demo_xor_training():
    """Demonstrate XOR-of-the-other-2 training."""
    print("=" * 60)
    print("DEMO 2: XOR-of-the-Other-2 Training")
    print("=" * 60)
    
    xor3n = create_xor3n()
    
    print("\nScenario 1: All phases have same signal (1, 1, 1)")
    print("  → Persistent/common signal gets CANCELLED")
    xor3n.step(0, signal_a=1, signal_b=1, signal_c=1)
    print(f"  Training signals: A={xor3n.phase_a.training_history[0]}, "
          f"B={xor3n.phase_b.training_history[0]}, "
          f"C={xor3n.phase_c.training_history[0]}")
    print("  → All zeros! Common signal is filtered out.")
    
    print("\nScenario 2: Phase-specific signal (1, 0, 0)")
    print("  → Unique/fluctuating signal is EMPHASIZED")
    xor3n.step(1, signal_a=1, signal_b=0, signal_c=0)
    print(f"  Training signals: A={xor3n.phase_a.training_history[1]}, "
          f"B={xor3n.phase_b.training_history[1]}, "
          f"C={xor3n.phase_c.training_history[1]}")
    print("  → B and C detect novelty in A!")
    
    print("\nScenario 3: Mixed signals (1, 0, 1)")
    xor3n.step(2, signal_a=1, signal_b=0, signal_c=1)
    print(f"  Training signals: A={xor3n.phase_a.training_history[2]}, "
          f"B={xor3n.phase_b.training_history[2]}, "
          f"C={xor3n.phase_c.training_history[2]}")
    print("  → Each phase sees different novelty patterns")
    
    print()


def demo_high_pass_filter():
    """Demonstrate high-pass/novelty filter behavior."""
    print("=" * 60)
    print("DEMO 3: High-Pass/Novelty Filter Effect")
    print("=" * 60)
    
    xor3n = create_xor3n(cadence_a=2, cadence_b=3, cadence_c=5)
    
    print("\nSimulating signal patterns over time...")
    
    # Simulate with alternating pattern
    for t in range(10):
        # Create a pattern where phases alternate
        sig_a = t % 2
        sig_b = (t + 1) % 2
        sig_c = t % 2
        
        xor3n.step(t, signal_a=sig_a, signal_b=sig_b, signal_c=sig_c)
    
    print("\nTime step analysis:")
    print("t  | A_sig | B_sig | C_sig | A_train | B_train | C_train")
    print("---|-------|-------|-------|---------|---------|--------")
    for t in range(10):
        a_sig = xor3n.phase_a.get_signal(t)
        b_sig = xor3n.phase_b.get_signal(t)
        c_sig = xor3n.phase_c.get_signal(t)
        a_train = xor3n.phase_a.training_history[t]
        b_train = xor3n.phase_b.training_history[t]
        c_train = xor3n.phase_c.training_history[t]
        print(f"{t:2d} |   {a_sig}   |   {b_sig}   |   {c_sig}   |    {a_train}    |    {b_train}    |    {c_train}")
    
    print("\nNote: Training signals highlight differences (high-pass filter)")
    print("      When A=C, their common pattern is filtered from B's training")
    print()


def demo_supercycle_analysis():
    """Demonstrate supercycle analysis."""
    print("=" * 60)
    print("DEMO 4: Supercycle Analysis")
    print("=" * 60)
    
    # Test different cadence combinations
    test_cases = [
        (2, 3, 5),
        (3, 4, 6),
        (2, 4, 8),
        (7, 11, 13)
    ]
    
    print("\nComparing different cadence patterns:\n")
    for a, b, c in test_cases:
        xor3n = create_xor3n(cadence_a=a, cadence_b=b, cadence_c=c)
        analysis = xor3n.analyze_novelty_filter(xor3n.supercycle)
        
        print(f"Cadences ({a}, {b}, {c}):")
        print(f"  Supercycle: {analysis['supercycle']}")
        print(f"  Phase A activates {analysis['active_counts']['A']} times")
        print(f"  Phase B activates {analysis['active_counts']['B']} times")
        print(f"  Phase C activates {analysis['active_counts']['C']} times")
        
        # Calculate synchronization points (all phases active)
        sync_points = sum(1 for t, active in analysis['schedule_pattern'] 
                         if len(active) == 3)
        print(f"  Full synchronization points: {sync_points}")
        print()


def demo_hypergraph_scheduling():
    """Demonstrate periodic hypergraph scheduling."""
    print("=" * 60)
    print("DEMO 5: Hypergraph Periodic Scheduling")
    print("=" * 60)
    
    xor3n = create_xor3n(cadence_a=2, cadence_b=3, cadence_c=5, t0=0)
    
    print(f"\nSupercycle T = LCM(2, 3, 5) + t0 = {xor3n.supercycle} + {xor3n.t0} "
          f"= {xor3n.get_supercycle_with_offset()}")
    
    print("\nHypergraph node activation patterns:")
    print("(Showing which bundles/layers are active at each time)")
    
    schedule = xor3n.get_schedule(30)
    
    # Group by activation pattern
    patterns = {}
    for t, active in schedule:
        pattern = tuple(sorted(active))
        if pattern not in patterns:
            patterns[pattern] = []
        patterns[pattern].append(t)
    
    print("\nActivation patterns:")
    for pattern, times in sorted(patterns.items()):
        if not pattern:
            pattern_str = "∅ (none)"
        else:
            pattern_str = "{" + ", ".join(pattern) + "}"
        times_str = ", ".join(str(t) for t in times[:5])
        if len(times) > 5:
            times_str += f", ... ({len(times)} total)"
        print(f"  {pattern_str:12s}: t = {times_str}")
    
    print("\nThis creates a periodic hypergraph structure where edges")
    print("connect nodes based on temporal synchronization patterns.")
    print()


def main():
    """Run all demonstrations."""
    demo_basic_usage()
    demo_xor_training()
    demo_high_pass_filter()
    demo_supercycle_analysis()
    demo_hypergraph_scheduling()
    
    print("=" * 60)
    print("All demonstrations complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
