# utils/muscle_mapper.py

MUSCLE_GROUPS = {
    'chest': ['bench press', 'chest fly', 'push up', 'pec deck', 'incline press', 'decline press', 'dumbbell press', 'machine fly', 'smith machine bench press'],
    'back': ['pull up', 'row', 'lat pulldown', 'deadlift', 'back extension', 'cable row', 'dumbbell row', 't-bar row', 'machine row', 'face pull'],
    'shoulders': ['overhead press', 'lateral raise', 'front raise', 'shoulder press', 'arnold press', 'upright row', 'behind the neck barbell press'],
    'biceps': ['bicep curl', 'hammer curl', 'preacher curl', 'concentration curl', 'cable curl', 'barbell curl', 'seated dumbbell curl'],
    'triceps': ['tricep pushdown', 'skull crusher', 'tricep extension', 'dip', 'close grip press', 'rod pushdown', 'rope overhead'],
    'legs': ['squat', 'leg press', 'leg extension', 'leg curl', 'lunge', 'calf raise', 'hack squat', 'barbell squat', 'dumbbell squat', 'romanian deadlift', 'adductor machine', 'lying leg curl'],
    'glutes': ['hip thrust', 'glute bridge', 'bulgarian split squat', 'sumo squat', 'glute kickback'],
    'core': ['plank', 'crunch', 'leg raise', 'russian twist', 'sit up', 'hanging leg raise'],
    'forearms': ['wrist curl', 'reverse wrist curl', 'farmer carry'],
    'cardio': ['running', 'cycling', 'rowing', 'swimming', 'jump rope', 'elliptical']
}

def get_muscle_group(exercise_name):
    """Map exercise name to muscle group"""
    if not exercise_name:
        return 'other'
    exercise_name_lower = exercise_name.lower()
    for group, exercises in MUSCLE_GROUPS.items():
        for exercise in exercises:
            if exercise in exercise_name_lower:
                return group
    return 'other'

def get_muscle_groups_from_workout(exercise_names):
    """Extract muscle groups from exercise names"""
    muscle_counts = {}
    for exercise in exercise_names:
        muscle = get_muscle_group(exercise)
        muscle_counts[muscle] = muscle_counts.get(muscle, 0) + 1
    return muscle_counts