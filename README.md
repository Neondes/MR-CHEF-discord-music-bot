# Discord Music Bot

A feature-rich Discord music bot built with Python, discord.py, yt_dlp, and FFmpeg. It allows users to stream audio directly from YouTube into voice channels with queue management, loop support, and custom commands.

---

## Features

* **YouTube Streaming:** Stream audio directly from YouTube URLs or search queries.
* **Queue Management:** Add multiple tracks to a server-specific queue.
* **Loop Toggle:** Repeatedly play the currently active track.
* **Voice Controls:** Dynamically join, move between, and disconnect from voice channels.
* **Automated Cleanup:** Automatically disconnects when the queue is finished and clears guild-specific state data.

---

## Commands

All commands use the `*` prefix.

| Command | Usage | Description |
| :--- | :--- | :--- |
| *play | *play <search terms or URL> | Connects to your voice channel and streams or queues audio from YouTube. |
| *queue | *queue | Displays the current list of queued tracks for the server. |
| *loop | *loop | Toggles loop mode on or off for the currently playing track. |
| *join | *join | Summons the bot to your current voice channel. |
| *stop | *stop | Stops playback, clears the server's queue, and disconnects the bot. |
| *ping | *ping | Responds with "Pong!" to test bot latency/responsiveness. |

---

## Setup & Installation

### Prerequisites

1. **Python 3.8+**
2. **FFmpeg:** Ensure FFmpeg is installed on your system and added to your system's PATH environment variable.
3. **Discord Bot Token:** Created via the Discord Developer Portal.

### Step-by-Step Installation

1. **Install Dependencies:**
   pip install discord.py yt-dlp python-dotenv

2. **Configure Environment Variables:**
   Create a `.env` file in the same directory as `main.py` and add your Discord bot token:
   DISCORD_TOKEN=your_discord_bot_token_here

3. **Enable Bot Intents:**
   Go to the Discord Developer Portal, navigate to your application's Bot tab, and enable Message Content Intent under Privileged Gateway Intents.

4. **Run the Bot:**
   python main.py
