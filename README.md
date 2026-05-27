# 🚀 Multi-Project Async Runner

This `main.py` runs all three projects simultaneously and asynchronously:

## 📋 Projects Included

1. **JWT Token Generator API** (Port 30326)
   - Generates JWT access tokens
   - Required by Long Bio API

2. **Long Bio API** (Port 5000)
   - Updates user bios in Free Fire
   - Depends on JWT Token Generator API

3. **Discord Bot** (Port 5005)
   - Discord bot for interaction
   - Calls Long Bio API endpoints

## ⚙️ Setup & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Edit `.env` file and add your Discord Bot Token:
```
DISCORD_TOKEN=your_bot_token_here
```

### 3. Run All Projects
```bash
python main.py
```

## 📡 API Endpoints

| Project | URL | Port |
|---------|-----|------|
| JWT API | `http://localhost:30326` | 30326 |
| Bio API | `http://localhost:5000` | 5000 |
| Discord Bot | Running in background | 5005 |

## 🔗 API Dependency Chain

```
Discord Bot 
    ↓ (calls)
Long Bio API (http://localhost:5000)
    ↓ (calls)
JWT Token Generator API (http://localhost:30326)
```

## 📝 JWT Token API Usage

**Get Token:**
```bash
curl "http://localhost:30326/token?key=watashii&access=YOUR_ACCESS_TOKEN"
```

## 🛑 Stopping All Projects

Press `Ctrl + C` in the terminal to gracefully shutdown all projects.

## ❌ Troubleshooting

### Port Already in Use
If you get "Address already in use" error:
```bash
# Find process using port (Windows)
netstat -ano | findstr :30326

# Find process using port (macOS/Linux)
lsof -i :30326

# Kill the process
# On Windows: taskkill /PID <PID> /F
# On Linux/macOS: kill -9 <PID>
```

### Discord Token Error
- Ensure `.env` file exists in the project root
- Verify Discord bot token is valid
- Check bot has proper permissions in Discord server

### Flask Apps Not Starting
- Check if ports 30326 and 5000 are available
- Verify all dependencies are installed: `pip install -r requirements.txt`

## 📚 Project Structure

```
.
├── main.py                          # 👈 Main async runner
├── requirements.txt                 # Combined dependencies
├── .env                            # Environment variables
├── Acc-to-Jwt-Gen-Api-main/       # JWT Token Generator
│   ├── main.py
│   ├── requirements.txt
│   └── app/
├── Long-bio-api-main/             # Bio Update API
│   ├── app.py
│   ├── requirements.txt
│   └── ...
└── Long-bio-bot-main/             # Discord Bot
    ├── app.py
    ├── requirements.txt
    └── ...
```

## 🔐 Security Notes

- Never commit `.env` file with real tokens
- Use strong API keys
- Enable HTTPS in production
- Validate all input data

## 📞 Support

For issues, check logs or review individual project files for detailed error messages.

---
**Created by @watashii_ff** ✨
