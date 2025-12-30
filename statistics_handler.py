import os, json


BASE_DIR = os.path.dirname(__file__)

STATS_FILE = os.path.join(BASE_DIR,'data',"statistics.json")

def load_stats() -> dict | None:
    if not os.path.exists(STATS_FILE):
        return {
            "total_answers": 0,
            "correct_answers": 0,
            "wrong_answers": 0,
            "sessions": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "wrong_words": {}
        }

    with open(STATS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    
def save_stats(stats: dict) -> None:
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)



stats = load_stats()
def add_answer(stats, word, translation, is_correct):
    stats["total_answers"] += 1

    if is_correct:
        stats["correct_answers"] += 1
        stats["current_streak"] += 1

        if stats["current_streak"] > stats["longest_streak"]:
            stats["longest_streak"] = stats["current_streak"]
    else:
        stats["wrong_answers"] += 1
        stats["current_streak"] = 0

        if word not in stats["wrong_words"]:
            stats["wrong_words"][word] = {
                "translation": translation,
                "count": 1
            }
        else:
            stats["wrong_words"][word]["count"] += 1



def add_session(stats):
    stats["sessions"] += 1
    save_stats(stats)


