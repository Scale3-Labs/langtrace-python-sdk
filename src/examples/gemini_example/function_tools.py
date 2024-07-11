tools = [
    {
        "function_declarations": [
            {
                "name": "find_movies",
                "description": "find movie titles currently playing in theaters based on any description, genre, title words, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA or a zip code e.g. 95616",
                        },
                        "description": {
                            "type": "string",
                            "description": "Any kind of description including category or genre, title words, attributes, etc.",
                        },
                    },
                    "required": ["description"],
                },
            },
            {
                "name": "find_theaters",
                "description": "find theaters based on location and optionally movie title which is currently playing in theaters",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA or a zip code e.g. 95616",
                        },
                        "movie": {"type": "string", "description": "Any movie title"},
                    },
                    "required": ["location"],
                },
            },
            {
                "name": "get_showtimes",
                "description": "Find the start times for movies playing in a specific theater",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA or a zip code e.g. 95616",
                        },
                        "movie": {"type": "string", "description": "Any movie title"},
                        "theater": {
                            "type": "string",
                            "description": "Name of the theater",
                        },
                        "date": {
                            "type": "string",
                            "description": "Date for requested showtime",
                        },
                    },
                    "required": ["location", "movie", "theater", "date"],
                },
            },
        ]
    }
]
