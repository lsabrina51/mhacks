import flask
import bigHouses
import google.generativeai as genai
from google.generativeai import types 
import os
import json


def get_user_with_preferences(username):
    """Get user data with their housing preferences"""
    connection = bigHouses.model.get_db()
    
    user_data = connection.execute(
        """
        SELECT uniqname, name, budget, house_type_pref, room_type_pref, 
               move_in_date, move_out_date, car, img_url
        FROM users
        WHERE uniqname = ?
        """,
        (username,)
    ).fetchone()
    
    if user_data:
        return dict(user_data)
    return {}


def get_filtered_housing(user_data):
    """Get available housing that might match user preferences"""
    connection = bigHouses.model.get_db()
    
    # Get all housing posts with basic info and primary image
    housing_posts = connection.execute(
        """
        SELECT p.housing_id, p.monthly_rent, p.house_type, p.room_type,
               p.street_address, p.city, p.state, p.zip_code,
               p.distance_from_campus, p.parking, p.furnished,
               p.contact_student_uniqname,
               COALESCE(i.img_url, '/static/images/default-house.png') as image_url
        FROM posts p
        LEFT JOIN images i ON p.housing_id = i.housing_id AND i.img_order = 0
        ORDER BY p.housing_id DESC
        LIMIT 20
        """
    ).fetchall()
    
    return [dict(post) for post in housing_posts]

class RecommendationService:
    def __init__(self):
        # Configuration remains the same
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        # Using the same model as in your original class
        self.model = genai.GenerativeModel('gemini-pro') 
    
    # Helper method included for completeness/context based on the prompt's usage
    def format_housing_data(self, housing_list):
        """Formats the list of housing data into a string for the prompt."""
        formatted_list = []
        for item in housing_list:
            formatted_list.append(
                f"Housing ID: {item.get('housing_id')}, "
                f"Price: ${item.get('monthly_rent', 0)}/month, "
                f"House Type: {item.get('house_type', 'N/A')}, "
                f"Room Type: {item.get('room_type', 'N/A')}, "
                f"Location: {item.get('city', 'N/A')}, {item.get('state', 'N/A')}, "
                f"Distance to Campus: {item.get('distance_from_campus', 'N/A')} miles, "
                f"Parking: {'Yes' if item.get('parking') else 'No'}, "
                f"Furnished: {'Yes' if item.get('furnished') else 'No'}"
            )
        return "\n".join(formatted_list)
        
    def get_housing_recommendations(self, user_preferences, available_housing, dream_description=None):
        """Generate personalized housing recommendations with thinking disabled."""
        prompt = self.build_recommendation_prompt(user_preferences, available_housing, dream_description)
        
        # --- MODIFIED PART: Adding the thinking_config to the generate_content call ---
        response = self.model.generate_content(
            prompt,
            config=types.GenerateContentConfig(
                # Set thinking_budget to 0 to disable thinking
                thinking_config=types.ThinkingConfig(thinking_budget=0) 
            )
        )
        # --------------------------------------------------------------------------
        
        # Call the parser with available_housing data to map image URLs
        return self.parse_recommendations(response.text, available_housing) 
    
    def build_recommendation_prompt(self, user_prefs, housing_list, dream_description=None):
        """Builds the detailed prompt for the model."""
        budget = user_prefs.get('budget', 'Not specified')
        house_type = user_prefs.get('house_type_pref', 'Any')
        room_type = user_prefs.get('room_type_pref', 'Any')
        has_car = 'Yes' if user_prefs.get('car') else 'No'
        
        dream_place_text = ""
        if dream_description:
            dream_place_text = f"\n        - Dream Place Description: \"{dream_description}\""
        
        return f"""
        You are a housing recommendation expert. Based on this student's preferences:
        - Budget: ${budget}/month
        - Preferred House Type: {house_type}
        - Preferred Room Type: {room_type}
        - Has Car: {has_car}
        - Name: {user_prefs.get('name', 'Student')}{dream_place_text}
        
        Available housing options:
        {self.format_housing_data(housing_list)}
        
        Analyze these options and provide 3-5 personalized recommendations.
        {f"Pay special attention to matching the dream place description: '{dream_description}'" if dream_description else ""}
        Consider budget fit, location convenience, amenities match, and lifestyle compatibility.
        
        Return ONLY a valid JSON array in this exact format:
        [
            {{
                "housing_id": 123,
                "score": 8.5,
                "reason": "Perfect budget fit with great amenities{' and matches your dream place description' if dream_description else ''}",
                "monthly_rent": 1200,
                "address": "123 Main St, Ann Arbor, MI",
                "image_url": "image.jpg"
            }}
        ]
        """

    def parse_recommendations(self, response_text, available_housing=None):
        """
        Converts the raw JSON string from the model into a Python object.
        This is crucial for easy rendering in the Flask template.
        """
        try:
            # Clean up the response text
            clean_text = response_text.strip()
            
            # Remove markdown formatting if present
            if '```json' in clean_text:
                clean_text = clean_text.split('```json')[1].split('```')[0].strip()
            elif '```' in clean_text:
                clean_text = clean_text.replace('```', '').strip()
            
            # Parse JSON
            recommendations = json.loads(clean_text)
            
            # Ensure it's a list
            if not isinstance(recommendations, list):
                recommendations = [recommendations]
            
            # Map housing_ids to actual image URLs from available_housing data
            if available_housing:
                housing_map = {h['housing_id']: h for h in available_housing}
                for rec in recommendations:
                    housing_id = rec.get('housing_id')
                    if housing_id in housing_map:
                        rec['image_url'] = housing_map[housing_id].get('image_url', '/static/images/default-house.png')
                    else:
                        rec['image_url'] = '/static/images/default-house.png'
                
            return recommendations
            
        except (json.JSONDecodeError, IndexError, KeyError) as e:
            print(f"Error parsing recommendations JSON: {e}")
            print(f"Raw response: {response_text}")
            
            # Return fallback recommendations
            return [
                {
                    "housing_id": 0,
                    "score": 7.0,
                    "reason": "AI recommendations temporarily unavailable. Showing recent listings instead.",
                    "monthly_rent": 0,
                    "address": "Various locations",
                    "image_url": "/static/images/default-house.png"
                }
            ]

