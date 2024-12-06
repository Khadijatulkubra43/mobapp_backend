import cv2
import numpy as np
import dlib
import csv
import os

# Webcam control and upload control
use_webcam = False  # Set to True to use webcam
uploaded_img_path = '2.png'  # The path to the uploaded image

# Face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Function to create a mask for facial regions
def createMask(img, points):
    mask = np.zeros_like(img)
    mask = cv2.fillPoly(mask, [points], (255, 255, 255))
    return mask

# Function to load makeup looks from CSV file by style
def load_looks_by_style(file_path, selected_style):
    looks = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['style'].lower() == selected_style.lower():
                looks.append({
                    'id': row['id'],
                    'lipstick': (int(row['lipstick_b']), int(row['lipstick_g']), int(row['lipstick_r'])),
                    'blush': (int(row['blush_b']), int(row['blush_g']), int(row['blush_r'])),
                    'lens': (int(row['lens_b']), int(row['lens_g']), int(row['lens_r']))
                })
    return looks

# Prompt user to input desired makeup style
selected_style = input("Enter the makeup style (e.g., 'party', 'wedding', 'casual'): ")

# Load predefined makeup looks based on user-selected style
looks = load_looks_by_style('data/makeup_styles.csv', selected_style)
if not looks:
    print(f"No looks found for the style '{selected_style}'.")
    exit()

current_look_indices = [0, 1, 2] if len(looks) >= 3 else list(range(len(looks)))

# Function to calculate a heuristic score for a look
def calculate_look_score(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    contrast = np.std(gray)
    score = brightness * 0.5 + contrast * 0.5
    return score

# Function to apply makeup
def apply_makeup(img, selected_look):
    imgOriginal = img.copy()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(imgGray)

    if len(faces) == 0:
        print("No faces detected.")
        return imgOriginal

    for face in faces:
        landmarks = predictor(imgGray, face)
        myPoints = []
        for n in range(68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            myPoints.append([x, y])
        myPoints = np.array(myPoints)

        # Lips makeup
        imgLips = createMask(img, myPoints[48:61])
        imgColorLips = np.zeros_like(imgLips)
        imgColorLips[:] = selected_look['lipstick']
        imgColorLips = cv2.bitwise_and(imgLips, imgColorLips)
        imgColorLips = cv2.GaussianBlur(imgColorLips, (7, 7), 10)
        imgFinal = cv2.addWeighted(imgOriginal, 1, imgColorLips, 0.4, 0)

        # Blush on cheeks
        leftCheekPoints = np.array([myPoints[1], myPoints[2], myPoints[3], myPoints[31], myPoints[30]])
        rightCheekPoints = np.array([myPoints[15], myPoints[14], myPoints[13], myPoints[35], myPoints[30]])

        imgLeftCheek = createMask(img, leftCheekPoints)
        imgRightCheek = createMask(img, rightCheekPoints)

        imgColorBlushLeft = np.zeros_like(imgLeftCheek)
        imgColorBlushRight = np.zeros_like(imgRightCheek)
        imgColorBlushLeft[:] = selected_look['blush']
        imgColorBlushRight[:] = selected_look['blush']

        imgBlushLeft = cv2.bitwise_and(imgLeftCheek, imgColorBlushLeft)
        imgBlushRight = cv2.bitwise_and(imgRightCheek, imgColorBlushRight)
        imgBlushLeft = cv2.GaussianBlur(imgBlushLeft, (15, 15), 10)
        imgBlushRight = cv2.GaussianBlur(imgBlushRight, (15, 15), 10)

        imgFinal = cv2.addWeighted(imgFinal, 1, imgBlushLeft, 0.4, 0)
        imgFinal = cv2.addWeighted(imgFinal, 1, imgBlushRight, 0.4, 0)

        # Eyeshadow/Lenses
        imgLeftEye = createMask(img, myPoints[36:42])
        imgRightEye = createMask(img, myPoints[42:48])

        imgColorLensLeft = np.zeros_like(imgLeftEye)
        imgColorLensRight = np.zeros_like(imgRightEye)
        imgColorLensLeft[:] = selected_look['lens']
        imgColorLensRight[:] = selected_look['lens']

        imgLensLeft = cv2.bitwise_and(imgLeftEye, imgColorLensLeft)
        imgLensRight = cv2.bitwise_and(imgRightEye, imgColorLensRight)
        imgLensLeft = cv2.GaussianBlur(imgLensLeft, (7, 7), 10)
        imgLensRight = cv2.GaussianBlur(imgLensRight, (7, 7), 10)

        imgFinal = cv2.addWeighted(imgFinal, 1, imgLensLeft, 0.4, 0)
        imgFinal = cv2.addWeighted(imgFinal, 1, imgLensRight, 0.4, 0)

        return imgFinal

# Main loop
while True:
    if use_webcam:
        cap = cv2.VideoCapture(0)
        success, img = cap.read()
        if not success:
            print("Failed to capture from webcam.")
            break
    else:
        if not os.path.isfile(uploaded_img_path):
            print(f"File '{uploaded_img_path}' does not exist. Please check the path.")
            break
        img = cv2.imread(uploaded_img_path)
        if img is None:
            print("Failed to load uploaded image.")
            break

    img = cv2.resize(img, (380, 380))

    imgs_with_makeup = []
    look_scores = []
    for idx in current_look_indices:
        img_with_makeup = apply_makeup(img, looks[idx])
        if img_with_makeup is not None:
            imgs_with_makeup.append(img_with_makeup)
            look_score = calculate_look_score(img_with_makeup)
            look_scores.append(look_score)

    best_suggestion_idx = np.argmax(look_scores)
    for i, img_with_makeup in enumerate(imgs_with_makeup):
        window_name = f"Look {i + 1}"
        if i == best_suggestion_idx:
            window_name += " (Best Suggestion)"
        cv2.imshow(window_name, img_with_makeup)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('n'):
        current_look_indices = [(i + 3) % len(looks) for i in current_look_indices]
    elif key == ord('q'):
        break

if use_webcam and cap is not None:
    cap.release()

cv2.destroyAllWindows()
