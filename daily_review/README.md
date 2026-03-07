# Daily News Report Generator

A Python script that fetches top stories from Google News RSS feed and generates a formatted daily news report.

## Features

- Fetches top 10 news stories from Google News
- Generates formatted Markdown reports
- Saves reports with date-stamped filenames
- Shows preview in console when run
- **Email reports automatically** (via Resend - free tier: 100 emails/day)
- Configurable country and language settings

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage (Generate Report Only)

```bash
python daily_news.py
```

The script will:
1. Fetch the latest top stories from Google News (US edition)
2. Generate a Markdown report
3. Save it to `daily_news_YYYY-MM-DD.md`
4. Display a preview in the console

### With Email (Auto-send Reports)

To email the report, you need to:

1. **Sign up for Resend** (free tier: 100 emails/day)
   - Go to https://resend.com
   - Create an account (free)
   - Get your API key (starts with `re_`)

2. **Save your API key** to the file:
   ```
   C:\Users\andre\Downloads\resend_api_key_plain_text.txt
   ```
   Just put the key (e.g., `re_xxxxxx`) in this file, nothing else.

3. **Set the recipient email:**

   **Option A - Environment variable (recommended):**
   ```powershell
   $env:DAILY_NEWS_EMAIL="andrew123daly@gmail.com"
   ```

   **Option B - Edit the script:**
   Change the default in `daily_news.py`:
   ```python
   to_email = os.environ.get("DAILY_NEWS_EMAIL", "andrew123daly@gmail.com")
   ```

4. **Run the script:**
   ```bash
   python daily_news.py
   ```

   The report will be emailed automatically!

**Alternative:** You can also set the API key via environment variable instead of the file:
```powershell
$env:RESEND_API_KEY="re_your_api_key_here"
```

## Output Format

Reports are generated in Markdown format with:
- Report date and generation timestamp
- Numbered list of top stories
- Title, source, publication date, and link for each story

## Customization

### News Feed Options

To customize the news feed, edit the `fetch_google_news_rss()` call in `main()`:

```python
# Example: Fetch UK news in English
stories = fetch_google_news_rss(country='GB', language='en', num_stories=15)

# Example: Fetch Spanish news
stories = fetch_google_news_rss(country='ES', language='es', num_stories=10)
```

### Available Parameters

- `country`: Country code (e.g., 'US', 'GB', 'CA', 'AU', 'IN')
- `language`: Language code (e.g., 'en', 'es', 'fr', 'de')
- `num_stories`: Number of stories to fetch (default: 10)

### Email Customization

To use a custom sender email (requires domain verification in Resend):

```python
# In main(), change:
from_email = os.environ.get("DAILY_NEWS_FROM", "news@yourdomain.com")
```

## Scheduling (Optional)

To run this script automatically every day with email delivery:

### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create a new Basic Task
3. Set trigger to "Daily" at your preferred time
4. Set action to "Start a program"
5. Program: `powershell.exe`
6. Arguments: `-Command "$env:RESEND_API_KEY='re_your_key'; $env:DAILY_NEWS_EMAIL='andrew123daly@gmail.com'; cd C:\path\to\daily_review; python daily_news.py"`

### Linux/Mac (Cron)
Add to crontab to run at 8 AM daily:
```bash
0 8 * * * cd /path/to/daily_review && RESEND_API_KEY=re_your_key DAILY_NEWS_EMAIL=andrew123daly@gmail.com python daily_news.py
```

## Files

- `daily_news.py` - Main script
- `requirements.txt` - Python dependencies
- `daily_news_YYYY-MM-DD.md` - Generated reports (created when script runs)

## Troubleshooting

### "RESEND_API_KEY environment variable not set"
- Make sure you've set the API key as shown in the setup instructions
- The key should start with `re_`

### "You must verify your domain to send to this recipient"
- With the free Resend tier, you can only send to the email you signed up with
- To send to any email, verify a domain in Resend dashboard
- Or use `onboarding@resend.dev` as sender (for testing only)



C:\Dev\virtual_envs\venv\Scripts>