@bigHouses.app.route('/recommendations/')
def show_recommendations():
    """Show AI-powered housing recommendations"""
    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')
    
    logname = flask.session.get('username')
    
    try:
        # Get user data and preferences
        user_data = get_user_with_preferences(logname)
        available_housing = get_filtered_housing(user_data)
        
        # Generate recommendations - this now returns a Python list/dict
        if os.getenv('GOOGLE_API_KEY'):
            rec_service = RecommendationService()
            recommendations = rec_service.get_housing_recommendations(
                user_data, available_housing
            )
        else:
            # Fallback to simple recommendations without AI
            recommendations = get_simple_recommendations(user_data, available_housing)
        
        context = {
            "logname": logname,
            "recommendations": recommendations,
            "user_preferences": user_data
        }
        return flask.render_template("recommendations.html", **context)
        
    except Exception as e:
        print(f"Error in recommendations: {e}")
        # Fallback to explore page
        return flask.redirect('/explore/')


def get_simple_recommendations(user_data, available_housing):
    """Simple rule-based recommendations when AI is not available"""
    budget = user_data.get('budget', 999999)
    has_car = user_data.get('car', False)
    
    # Filter and score based on simple rules
    recommendations = []
    for housing in available_housing[:5]:  # Top 5
        score = 7.0  # Base score
        
        # Budget matching
        rent = housing.get('monthly_rent', 0)
        if rent <= budget:
            score += 1.0
        
        # Parking preference
        if has_car and housing.get('parking'):
            score += 0.5
        
        # Distance bonus (closer is better)
        distance = housing.get('distance_from_campus', 999)
        if distance < 2:
            score += 0.5
        
        recommendations.append({
            "housing_id": housing.get('housing_id'),
            "score": min(score, 10.0),
            "reason": f"Matches your budget and preferences",
            "monthly_rent": rent,
            "address": f"{housing.get('street_address', '')}, {housing.get('city', '')}, {housing.get('state', '')}",
            "image_url": housing.get('image_url', '/static/images/default-house.png')
        })
    
    return sorted(recommendations, key=lambda x: x['score'], reverse=True)