# XOR3N: Three-Phase Synchronization with LCM Alignment

A sophisticated synchronization system implementing three-phase periodic scheduling with XOR-of-the-other-2 training over a hypergraph structure. The system acts as a high-pass/novelty filter, canceling persistent patterns while emphasizing phase-specific fluctuations.

## Overview

XOR3N implements:

- **3 Sync Phases** (A, B, C) with individual cadences (i, j, k)
- **LCM-aligned Supercycle**: T = LCM(i, j, k) + t₀
- **Periodic Scheduling** over hypergraph structure
- **XOR-of-the-Other-2 Training**: Each phase trains on XOR of the other two
  - Phase A ← (B XOR C)
  - Phase B ← (A XOR C)  
  - Phase C ← (A XOR B)
- **High-Pass/Novelty Filter**: Persistent/common signals get canceled (low-frequency), while fluctuating/phase-specific signals become salient (high-frequency)

## Key Concepts

### Algebraic Structure

The XOR operation creates a natural novelty detection mechanism:
- **Persistent patterns** (signals common across phases) → **Canceled** (XOR eliminates common bits)
- **Fluctuating patterns** (phase-specific signals) → **Emphasized** (XOR highlights differences)

### Hypergraph Scheduling

Each phase activates on its own cadence, creating complex temporal patterns where different combinations of phases are active. The supercycle T = LCM(i, j, k) ensures the pattern repeats periodically.

## Installation

No dependencies required - pure Python implementation.

```bash
git clone https://github.com/ZoneCog/xor3n.git
cd xor3n
```

## Usage

### Basic Example

```python
from xor3n import create_xor3n

# Create system with cadences 2, 3, 5
xor3n = create_xor3n(cadence_a=2, cadence_b=3, cadence_c=5)

# The supercycle is LCM(2, 3, 5) = 30
print(f"Supercycle: {xor3n.supercycle}")  # Output: 30

# Run a single step with signals
xor3n.step(0, signal_a=1, signal_b=0, signal_c=1)

# Check training signals (XOR of the other two)
print(xor3n.phase_a.training_history[0])  # B XOR C = 0 XOR 1 = 1
print(xor3n.phase_b.training_history[0])  # A XOR C = 1 XOR 1 = 0
print(xor3n.phase_c.training_history[0])  # A XOR B = 1 XOR 0 = 1
```

### High-Pass Filter Behavior

```python
from xor3n import XOR3N

xor3n = XOR3N(2, 3, 5)

# Scenario 1: All phases same (persistent signal)
xor3n.step(0, signal_a=1, signal_b=1, signal_c=1)
# Training signals: (0, 0, 0) - common signal canceled!

# Scenario 2: Phase-specific signal (novelty)
xor3n.step(1, signal_a=1, signal_b=0, signal_c=0)
# Training signals: (0, 1, 1) - B and C detect novelty in A!
```

### Phase Scheduling

```python
# Get the periodic schedule
schedule = xor3n.get_schedule(30)  # One full supercycle

for t, active_phases in schedule[:10]:
    print(f"t={t}: {', '.join(active_phases) or 'none'}")

# Output shows which phases are active at each time:
# t=0: A, B, C  (all synchronized)
# t=1: none
# t=2: A
# t=3: B
# t=4: A
# t=5: C
# ...
```

### Running Cycles

```python
# Define a signal generator
def signal_gen(t, phase_name):
    return (t + ord(phase_name)) % 2  # Different pattern per phase

# Run for multiple steps
xor3n.run_cycle(num_steps=30, signal_generator=signal_gen)

# Analyze the novelty filter behavior
analysis = xor3n.analyze_novelty_filter(30)
print(f"Active counts: {analysis['active_counts']}")
```

## API Reference

### Classes

#### `XOR3N(cadence_a, cadence_b, cadence_c, t0=0)`

Main class implementing the three-phase synchronization system.

**Methods:**
- `step(t, signal_a, signal_b, signal_c)` - Execute one time step
- `run_cycle(num_steps, signal_generator)` - Run multiple steps
- `compute_xor_training(t)` - Compute XOR training signals
- `get_active_phases(t)` - Get phases active at time t
- `get_schedule(num_steps)` - Get periodic schedule
- `analyze_novelty_filter(num_steps)` - Analyze filter behavior

#### `Phase(name, cadence, t0=0)`

Represents a single phase in the system.

**Methods:**
- `is_active(t)` - Check if phase is active at time t
- `get_signal(t)` - Get signal value at time t
- `set_signal(t, value)` - Set signal value at time t
- `record_training(t, value)` - Record training value

### Functions

- `lcm(a, b)` - Calculate LCM of two numbers
- `lcm_multiple(numbers)` - Calculate LCM of multiple numbers
- `create_xor3n(cadence_a, cadence_b, cadence_c, t0)` - Factory function

## Examples

Run the included examples:

```bash
python examples.py
```

This demonstrates:
1. Basic usage and supercycle calculation
2. XOR-of-the-other-2 training mechanism
3. High-pass/novelty filter effect
4. Supercycle analysis for different cadences
5. Hypergraph periodic scheduling patterns

## Testing

Run the test suite:

```bash
python -m unittest test_xor3n -v
```

All 21 tests validate:
- LCM calculations
- Phase activation patterns
- XOR operations
- Training signal computation
- Novelty filter behavior
- Schedule generation

## Mathematical Properties

### Supercycle Period

For cadences (i, j, k), the system repeats every T = LCM(i, j, k) steps.

Example cadences and their supercycles:
- (2, 3, 5) → T = 30
- (3, 4, 6) → T = 12
- (7, 11, 13) → T = 1001

### XOR Training Properties

For any signals a, b, c:
- a XOR a = 0 (self-cancellation)
- a XOR 0 = a (identity)
- (a XOR b) XOR c = a XOR (b XOR c) (associativity)

This creates the novelty detection:
- When all phases equal: all training signals = 0 (canceled)
- When phases differ: training signals highlight differences

## Use Cases

- **Temporal pattern detection** in multi-stream data
- **Novelty detection** in synchronized systems
- **Differential signal processing** with automatic common-mode rejection
- **Hypergraph edge scheduling** with periodic constraints
- **Multi-phase training** where each phase learns from others' differences

## License

See LICENSE file for details.

## Contributing

Contributions welcome! Please ensure all tests pass before submitting PRs.

## References

This implementation is based on concepts from:
- LCM-based periodic scheduling
- XOR-based novelty detection
- Hypergraph temporal synchronization
- Differential training in multi-agent systems