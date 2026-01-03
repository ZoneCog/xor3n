"""
Visualization utilities for XOR3N system.
Generates text-based visualizations of phase schedules and training signals.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xor3n import create_xor3n


def visualize_schedule(xor3n, num_steps=None):
    """
    Create a visual timeline of phase activations.
    
    Args:
        xor3n: XOR3N instance
        num_steps: Number of steps to visualize (default: one supercycle)
    """
    if num_steps is None:
        num_steps = xor3n.supercycle
    
    print(f"\nPhase Activation Timeline (Supercycle = {xor3n.supercycle})")
    print("=" * 70)
    
    schedule = xor3n.get_schedule(num_steps)
    
    # Print header
    print("Time | Phase A | Phase B | Phase C | Active")
    print("-----|---------|---------|---------|" + "-" * 20)
    
    for t, active in schedule:
        a_mark = "   ●   " if 'A' in active else "   ○   "
        b_mark = "   ●   " if 'B' in active else "   ○   "
        c_mark = "   ●   " if 'C' in active else "   ○   "
        active_str = ", ".join(active) if active else "none"
        print(f" {t:3d} | {a_mark} | {b_mark} | {c_mark} | {active_str}")


def visualize_xor_training(xor3n, num_steps=15):
    """
    Visualize XOR training over time with actual signals.
    
    Args:
        xor3n: XOR3N instance (should have been run with signals)
        num_steps: Number of steps to visualize
    """
    print(f"\nXOR Training Visualization")
    print("=" * 90)
    print("Shows how each phase trains on XOR of the other two")
    print()
    
    print("Time | A_sig | B_sig | C_sig | A_train(B⊕C) | B_train(A⊕C) | C_train(A⊕B) | Filter Effect")
    print("-----|-------|-------|-------|--------------|--------------|--------------|" + "-" * 20)
    
    for t in range(min(num_steps, len(xor3n.phase_a.signal_history))):
        a_sig = xor3n.phase_a.get_signal(t)
        b_sig = xor3n.phase_b.get_signal(t)
        c_sig = xor3n.phase_c.get_signal(t)
        
        if t < len(xor3n.phase_a.training_history):
            a_train = xor3n.phase_a.training_history[t]
            b_train = xor3n.phase_b.training_history[t]
            c_train = xor3n.phase_c.training_history[t]
            
            # Analyze filter effect
            if a_sig == b_sig == c_sig:
                effect = "Common → Cancelled"
            elif a_train or b_train or c_train:
                effect = "Novelty detected!"
            else:
                effect = "Low novelty"
            
            print(f" {t:3d} |   {a_sig}   |   {b_sig}   |   {c_sig}   |      {a_train}       |      {b_train}       |      {c_train}       | {effect}")


def visualize_hypergraph_structure(xor3n, num_steps=None):
    """
    Visualize the hypergraph structure of phase synchronizations.
    
    Args:
        xor3n: XOR3N instance
        num_steps: Number of steps to analyze (default: one supercycle)
    """
    if num_steps is None:
        num_steps = xor3n.supercycle
    
    print(f"\nHypergraph Structure (Supercycle = {xor3n.supercycle})")
    print("=" * 70)
    print("Hyperedges connect phases that are active simultaneously")
    print()
    
    schedule = xor3n.get_schedule(num_steps)
    
    # Group by hyperedge pattern
    hyperedges = {}
    for t, active in schedule:
        if active:  # Skip empty sets
            edge = tuple(sorted(active))
            if edge not in hyperedges:
                hyperedges[edge] = []
            hyperedges[edge].append(t)
    
    print(f"Found {len(hyperedges)} distinct hyperedge patterns:\n")
    
    for edge, times in sorted(hyperedges.items(), key=lambda x: len(x[0]), reverse=True):
        edge_str = "{" + ", ".join(edge) + "}"
        count = len(times)
        freq = count / num_steps * 100
        
        # Show first few occurrences
        times_str = ", ".join(str(t) for t in times[:5])
        if count > 5:
            times_str += f", ... ({count} total)"
        
        print(f"  Hyperedge {edge_str:12s}: occurs {count:3d} times ({freq:5.1f}%)")
        print(f"    Times: t = {times_str}")
        print()


def create_demo_visualization():
    """Create a comprehensive demonstration visualization."""
    print("\n" + "=" * 70)
    print("XOR3N SYSTEM VISUALIZATION DEMO")
    print("=" * 70)
    
    # Create system with interesting cadences
    xor3n = create_xor3n(cadence_a=2, cadence_b=3, cadence_c=5)
    
    print(f"\nSystem Configuration:")
    print(f"  Phase A cadence: {xor3n.phase_a.cadence}")
    print(f"  Phase B cadence: {xor3n.phase_b.cadence}")
    print(f"  Phase C cadence: {xor3n.phase_c.cadence}")
    print(f"  Supercycle: T = LCM({xor3n.phase_a.cadence}, {xor3n.phase_b.cadence}, {xor3n.phase_c.cadence}) = {xor3n.supercycle}")
    
    # Visualize schedule
    visualize_schedule(xor3n, num_steps=20)
    
    # Run with signals and visualize training
    print("\n")
    def signal_gen(t, phase):
        # Create interesting pattern
        if phase == 'A':
            return t % 2
        elif phase == 'B':
            return (t + 1) % 2
        else:
            return t % 2
    
    xor3n.run_cycle(15, signal_gen)
    visualize_xor_training(xor3n, num_steps=15)
    
    # Visualize hypergraph
    visualize_hypergraph_structure(xor3n, num_steps=30)
    
    print("\n" + "=" * 70)
    print("VISUALIZATION COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    create_demo_visualization()
