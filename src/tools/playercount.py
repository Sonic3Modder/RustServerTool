import a2s

def get_players():
    try:
        address = ("127.0.0.1", 28015)
        return a2s.players(address)
    except Exception as e:
        print(f"Error retrieving player count: {e}")
        return []