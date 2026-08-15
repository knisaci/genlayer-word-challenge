# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json

class WordChallenge(gl.Contract):
    today_word: str
    player_stats: TreeMap[Address, str]
    leaderboard: TreeMap[Address, str]

    def __init__(self) -> None:
        self.today_word = 'consensus'

    @gl.public.view
    def get_today_word(self) -> str:
        return self.today_word

    @gl.public.view
    def get_player_stats(self, player: Address) -> str:
        return self.player_stats.get(player, '{"score":0,"streak":0,"history":[]}')

    @gl.public.view
    def get_leaderboard(self) -> str:
        entries = []
        for addr in self.leaderboard:
            raw = self.leaderboard[addr]
            dat = json.loads(raw)
            entries.append({
                "address": str(addr),
                "score": dat.get("score", 0)
            })
        entries.sort(key=lambda x: x["score"], reverse=True)
        return json.dumps(entries[:20])

    @gl.public.write
    def set_word(self, word: str) -> None:
        self.today_word = word

    @gl.public.write
    def submit_sentence(self, sentence: str) -> None:
        word = self.today_word

        prompt = f'''Today's word: "{word}"
Player's sentence: "{sentence}"

Judge this sentence on two things:
1. Did the player use the word correctly? Answer true or false.
2. How creative is the sentence? Answer with exactly one of: low, good, creative.

Respond ONLY with this JSON, nothing else:
{{"correct": true, "creativity": "good", "feedback": "one sentence of encouragement"}}

It is mandatory that you respond only using the JSON format above.
Do not include markdown fences, explanation, or any other text.'''

        def leader_fn() -> dict:
            res = gl.nondet.exec_prompt(prompt)
            res = res.replace('```json', '').replace('```', '').strip()
            dat = json.loads(res)
            creativity = str(dat.get('creativity', 'low')).lower()
            if creativity not in ['low', 'good', 'creative']:
                creativity = 'low'
            correct = bool(dat.get('correct', False))
            feedback = str(dat.get('feedback', ''))
            points = 5 if correct else 0
            creativity_points = {'low': 1, 'good': 3, 'creative': 5}
            points += creativity_points.get(creativity, 0)
            return {
                'correct': correct,
                'creativity': creativity,
                'feedback': feedback,
                'points': points,
            }

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            leader = leader_result.calldata
            if not isinstance(leader, dict):
                return False
            mine = leader_fn()
            if mine['correct'] != leader.get('correct'):
                return False
            if mine['creativity'] != leader.get('creativity'):
                return False
            return True

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        addr = gl.message.sender_address
        raw = self.player_stats.get(addr, '{"score":0,"streak":0,"history":[]}')
        stats = json.loads(raw)
        stats['score'] = stats.get('score', 0) + result['points']
        stats['streak'] = stats.get('streak', 0) + 1
        history = stats.get('history', [])
        history.insert(0, {
            'word': word,
            'sentence': sentence,
            'correct': result['correct'],
            'creativity': result['creativity'],
            'feedback': result['feedback'],
            'points': result['points'],
        })
        stats['history'] = history[:10]
        self.player_stats[addr] = json.dumps(stats)

        lb_raw = self.leaderboard.get(addr, '{"score":0}')
        lb = json.loads(lb_raw)
        lb['score'] = lb.get('score', 0) + result['points']
        self.leaderboard[addr] = json.dumps(lb)
