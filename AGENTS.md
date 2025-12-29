# AGENTS.md - Truco Uruguayo Project Guide

This document serves as the primary source of truth for AI agents and developers working on the Truco Uruguayo project. It contains project context, game rules, coding standards, and architectural guidelines.

---

## 🚀 Project Overview

**Truco Uruguayo** is a trick-taking card game popular in Uruguay. This repository provides:
- A minimal engine for the 2-player version of the game.
- Reinforcement Learning (RL) agents (First-Visit Monte Carlo and Q-Learning).
- Tools for training, evaluation, and manual play (CLI).

---

## 🃏 Game Rules: Truco Uruguayo

### Overview
- Aim: Score points to be the first to reach **40 points**.
- Deck: Spanish 40-card deck (no 8s or 9s).
- Players: 2 players (each receives 3 cards).
- **Muestra**: One card turned face up after dealing, determining the trump suit.

### Card Hierarchy (Worst to Best)
The hierarchy is determined by the `Card.get_card_value()` method, which considers the **Muestra** (trump indicator).

1.  **Cuatros**: 4 of any suit (except Pieza) [Value 0]
2.  **Cincos**: 5 of any suit (except Pieza) [Value 1]
3.  **Seises**: 6 of any suit [Value 2]
4.  **Sietes Falsos**: 7 of Copa and Basto [Value 3]
5.  **Sotas**: 10 of any suit (except Pieza) [Value 4]
6.  **Caballos**: 11 of any suit (except Pieza) [Value 5]
7.  **Reyes**: 12 of any suit (except Pieza) [Value 6]
8.  **Ases Falsos**: 1 of Oro and Copa [Value 7]
9.  **Doses**: 2 of any suit (except Pieza) [Value 8]
10. **Treses**: 3 of any suit [Value 9]
11. **Matas** (Special fixed hierarchy):
    - 7 of Oro [Value 10]
    - 7 of Espadas [Value 11]
    - 1 of Basto [Value 12]
    - 1 of Espadas [Value 13]
12. **Piezas** (Top priority, must match **Muestra** suit):
    - 10 of Muestra [Value 14]
    - 11 of Muestra [Value 15]
    - 5 of Muestra [Value 16]
    - 4 of Muestra [Value 17]
    - 2 of Muestra [Value 18]
    - *Special Rule*: If the Muestra is one of the Piezas (2, 4, 5, 10, or 11), the **Rey (12)** of the Muestra suit becomes a Pieza and takes the value of the card that matches the Muestra.

### Truco (Trick-taking phase)
- A round consists of up to 3 tricks. The first team to win 2 tricks wins the round.
- **Tied Trick**:
    - If the first trick is tied, the winner of the second trick wins the round.
    - If the first has a winner and the second is tied, the winner of the first wins the round.
    - If all three tricks are tied, the **starting player** of the round (the "hand") wins.
    - If the first and second tricks are won by different players and the third is tied, the winner of the first wins.

### Bidding
- **Default**: 1 point
- **Truco**: 2 points
- **Retruco**: 3 points
- **Vale 4**: 4 points
- Players can only raise the bid if they didn't make the last bid (alternating turns).
- If a player rejects a bid, the other player wins the round with the points accumulated up to the *previous* accepted bid.

### Flor
- **Condition**: A player has a "Flor" if they have:
    - Three cards of the same suit.
    - One **Pieza** and two cards of the same suit.
    - Two or more **Piezas**.
- **Points**: 3 points for the team.
- **Rules**:
    - Must be called on the player's **first turn** of the round.
    - Saying "Flor" does not end the turn; the player must still play a card or bid Truco.
    - **Fake Flor**: If a player calls Flor without having one, the opposing team gets the 3 points at the end of the round.

---

## 📂 Repository Structure

```plaintext
src/
  agents/           # RL Agents (MonteCarlo, QLearning) and Action Providers
    base_agent.py
    monte_carlo_agent.py
    q_learning_agent.py
    random_agent.py
    provider.py      # Bridges game logic and agents
  models/           # Core Domain Models
    card.py          # Card hierarchy and comparison
    deck.py          # Full 40-card Spanish deck
    game.py          # coordinates multiple rounds
    player.py        # Player state and card management
    round.py         # Main game flow, bidding, and trick resolution
  schemas/          # Pydantic & TypedDict Schemas
    actions.py       # ActionCode enum and helpers
    constants.py     # Card numbers, suits, etc.
    observation.py   # State representation for agents
    player_state.py  # View of the game from a player's perspective
    round_state.py   # Internal round tracking
    train_config.py  # Pydantic config for training sessions
  utils/            # Support Utilities
    config_loader.py
    cli_actions.py
  evaluate.py       # Script: Evaluate a trained agent
  play.py           # Script: Play human vs human (CLI)
  play_vs_agent.py  # Script: Play human vs agent (CLI)
  train.py          # Script: Train agents
configs/            # Agent and training YAML configurations
```

---

## 🎮 Action Codes
Agents interact with the game using `ActionCode` (IntEnum):
- `0, 1, 2`: Play card at hand index 0, 1, or 2.
- `3`: **Offer/Advance**: Raise the Truco bid (Offer Truco/Retruco/Vale 4).
- `4`: **Accept**: Agree to the current Truco bid.
- `5`: **Reject**: Fold/Concede the round at the current bid level.
- `6`: **Flor**: Call Flor (3 points).

---

## 🛠 Coding Standards

### Python Standards
- **Python 3.12+**: Use modern syntax and features.
- **Typing Always**: Full type hints for all parameters and return types. Use `dict` and `list` instead of `typing.Dict/List`.
- **Google Docstring Standard**: Every class and function must have a docstring with `Args`, `Returns`, and `Raises`.
- **No Module Docstrings**: Do NOT add docstrings at the top of the file.
- **Meaningful Comments**: Only comment complex logic; avoid obvious or redundant comments.

### Data Models & Schemas
- **Pydantic `BaseModel`**: Use for complex schemas (States, Configs).
- **`dataclass`**: Use for simple mutable containers.
- **`Literal` & `IntEnum`**: Use for fixed sets of values (Suits, Card Numbers, Action Codes).

### Code Quality
- Follow **PEP 8**.
- Maintain consistency with the existing card-comparison and state-tracking patterns.
- Ensure all new logic is covered by types to facilitate static analysis (Pyright/Ruff).

---

## 📖 Operational Guide

### Setup
```bash
uv sync
```

### Common Commands
- **Play (Human vs Human):** `uv run python src/play.py`
- **Train Agent:** `uv run python src/train.py --config configs/mc_config.yaml`
- **Evaluate Agent:** `uv run python src/evaluate.py --config configs/mc_config.yaml`
- **Play vs Agent:** `uv run python src/play_vs_agent.py --config configs/mc_config.yaml`

### Training Outputs
Artifacts are stored in `src/output/<type>/<timestamp>/`. The agent file is saved as defined in the config `out` field (e.g., `mc_agent.pkl`).
