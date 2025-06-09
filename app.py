from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# app.py

# … your imports …

# ─── sample assisted‐living facilities ───────────────────────────────
ASSISTED_LIVING_FACILITIES = {
    "90210": [
        {
            "name": "Sunset Villa Assisted Living",
            "address": "123 Beverly Dr, Beverly Hills, CA 90210",
            "phone": "(310) 555-0100",
            "website": "https://sunsetvilla.example.com"
        },
        {
            "name": "Beverly Gardens Senior Living",
            "address": "456 Maple St, Beverly Hills, CA 90210",
            "phone": "(310) 555-0200",
            "website": "https://beverlygardens.example.com"
        },
        {
            "name": "Rodeo Senior Residence",
            "address": "789 Rodeo Rd, Beverly Hills, CA 90210",
            "phone": "(310) 555-0300",
            "website": "https://rodeosenior.example.com"
        }
    ]
}

# Survey questions configuration
QUESTIONS = [
    {
        'id': 'ageRange',
        'title': 'What is your age range?',
        'icon': 'user',
        'type': 'radio',
        'options': [
            {'value': '50-55', 'label': '50-55 years old'},
            {'value': '55-65', 'label': '55-65 years old'},
            {'value': '65+', 'label': '65+ years old'},
        ]
    },
    {
        'id': 'budget',
        'title': 'What is your monthly budget?',
        'icon': 'dollar-sign',
        'type': 'radio',
        'options': [
            {'value': 'under-2000', 'label': 'Under $2,000 per month'},
            {'value': '2000-4000', 'label': '$2,000 - $4,000 per month'},
            {'value': '4000-6000', 'label': '$4,000 - $6,000 per month'},
            {'value': 'over-6000', 'label': 'Over $6,000 per month'},
        ]
    },
    {
        'id': 'livingArrangement',
        'title': 'What type of living arrangement do you prefer?',
        'icon': 'building',
        'type': 'radio',
        'options': [
            {'value': 'independent', 'label': 'Independent Living - I want to maintain my independence'},
            {'value': 'assisted', 'label': 'Assisted Living - I\'d like some help with daily activities'},
            {'value': 'memory-care', 'label': 'Memory Care - I need specialized memory support'},
        ]
    },
    {
        'id': 'activities',
        'title': 'What activities interest you most?',
        'subtitle': 'Select all that apply',
        'icon': 'activity',
        'type': 'checkbox',
        'options': [
            {'value': 'fitness', 'label': 'Fitness and Exercise'},
            {'value': 'arts-crafts', 'label': 'Arts and Crafts'},
            {'value': 'gardening', 'label': 'Gardening'},
            {'value': 'reading', 'label': 'Reading and Book Clubs'},
            {'value': 'music', 'label': 'Music and Entertainment'},
            {'value': 'cooking', 'label': 'Cooking and Dining'},
            {'value': 'games', 'label': 'Games and Puzzles'},
            {'value': 'volunteering', 'label': 'Volunteering and Community Service'},
        ]
    },
    {
        'id': 'schedule',
        'title': 'How do you prefer to spend your days?',
        'icon': 'clock',
        'type': 'radio',
        'options': [
            {'value': 'structured', 'label': 'I like a structured routine with planned activities'},
            {'value': 'flexible', 'label': 'I prefer flexibility to choose what I do each day'},
            {'value': 'spontaneous', 'label': 'I\'m spontaneous and like to go with the flow'},
        ]
    },
    {
        'id': 'socialLevel',
        'title': 'How would you describe your social preferences?',
        'icon': 'users',
        'type': 'radio',
        'options': [
            {'value': 'very-social', 'label': 'Very social - I love meeting new people and group activities'},
            {'value': 'moderately-social', 'label': 'Moderately social - I enjoy some social activities'},
            {'value': 'private', 'label': 'I prefer privacy and quiet time to myself'},
        ]
    },
    {
        'id': 'location',
        'title': 'Where would you prefer to live?',
        'icon': 'navigation',
        'type': 'radio',
        'options': [
            {'value': 'urban', 'label': 'Urban area - Close to city amenities and services'},
            {'value': 'suburban', 'label': 'Suburban area - Quiet neighborhoods with some amenities'},
            {'value': 'rural', 'label': 'Rural area - Peaceful countryside setting'},
        ]
    },
    {
        'id': 'geographic',
        'title': 'Where in the United States would you like to live?',
        'subtitle': 'Enter your preferred zip code and how far you\'re willing to travel',
        'icon': 'map-pin',
        'type': 'geographic',
        'options': []
    },
    {
        'id': 'amenities',
        'title': 'Which amenities are most important to you?',
        'subtitle': 'Select all that are important',
        'icon': 'wrench',
        'type': 'checkbox',
        'options': [
            {'value': 'healthcare', 'label': 'On-site Healthcare Services'},
            {'value': 'dining', 'label': 'Restaurant-style Dining'},
            {'value': 'transportation', 'label': 'Transportation Services'},
            {'value': 'fitness', 'label': 'Fitness Center and Wellness Programs'},
            {'value': 'social-activities', 'label': 'Social Activities and Events'},
            {'value': 'housekeeping', 'label': 'Housekeeping Services'},
            {'value': 'maintenance', 'label': 'Home Maintenance'},
            {'value': 'security', 'label': '24/7 Security'},
        ]
    },
    {
        'id': 'communityType',
        'title': 'What type of community appeals to you most?',
        'icon': 'shield',
        'type': 'radio',
        'options': [
            {'value': 'active-adult', 'label': 'Active Adult Community - Focus on activities, fitness, and wellness'},
            {'value': 'full-service', 'label': 'Full Service Community - Comprehensive care and amenities'},
            {'value': 'continuing-care', 'label': 'Continuing Care Community - Multiple levels of care as needs change'},
        ]
    }
]

