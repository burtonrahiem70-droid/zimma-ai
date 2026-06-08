from flask import Flask, request, jsonify, render_template
import datetime
import requests
import json
import os
import random

app = Flask(__name__)

MEMORY_FILE = "zimma_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

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
    memory = load_memory()
    user = request.json.get("message", "").lower()
    response = ""

    if user == "what is the weather":
        response = get_weather()
    elif user in roblox:
        response = "Here's the Lua code:\n" + roblox[user]
    elif user.startswith("my name is "):
        name = user.replace("my name is ", "").strip().title()
        memory["name"] = name
        save_memory(memory)
        response = f"Got it. I'll remember that, {name}."
    elif user.startswith("remember that "):
        fact = user.replace("remember that ", "").strip()
        memory["fact"] = fact
        save_memory(memory)
        response = "Saved. I won't forget."
    elif user == "what do you remember":
        response = str(memory) if memory else "I don't have anything saved yet."
    elif user == "forget everything":
        save_memory({})
        response = "Done. Memory cleared."
    elif user == "roblox help":
        response = "Ask me: " + ", ".join(roblox.keys())
    elif user in responses:
        response = responses[user]
    else:
        response = "I don't know that yet, but I'm learning."

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")