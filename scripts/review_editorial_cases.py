"""Re-run deliberately selected script regressions; this is not an unseen benchmark."""
from pathlib import Path
import hashlib
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run_pipeline import DEFAULT_INPUT
from src.parser import parse_folder
from src.candidate_generator import segment,make_candidate
from src.llm_evaluator import evaluate_offline

CASES=[
 (30,3.0,43.5,False,'Decorative pocket-watch chain is not an attack.'),
 (49,84.0,112.8,False,'Eyes burning with ambition is metaphor, not visible injury.'),
 (47,14.8,59.8,False,'Burning ambition creates a false hook and the cut changes scenes.'),
 (21,47.3,99.2,False,'The child recovers before an unrelated Duchess subplot question.'),
 (24,0.0,20.5,False,'Slow door handle opening and medicine context fail a cold-viewer hook.'),
 (9,13.8,54.0,False,'Touching a feverish forehead is not itself a visceral opening.'),
 (32,3.0,24.8,False,'Revised after audit: book is visible, but this cut ends on filler What?; cut before the reaction or reject if under 20s.'),
 (25,13.2,33.8,False,'Revised after audit: injury is real, but one-word Who? is a weak endpoint; prefer a substantive accusation or question.'),
 (3,8.8,40.4,True,'You stole my wedding establishes the betrayal without decorative injury keywords.'),
 (21,11.2,35.8,True,'A desperate plea for a dying child ends before help is agreed or the child is cured.'),
 (3,84.0,112.5,True,'Guard is struck; a stranger protects a woman, whose question remains unanswered.'),
]

def main():
    episodes=parse_folder(DEFAULT_INPUT);lookup={e.number:e for e in episodes};results=[]
    for number,a,z,expected,note in CASES:
        item=evaluate_offline(make_candidate([segment(lookup[number],a,z)],f'REVIEW-{number}-{a}-{z}'),episodes)
        actual=item['decision']['eligible']
        results.append(dict(expected_shortlist=expected,actual_shortlist=actual,matches=actual==expected,review_note=note,candidate=item))
    output=Path(__file__).resolve().parents[1]/'raw_outputs/editorial_regression_review.json'
    output.write_text(json.dumps({'method':'Eleven hand-selected development cases; E25 and E32 expectations revised after the explicit filler-ending audit. Prior expectations preserved in history. Reviewed from complete source tracks. Not independent human validation or a general accuracy estimate.',
                                  'cases':results,'matched':sum(x['matches'] for x in results),'total':len(results)},ensure_ascii=False,indent=2)+'\n')
    manifest_path=output.parent/'manifest.json';manifest=json.loads(manifest_path.read_text())
    manifest[output.name]=hashlib.sha256(output.read_bytes()).hexdigest();manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    print(f"Editorial development regressions: {sum(x['matches'] for x in results)}/{len(results)} matched script-review expectations.")
    if not all(x['matches'] for x in results):raise SystemExit(1)

if __name__=='__main__':main()