def init_session():
    """Initialize session data if not present"""
    if 'survey_data' not in session:
        session['survey_data'] = {}
    if 'current_step' not in session:
        session['current_step'] = 0

def get_conversation_history():
    """Get conversation history based on completed questions"""
    history = []
    current_step = session.get('current_step', 0)
    survey_data = session.get('survey_data', {})
    
    for i in range(current_step):
        if i < len(QUESTIONS):
            question = QUESTIONS[i]
            value = survey_data.get(question['id'])
            
            if value:
                answer = ""
                if question['type'] == 'geographic':
                    if isinstance(value, dict) and value.get('zipCode') and value.get('radius'):
                        radius_text = "anywhere in the state" if value['radius'] == 'anywhere' else f"within {value['radius']} miles"
                        answer = f"Zip code {value['zipCode']}, {radius_text}"
                elif question['type'] == 'checkbox':
                    if isinstance(value, list) and value:
                        selected_options = [opt['label'] for opt in question['options'] if opt['value'] in value]
                        answer = ", ".join(selected_options)
                else:
                    selected_option = next((opt['label'] for opt in question['options'] if opt['value'] == value), "")
                    answer = selected_option
                
                if answer:
                    history.append({
                        'question': question['title'],
                        'answer': answer,
                        'icon': question['icon']
                    })
    
    return history

