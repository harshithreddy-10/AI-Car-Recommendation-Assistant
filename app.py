from flask import Flask, render_template, request
from google import genai
import os

app = Flask(__name__)

# Initialize the Gemini Client
# It automatically picks up the GEMINI_API_KEY from your environment variables
# NEW FOOLPROOF BLOCK FOR LOCAL PROTOTYPING
import os

# Option A: Forcefully write it into the system memory via Python
os.environ["GEMINI_API_KEY"] = "YOUR_ACTUAL_GEMINI_API_KEY_HERE"

try:
    # Option B: Pass it directly into the Client initialization
    client = genai.Client(api_key="YOUR_ACTUAL_GEMINI_API_KEY_HERE")
    print("Success: Gemini Client initialized successfully!")
    
except Exception as e:
    print(f"Error initializing client: {e}")
# 1. The Mock Database
car_fleet = [
    {
        "id": 1,
        "model": "Suzuki Dzire",
        "type": "Sedan",
        "passengers": 4,
        "luggage_capacity": 2,
        "daily_rate": 2000,
        "features": "Economical, AC, perfect for city driving"
    },
    {
        "id": 2,
        "model": "Toyota Innova Crysta",
        "type": "SUV",
        "passengers": 6,
        "luggage_capacity": 4,
        "daily_rate": 4500,
        "features": "Premium comfort, extra legroom, rear AC vents"
    },
    {
        "id": 3,
        "model": "Force Traveler",
        "type": "Van",
        "passengers": 12,
        "luggage_capacity": 8,
        "daily_rate": 8000,
        "features": "Spacious, push-back seats, ideal for large groups"
    }
]

# 2. The Filtering Logic
def get_suitable_cars(passengers, luggage, budget):
    suitable_cars = []
    for car in car_fleet:
        if (car["passengers"] >= passengers and 
            car["luggage_capacity"] >= luggage and 
            car["daily_rate"] <= budget):
            suitable_cars.append(car)
    return suitable_cars

# 3. The GenAI Pitch Generator
def generate_pitch(user_trip, car_match):
    prompt = f"""
    You are a professional customer service agent for a car rental company. 
    A customer is planning a: '{user_trip}'.
    
    Based on their passenger count and luggage, our system has selected the {car_match['model']} 
    at a rate of ₹{car_match['daily_rate']} per day.
    
    Write a short, friendly, and persuasive message (max 3 sentences) explaining why 
    the {car_match['model']} is the perfect vehicle for their specific trip. 
    Highlight its key features: {car_match['features']}.
    """
    
    try:
        # Using the recommended gemini-2.5-flash model for fast text generation
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generating pitch: {str(e)}"

# 4. Web Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    
    if request.method == 'POST':
        # Retrieve form data
        trip_type = request.form.get('trip_type')
        passengers = int(request.form.get('passengers', 0))
        luggage = int(request.form.get('luggage', 0))
        budget = int(request.form.get('budget', 0))
        
        # Run standard programming logic
        matched_cars = get_suitable_cars(passengers, luggage, budget)
        
        if matched_cars:
            # We pick the first match (or you could sort by price/features)
            best_match = matched_cars[0]
            # Hand over the matched details to GenAI
            ai_pitch = generate_pitch(trip_type, best_match)
            
            result = {
                "car": best_match,
                "pitch": ai_pitch
            }
        else:
            error = "No vehicles currently match your requirements or budget. Please adjust your criteria."
            
    return render_template('index.html', result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)
