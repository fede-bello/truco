## Truco Uruguayo (2‑player)

Minimal engine for the Uruguayan Truco card game plus simple RL agents (first‑visit Monte Carlo and Q‑learning). You can play in the terminal, train agents against a random opponent, evaluate trained agents, and play against a trained bot.

### Setup

All project dependencies are managed by `uv`. To install them, run:

```bash
uv sync
```

### Quick start

- **Play (human vs human, CLI):**

```bash
uv run python src/play.py
```

- **Train an agent:**

```bash
# Monte Carlo
uv run python src/train.py --config configs/mc_config.yaml

# Q-learning
uv run python src/train.py --config configs/ql_config.yaml
```

- **Evaluate a trained agent:**

```bash
uv run python src/evaluate.py --config configs/mc_config.yaml
# Uses latest session in src/output/mc (or ql) unless evaluation.output_dir is set
```

- **Play vs trained agent (human vs bot):**

```bash
python src/play_vs_agent.py --config configs/mc_config.yaml
```

### Configuration

Edit the YAML under `configs/` to set episodes, seeds, agent type (`mc_first_visit` or `q_learning`), and evaluation params. The `out` field names the saved artifact inside the session folder.

### Outputs

- Training and evaluation artifacts are stored under `src/output/<mc|ql>/<YYYYmmdd-HHMMSS>/`.
- The agent file is saved as the `out` value from the config (e.g., `mc_agent.pkl`, `q_agent.json`).
- Rolling stats are logged to console; training writes `rewards.txt` every 10k episodes; evaluation writes `evaluation.txt` with win rate and average points.

### Project structure

```
src/
  agents/           # MonteCarloAgent, QLearningAgent, providers for game ↔ agent
  exceptions/       # Custom exceptions
  models/           # Core game: Card, Deck, Player, Round, Game
  schemas/          # Typed states, constants, actions, training config
  utils/            # CLI helpers, config loader
  play.py           # Human vs human (CLI)
  play_vs_agent.py  # Human vs trained agent (CLI)
  train.py          # Train MC/QL agents from YAML config
  evaluate.py       # Evaluate a saved agent from a session dir
configs/            # Example YAML configs (mc_config.yaml, ql_config.yaml)
```