def generate_recommendations(survey_data):
    """Generate personalized recommendations based on survey data"""
    recommendations = []
    
    # Base recommendation
    base_rec = {
        'title': 'Comfort Living Community',
        'description': 'A well-rounded senior living community offering a balance of independence, care, and social opportunities.',
        'features': ['Flexible Care Options', 'Dining Services', 'Activities', 'Transportation', 'Wellness Programs'],
        'matchPercentage': 78,
        'price': '$2,500 - $4,000/month',
        'location': 'Pleasant Valley, TX',
        'image': '/static/images/community-placeholder.jpg'
    }
    
    # Customize based on survey responses
    personalized_features = []
    why_recommended = []
    
    activities = survey_data.get('activities', [])
    if isinstance(activities, list):
        if 'fitness' in activities:
            personalized_features.extend(['State-of-the-art Fitness Center', 'Aquatic Therapy Pool', 'Walking Trails'])
            why_recommended.append('You expressed interest in fitness and exercise activities')
        
        if 'arts-crafts' in activities:
            personalized_features.extend(['Art Studio', 'Craft Workshops', 'Creative Arts Program'])
            why_recommended.append('You enjoy arts and crafts activities')
        
        if 'gardening' in activities:
            personalized_features.extend(['Community Garden', 'Greenhouse', 'Landscaping Club'])
            why_recommended.append('You have an interest in gardening')
    
    social_level = survey_data.get('socialLevel')
    if social_level == 'very-social':
        personalized_features.extend(['Daily Social Events', 'Community Clubhouse', 'Group Dining'])
        why_recommended.append('You prefer a very social environment with group activities')
    elif social_level == 'private':
        personalized_features.extend(['Private Patios', 'Quiet Reading Areas', 'Individual Dining Options'])
        why_recommended.append('You value privacy and quiet spaces')
    
    amenities = survey_data.get('amenities', [])
    if isinstance(amenities, list):
        if 'healthcare' in amenities:
            personalized_features.extend(['On-site Medical Center', '24/7 Nursing Staff', 'Wellness Clinic'])
            why_recommended.append('You prioritized on-site healthcare services')
        
        if 'dining' in amenities:
            personalized_features.extend(['Restaurant-style Dining', 'Multiple Meal Plans', 'Chef-prepared Meals'])
            why_recommended.append('You want quality dining services')
        
        if 'transportation' in amenities:
            personalized_features.extend(['Scheduled Transportation', 'Medical Appointment Shuttle', 'Shopping Trips'])
            why_recommended.append('You need reliable transportation services')
    
    # Create personalized recommendation
    recommendation = base_rec.copy()
    if personalized_features:
        recommendation['personalizedFeatures'] = personalized_features
    else:
        recommendation['personalizedFeatures'] = base_rec['features']
    
    recommendation['whyRecommended'] = why_recommended
    recommendation['matchPercentage'] = min(95, 75 + len(why_recommended) * 5)
    
    # Add specific recommendations based on combinations
    community_type = survey_data.get('communityType')
    age_range = survey_data.get('ageRange')
    
    if community_type == 'active-adult' and age_range == '55-65':
        recommendation.update({
            'title': 'Sunset Gardens Active Living',
            'description': 'A vibrant 55+ community designed for active adults who want to maintain an independent lifestyle while enjoying resort-style amenities.',
            'location': 'Sunny Valley, CA',
            'price': '$2,800 - $4,200/month',
            'matchPercentage': 95
        })
    elif 'healthcare' in amenities and age_range == '65+':
        recommendation.update({
            'title': 'Heritage Care Community',
            'description': 'Full-service senior living with on-site healthcare, dining services, and a caring community atmosphere.',
            'location': 'Peaceful Pines, FL',
            'price': '$3,500 - $5,800/month',
            'matchPercentage': 88
        })
    elif social_level == 'very-social' and 'social-activities' in amenities:
        recommendation.update({
            'title': 'Harmony Heights Social Living',
            'description': 'A community-focused living environment with daily activities, clubs, and social events for those who love staying connected.',
            'location': 'Friendly Falls, AZ',
            'price': '$2,200 - $3,800/month',
            'matchPercentage': 92
        })
    return recommendation

@app.route('/')
def index():
    """Start or continue the survey"""
    init_session()
    return redirect(url_for('survey'))

@app.route('/survey')
def survey():
    """Display current survey question"""
    init_session()
    current_step = session.get('current_step', 0)
    
    if current_step >= len(QUESTIONS):
        return redirect(url_for('recommendations'))
    
    question = QUESTIONS[current_step]
    conversation_history = get_conversation_history()
    progress = ((current_step + 1) / len(QUESTIONS)) * 100
    
    return render_template('survey.html', 
                         question=question, 
                         current_step=current_step,
                         total_questions=len(QUESTIONS),
                         progress=progress,
                         conversation_history=conversation_history,
                         survey_data=session.get('survey_data', {}))

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    """Process survey answer and move to next question"""
    init_session()
    current_step = session.get('current_step', 0)
    
    if current_step >= len(QUESTIONS):
        return redirect(url_for('recommendations'))
    
    question = QUESTIONS[current_step]
    survey_data = session.get('survey_data', {})
    
    if question['type'] == 'checkbox':
        # Handle multiple selections
        values = request.form.getlist(question['id'])
        survey_data[question['id']] = values
    elif question['type'] == 'geographic':
        # Handle geographic data
        zip_code = request.form.get('zipCode', '').strip()
        radius = request.form.get('radius', '').strip()
        survey_data[question['id']] = {
            'zipCode': zip_code,
            'radius': radius
        }
    else:
        # Handle single selection
        value = request.form.get(question['id'], '').strip()
        survey_data[question['id']] = value
    
    session['survey_data'] = survey_data
    session['current_step'] = current_step + 1
    
    return redirect(url_for('survey'))

@app.route('/previous')
def previous_question():
    """Go back to previous question"""
    init_session()
    current_step = session.get('current_step', 0)
    if current_step > 0:
        session['current_step'] = current_step - 1
    return redirect(url_for('survey'))

@app.route('/recommendations')
def recommendations():
    """Display personalized recommendations"""
    init_session()
    survey_data = session.get('survey_data', {})
    
    if not survey_data:
        return redirect(url_for('survey'))
    
    recommendation = generate_recommendations(survey_data)
    conversation_history = get_conversation_history()
    
    return render_template('dummy_recommendations.html')

@app.route('/restart')
def restart_survey():
    """Restart the survey"""
    session.clear()
    return redirect(url_for('survey'))

if __name__ == '__main__':
    app.run(debug=True)
