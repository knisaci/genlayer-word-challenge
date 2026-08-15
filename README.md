# Word Challenge — GenLayer

A word game built on GenLayer's Testnet Bradbury. Every day, a challenge word is set on-chain. Players write one sentence using the word correctly. Five AI validators independently judge the sentence for correctness and creativity, reach consensus, and update the player's score on-chain.

## How it works

1. Admin sets today's word via `set_word()`
2. Player submits a sentence via `submit_sentence()`
3. Five Bradbury validators independently run an LLM prompt judging the sentence
4. Custom validator logic (`gl.vm.run_nondet_unsafe`) accepts the result only when:
   - Correctness judgment matches across validators
   - Creativity band (low / good / creative) matches
5. Score and history stored on-chain per wallet address via `TreeMap`

## Scoring

| Outcome | Points |
|---|---|
| Word used correctly | +5 |
| Creativity: low | +1 |
| Creativity: good | +3 |
| Creativity: creative | +5 |
| Max per round | 10 |

## Deployed Contract

- **Network:** Testnet Bradbury
- **Address:** `0x621326E5faE3c5dEe52171E14Eff9DC4741138c1`

## Files

- `WordChallenge.py` — Intelligent Contract
- `play.py` — CLI player script

## How to play

Install the GenLayer CLI:
```bash
sudo npm install -g genlayer
genlayer network set testnet-bradbury
genlayer account create --name default
```

Then run:
```bash
python3 play.py
```

## Contract Methods

| Method | Type | Description |
|---|---|---|
| `get_today_word()` | view | Returns the current challenge word |
| `get_player_stats(address)` | view | Returns score, streak, and history for a wallet |
| `get_leaderboard()` | view | Returns top 20 players by score |
| `set_word(word)` | write | Admin sets the challenge word |
| `submit_sentence(sentence)` | write | Submit a sentence for AI judging |
