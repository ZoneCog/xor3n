#!/usr/bin/env python3
"""
Quick demo script showing XOR3N in action.
Run this to see the key features of the system.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xor3n import create_xor3n


def main():
    print("=" * 70)
    print("XOR3N: Three-Phase Synchronization with LCM Alignment")
    print("=" * 70)
    print()
    
    # Create the system
    print("Creating XOR3N system with cadences (2, 3, 5)...")
    xor3n = create_xor3n(cadence_a=2, cadence_b=3, cadence_c=5)
    print(f"✓ Supercycle calculated: T = LCM(2, 3, 5) = {xor3n.supercycle}")
    print()
    
    # Show the key concept
    print("KEY CONCEPT: XOR-of-the-Other-2 Training")
    print("-" * 70)
    print("Each phase trains on the XOR of the other two:")
    print("  • Phase A learns from: B XOR C")
    print("  • Phase B learns from: A XOR C")
    print("  • Phase C learns from: A XOR B")
    print()
    
    # Demonstrate novelty detection
    print("DEMO: High-Pass / Novelty Filter Behavior")
    print("-" * 70)
    
    print("\n1. Persistent signal (all phases = 1):")
    xor3n.step(0, signal_a=1, signal_b=1, signal_c=1)
    train_a, train_b, train_c = (xor3n.phase_a.training_history[0], 
                                   xor3n.phase_b.training_history[0],
                                   xor3n.phase_c.training_history[0])
    print(f"   Signals: A=1, B=1, C=1")
    print(f"   Training: A={train_a}, B={train_b}, C={train_c}")
    print(f"   ➜ Common signal CANCELLED (all zeros)")
    
    print("\n2. Phase-specific signal (only A = 1):")
    xor3n.step(1, signal_a=1, signal_b=0, signal_c=0)
    train_a, train_b, train_c = (xor3n.phase_a.training_history[1], 
                                   xor3n.phase_b.training_history[1],
                                   xor3n.phase_c.training_history[1])
    print(f"   Signals: A=1, B=0, C=0")
    print(f"   Training: A={train_a}, B={train_b}, C={train_c}")
    print(f"   ➜ Novelty DETECTED by B and C!")
    
    print("\n3. Mixed signals (A=1, B=0, C=1):")
    xor3n.step(2, signal_a=1, signal_b=0, signal_c=1)
    train_a, train_b, train_c = (xor3n.phase_a.training_history[2], 
                                   xor3n.phase_b.training_history[2],
                                   xor3n.phase_c.training_history[2])
    print(f"   Signals: A=1, B=0, C=1")
    print(f"   Training: A={train_a}, B={train_b}, C={train_c}")
    print(f"   ➜ Different novelty patterns per phase")
    
    # Show schedule
    print("\n" + "=" * 70)
    print("Phase Activation Schedule (first 15 steps):")
    print("-" * 70)
    schedule = xor3n.get_schedule(15)
    for t, active in schedule:
        active_str = ", ".join(active) if active else "none"
        markers = ""
        if 'A' in active: markers += "●"
        else: markers += "○"
        if 'B' in active: markers += "●"
        else: markers += "○"
        if 'C' in active: markers += "●"
        else: markers += "○"
        print(f"  t={t:2d}: [{markers}]  {active_str}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("-" * 70)
    analysis = xor3n.analyze_novelty_filter(30)
    print(f"• Supercycle repeats every {analysis['supercycle']} steps")
    print(f"• Phase A activates {analysis['active_counts']['A']} times per supercycle")
    print(f"• Phase B activates {analysis['active_counts']['B']} times per supercycle")
    print(f"• Phase C activates {analysis['active_counts']['C']} times per supercycle")
    print()
    print("The XOR training creates a HIGH-PASS / NOVELTY FILTER:")
    print("  ✓ Persistent patterns (common across phases) → CANCELLED")
    print("  ✓ Fluctuating patterns (phase-specific) → EMPHASIZED")
    print()
    print("=" * 70)
    print("For more examples, run: python examples.py")
    print("For visualization, run: python visualize.py")
    print("=" * 70)


if __name__ == '__main__':
    main()
