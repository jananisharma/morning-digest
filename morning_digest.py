import feedparser
import smtplib
import os
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText
from dotenv import load_dotenv
import anthropic

# Load secret variables from .env file
load_dotenv()

# Load credentials from .env
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# Initialize Claude client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Who Janani is — this gets sent to Claude with every request
JANANI_PROFILE = """Bioengineering graduate (Northeastern, 2021) with experience in 
pharmaceutical R&D, life sciences consulting, and biotech business development and sales. 
Grammy-nominated vocalist, dancer, producer, and independent artist with an organically 
built audience of 425K+ followers and 40M+ views across social platforms, based in 
Cambridge, MA. Building toward founding a science media company targeting health-literate 
consumers — Gen Z women — at the intersection of scientific credibility and cultural fluency. 
Gearing up to release her debut concept album inspired by Amitav Ghosh's The Living Mountain, 
wanting to establish herself as a new-age indie music star and cultural tastemaker similar to 
Rosalia, Eartheater, Sega Bodega, Charli XCX. Wants to launch her album alongside a consumer 
product targeting female middle class consumers. Actively job searching in biotech, science 
communications, and AI-adjacent roles, preferably remote. For each news story provide one 
specific actionable strategic move — companies to reach out to, content angles to develop, 
album release timing insights, or AI tools to adopt."""


# RSS feeds organized by category
RSS_FEEDS = {
    "AI & Tech": [
        "https://feeds.simplecast.com/54nAGcIl",
        "https://rss.slashdot.org/Slashdot/slashdotMain",
        "https://hnrss.org/frontpage",
    ],
    "Music Industry": [
        "https://www.musicbusinessworldwide.com/feed/",
        "https://consequenceofsound.net/feed/",
        "https://www.nme.com/feed",
    ],
    "Biotech & Wellness": [
        "https://www.statnews.com/feed/",
        "https://medcitynews.com/feed/",
        "https://www.nature.com/nature.rss",
    ],
    "Consumer Markets": [
        "https://www.glossy.co/feed/",
        "https://www.modernretail.co/feed/",
        "https://feeds.feedburner.com/entrepreneur/latest",
    ]
}

def fetch_stories(feeds, max_per_feed=3):
    """Fetch stories from a list of RSS feed URLs."""
    all_stories = []
    for url in feeds:
        try:
            feed = feedparser.parse(url, agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            for entry in feed.entries[:max_per_feed]:
                story = {
                    "title": entry.get("title", "No title"),
                    "summary": entry.get("summary", "No summary available"),
                    "link": entry.get("link", ""),
                }
                all_stories.append(story)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return all_stories

def summarize_with_claude(category, stories):
    """Send stories to Claude and get back summaries + strategic move."""
    
    # Build a text block of all stories to send to Claude
    stories_text = ""
    for story in stories:
        stories_text += f"Title: {story['title']}\n"
        stories_text += f"Summary: {story['summary'][:300]}\n"
        stories_text += f"Link: {story['link']}\n\n"
    
    prompt = f"""You are a personal briefing assistant for Janani Sharma.

About Janani: {JANANI_PROFILE}

Here are today's {category} news stories:

{stories_text}

Your task:
1. Select the 3 most relevant and interesting stories for Janani
2. For each story write:
   - HEADLINE: the story title
   - SUMMARY: 2 sentences max, plain english, no jargon
   - STRATEGIC MOVE: one specific actionable thing Janani could do given this news

Format each story exactly like this:
HEADLINE: [title]
SUMMARY: [2 sentences]
STRATEGIC MOVE: [one specific action]

Only return the 3 stories, nothing else."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text


def send_email(subject, body):
    """Send the digest email via Gmail."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    
    # Attach the body as plain text
    part = MIMEText(body, "plain")
    msg.attach(part)
    
    # Connect to Gmail and send
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


def generate_subject_line(all_summaries):
    """Ask Claude to write a funny subject line."""
    prompt = f"""Write a single funny, clever, witty email subject line for a morning news 
digest covering AI, biotech, music industry, and consumer market news. 
Make it feel like something a sharp, culturally fluent Gen Z woman would find delightful. 
Max 10 words. Return only the subject line, nothing else.

Here's a sample of today's content:
{all_summaries[:500]}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=50,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()

def run_morning_digest():
    """Main function that runs the entire digest."""
    print("Starting morning digest...")
    
    all_summaries = ""
    email_body = "YOUR MORNING BRIEFING\n"
    email_body += "=" * 50 + "\n\n"
    
    # Loop through each category and its feeds
    for category, feeds in RSS_FEEDS.items():
        print(f"Fetching {category} stories...")
        
        # Fetch raw stories from RSS feeds
        stories = fetch_stories(feeds)
        
        if not stories:
            print(f"No stories found for {category}")
            continue
        
        # Send to Claude for summarizing
        print(f"Summarizing {category} with Claude...")
        summaries = summarize_with_claude(category, stories)
        
        # Add to email body
        email_body += f"📰 {category.upper()}\n"
        email_body += "-" * 40 + "\n"
        email_body += summaries + "\n\n"
        
        all_summaries += summaries + " "
    
    # Generate funny subject line
    print("Generating subject line...")
    subject = generate_subject_line(all_summaries)
    
    # Send the email
    print(f"Sending email with subject: {subject}")
    send_email(subject, email_body)
    print("Morning digest complete!")


# Ignition key — this runs everything
if __name__ == "__main__":
    run_morning_digest()

