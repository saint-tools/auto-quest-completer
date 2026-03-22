# Discord Quest Completer

> Automated Discord quest completion with multi-account support, auto-enrollment, and a clean real-time progress display.

---

## Features

- **Auto-enrollment** — Automatically accepts all available quests, no manual clicking required
- **Multi-token support** — Run as many accounts as you want simultaneously, each with its own colored output
- **Concurrent quest completion** — All quests on each account run at the same time, not one by one
- **Invalid token handling** — Bad tokens are detected on login and automatically removed from `tokens.txt`
- **Supported quest types:**
  - `WATCH_VIDEO` / `WATCH_VIDEO_ON_MOBILE`
  - `PLAY_ON_DESKTOP`
  - `STREAM_ON_DESKTOP`
  - `PLAY_ACTIVITY`

---

## Requirements

- Python 3.10 or newer
- pip packages listed in `requirements.txt`

```
discord.py-self
aiohttp
colorama
```

---

## Installation

```bash
git clone https://github.com/saint-tools/auto-quest-completer.git
cd auto-quest-completer
pip install -r requirements.txt
```

---

## Configuration

**`tokens.txt`** — one token per line:
```
token1
token2
token3
```

**`config.json`** — settings file in the same folder as `main.py`:
```json
{
    "activity_channel_id": null,
    "timezone": "America/New_York",
    "locale": "en-US"
}
```

| Field | Description |
|---|---|
| `activity_channel_id` | Voice channel ID to use for `PLAY_ACTIVITY` quests. Set to `null` to auto-detect. |
| `timezone` | Your timezone string, e.g. `"Europe/London"` |
| `locale` | Your locale string, e.g. `"en-GB"` |

---

## Usage

```bash
python main.py
```

The script will:
1. Log in all tokens from `tokens.txt`
2. Fetch all available quests for each account
3. Auto-enroll in any quests not yet accepted
4. Complete all eligible quests concurrently
5. Print real-time progress bars for each quest

---

## Project Structure

```
.
├── main.py           # main script
├── tokens.txt        # one Discord token per line
├── config.json       # timezone, locale, activity channel
├── requirements.txt  # pip dependencies
└── README.md
```

---

## Notes

- `STREAM_ON_DESKTOP` quests require at least one other person in the voice channel to count progress, same as the official Discord client
- Auto-enrollment may fail on quests that show a captcha — those will be skipped with an error message
- Avoid running too many tokens at once to stay within Discord rate limits

---

## Disclaimer

This project is for educational purposes only. You are solely responsible for how you use this tool. Misuse may violate Discord's Terms of Service and result in account suspension. The author assumes no liability for any consequences.

---

## License

MIT License
