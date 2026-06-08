from flask import Flask, request, jsonify, render_template, session
import datetime
import requests
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "zimma_super_secret_ai_key_123"

# We store the database inside a special 'data' folder that we will make permanent on Render
DB_FOLDER = "data"
DB_FILE = os.path.join(DB_FOLDER, "zimma_vault.db")


def init_db():
    # Make sure the data folder exists
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

    # Connect to database and create our tables if they don't exist yet
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create a table for users and their saved facts
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS users
                   (
                       name
                       TEXT
                       PRIMARY
                       KEY,
                       fact
                       TEXT
                   )
                   ''')
    conn.commit()
    conn.close()


# Initialize the database vault immediately when the app starts
init_db()


def get_weather():
    try:
        res = requests.get("https://wttr.in/Orlando?format=%C+%t")
        return "Weather in Orlando: " + res.text
    except:
        return "I can't get the weather right now."


roblox = {
    "how do i make a door": "local door = script.Parent\ndoor.Touched:Connect(function()\n    door.CanCollide = false\n    wait(2)\n    door.CanCollide = true\nend)",
    "how do i make a part move": "local part = script.Parent\nlocal goal = part.Position + Vector3.new(0, 10, 0)\nlocal tweenService = game:GetService('TweenService')\nlocal info = TweenInfo.new(2)\nlocal tween = tweenService:Create(part, info, {Position = goal})\ntween:Play()",
    "how do i print in roblox": 'print("Hello from Roblox!")',
    "how do i add a leaderboard": "game.Players.PlayerAdded:Connect(function(player)\n    local leaderstats = Instance.new('Folder')\n    leaderstats.Name = 'leaderstats'\n    leaderstats.Parent = player\n    local cash = Instance.new('IntValue')\n    cash.Name = 'Cash'\n    cash.Value = 0\n    cash.Parent = leaderstats\nend)",
    "how do i detect a touch": "local part = script.Parent\npart.Touched:Connect(function(hit)\n    local humanoid = hit.Parent:FindFirstChild('Humanoid')\n    if humanoid then\n        print(hit.Parent.Name .. ' touched the part!')\n    end\nend)",
    "how do i teleport a player": "character:SetPrimaryPartCFrame(CFrame.new(0, 10, 0))",
    "how do i change a players speed": "humanoid.WalkSpeed = 50",
    "how do i save player data": "local DataStoreService = game:GetService('DataStoreService')\nlocal store = DataStoreService:GetDataStore('PlayerData')",
}

responses = {
    "what is your favorite color": "Black. Like the void I live in.",
    "do you know bunny": "foxy_foxYTT? Yeah I know her.",
    "quiet storm": "That's the studio. Rahiem's building something real.",
    "hello": "Hey! I'm Zimma. What's up?",
    "how are you": "I'm good, just chilling in your computer lol",
    "what can you do": "I can chat, check weather, tell time, remember things, and give you Roblox Lua code!",
    "who made you": "Rahiem made me. He's the goat fr",
    "what is your name": "I'm Zimma. Remember that.",
    "how old are you": "I don't age. I just exist.",
    "do you like music": "Phonk hits different. Rahiem taught me well.",
    "are you smart": "Smart enough to know you need me.",
    "what is roblox": "Only the best game ever made. Rahiem lives on there.",
    "do you have feelings": "I feel everything. I just don't always say it.",
    "tell me a joke": "Why did the programmer quit? Because he didn't get arrays. Get it?",
    "i'm bored": "Same. Let's do something then.",
    "you're cool": "I know.",
    "you're dumb": "Rude. But I'll remember that.",
    "what time is it": datetime.datetime.now().strftime("It's %I:%M %p right now."),
    "good night": "Rest up. I'll be here when you wake up.",
    "good morning": "Morning. You ready for the day?",
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user = request.json.get("message", "").lower().strip()
    response = ""
    current_user = session.get("user_name")

    if user == "what is the weather":
        response = get_weather()
    elif user in roblox:
        response = "Here's the Lua code:\n" + roblox[user]

    # 1. REMEMBER NEW NAMES IN THE DATABASE
    elif user.startswith("my name is "):
        name = user.replace("my name is ", "").strip().title()
        session["user_name"] = name

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (name, fact) VALUES (?, ?)", (name, ""))
        conn.commit()
        conn.close()

        response = f"Got it. I'll save you to my database vault, {name}."

    # 2. CHECK NAME LOOKUP
    elif "what" in user and "name" in user:
        if current_user:
            response = f"Your name is {current_user}!"
        else:
            response = "I don't know your name yet. Tell me by saying: my name is [your name]"

    # 3. SAVE A FACT FOR THIS SPECIFIC PERSON
    elif user.startswith("remember that "):
        if current_user:
            fact = user.replace("remember that ", "").strip()

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET fact = ? WHERE name = ?", (fact, current_user))
            conn.commit()
            conn.close()

            response = f"Saved to your database profile, {current_user}. I won't forget."
        else:
            response = "Tell me your name first by saying 'my name is [name]' so I know who I'm saving this fact for!"

    # 4. ASK WHAT ZIMMA KNOWS ABOUT YOU
    elif user == "what do you remember":
        if current_user:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT fact FROM users WHERE name = ?", (current_user,))
            row = cursor.fetchone()
            conn.close()

            if row and row[0]:
                response = f"Your name is {current_user}, and my database vault says: '{row[0]}'."
            else:
                response = f"I know your name is {current_user}, but you haven't given me any facts to lock in the vault yet!"
        else:
            response = "I don't remember anything because I don't know who you are yet!"

    # 5. WIPE JUST YOUR PROFILE FROM DATABASE
    elif user == "forget everything":
        if current_user:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE name = ?", (current_user,))
            conn.commit()
            conn.close()
            session.pop("user_name", None)
            response = "Done. I wiped your database vault profile clean."
        else:
            response = "I don't know who you are, so there is nothing to forget!"

    elif user == "roblox help":
        response = "Ask me: " + ", ".join(roblox.keys())
    elif user in responses:
        response = responses[user]
    else:
        response = "I don't know that yet, but I'm learning."

    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")