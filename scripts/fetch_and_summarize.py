import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

MAX_TOPICS = 15


def get_target_date_jst() -> str:
    """JSTで「昨日」の日付(YYYY-MM-DD)を返す。"""
    now_jst = datetime.now(ZoneInfo("Asia/Tokyo"))
    target = now_jst.date() - timedelta(days=1)
    return target.isoformat()


def fetch_posts_from_x_placeholder(target_date: str):
    """
    ★ここは後で「Xの投稿取得」に差し替える場所です。

    今は動作確認用にダミーデータを返しています。
    実際には:
      - 5アカウントから target_date の投稿を取得
      - 1件ごとに dict を作成 {text, url, created_at, author}
    のような形にします。
    """
    dummy_posts = [
        {
            "text": "OpenAIが新しいマルチモーダルモデルを発表。画像と音声を同時に処理可能になりました。",
            "url": "https://x.com/example/status/1",
            "created_at": f"{target_date}T12:00:00+09:00",
            "author": "AIExplainedYT",
        },
        {
            "text": "Googleが次世代生成AIモデルを公開。推論速度が向上し、APIとして提供開始。",
            "url": "https://x.com/example/status/2",
            "created_at": f"{target_date}T15:30:00+09:00",
            "author": "rowancheung",
        },
    ]
    return dummy_posts


def simple_japanese_summary(texts):
    """
    本来はLLMで「日本語の要約」を作るが、
    今は簡易的に最初の1〜2文程度を切り出すだけ。
    """
    joined = " ".join(texts)
    # 句点でざっくり区切って先頭2文だけ使う
    sentences = joined.split("。")
    summary = "。".join(sentences[:2]).strip()
    if not summary.endswith("。") and summary != "":
        summary += "。"
    return summary or joined[:120]


def build_topics_from_posts(posts, max_topics: int = MAX_TOPICS):
    """
    本来は「重複トピックのクラスタリング」を行うが、
    今は各投稿1件＝1トピックとしてそのまま使う簡易版。
    """
    topics = []
    for i, post in enumerate(posts[:max_topics]):
        title = post["text"][:40]  # 先頭40文字をタイトルっぽく
        summary_short = simple_japanese_summary([post["text"]])
        summary_detail = summary_short  # 詳細＝同じ（あとでLLM要約に差し替え）

        topic = {
            "id": f"topic_{i+1:03d}",
            "title": title,
            "summary_short": summary_short,
            "summary_detail": summary_detail,
            "sources": [
                {
                    "title": f"{post['author']} の投稿",
                    "url": post["url"],
                }
            ],
        }
        topics.append(topic)
    return topics


def main():
    repo_root = Path(__file__).resolve().parents[1]
    public_dir = repo_root / "public"
    public_dir.mkdir(parents=True, exist_ok=True)

    target_date = get_target_date_jst()
    posts = fetch_posts_from_x_placeholder(target_date)
    topics = build_topics_from_posts(posts, MAX_TOPICS)

    output = {
        "date": target_date,
        "topics": topics,
    }

    output_path = public_dir / f"daily_topics_{target_date}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
