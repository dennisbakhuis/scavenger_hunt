import json


GAME_FILE = "data/game.json"


game = {
    "locations": [
        {
            "name": "Ladders", 
            "latitude": 52.21197114516794,
            "longitude": 6.884310991373106,  
            "description_file": "1_ladders.md",
            "options": [
                {"option": "Ladder A falls faster", "score": 1},
                {"option": "Ladder B falls faster", "score": -1},
                {"option": "They both fall equally fast", "score": -1},
                {"option": "I have no idea", "score": 0},
            ]
        },
        {
            "name": "Three doors", 
            "latitude": 52.21362018414284,
            "longitude": 6.876367666122294,
            "description_file": "2_three_doors.md",
            "options": [
                {"option": "Keep your originally chosen door", "score": -1},
                {"option": "Switch to another door", "score": 1},
                {"option": "It does not matter what you do", "score": -1},
                {"option": "I have no idea", "score": 0},
            ]
        },
        {
            "name": "Two kids", 
            "latitude": 52.209598123050185,
            "longitude": 6.881176148907194,
            "description_file": "3_two_kids.md",
            "options": [
                {"option": "1/2", "score": -1},
                {"option": "2/3", "score": -1},
                {"option": "1/3", "score": 1},
                {"option": "I have no idea", "score": 0},
            ]
        },
    ],
    "radius": 75,
}


with open(GAME_FILE, "w") as file:
    json.dump(game, file, indent=4, sort_keys=True)

