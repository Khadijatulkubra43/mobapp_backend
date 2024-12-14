import os, csv
import dlib
from django.conf import settings

# Function to load makeup looks from CSV file
def load_looks_from_csv(file_path):
    looks = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            looks.append({
                'id': row['id'],
                'lipstick': (int(row['lipstick_b']), int(row['lipstick_g']), int(row['lipstick_r'])),
                'blush': (int(row['blush_b']), int(row['blush_g']), int(row['blush_r'])),
                'lens': (int(row['lens_b']), int(row['lens_g']), int(row['lens_r']))
            })
    return looks

# Face detector and landmark predictor
model_path = os.path.join(settings.BASE_DIR, 'data', 'shape_predictor_68_face_landmarks.dat')
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(model_path)
# Load predefined makeup looks
dataset_file = os.path.join(settings.BASE_DIR, 'data', 'colors.csv')
looks = load_looks_from_csv(dataset_file)
current_look_indices = [0, 1, 2]  # Start with the first 3 looks