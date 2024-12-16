import cv2
import numpy as np
from .models import detector, predictor

# Function to create a mask for facial regions
def createMask(img, points):
    mask = np.zeros_like(img)
    mask = cv2.fillPoly(mask, [points], (255, 255, 255))
    return mask

# Function to calculate a heuristic score for a look
def calculate_look_score(img):
    # Convert image to grayscale to calculate brightness and contrast
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Calculate the average brightness
    brightness = np.mean(gray)
    
    # Calculate contrast as the standard deviation of pixel intensity
    contrast = np.std(gray)
    
    # Score based on a combination of brightness and contrast
    score = brightness * 0.5 + contrast * 0.5
    
    return score

def apply_makeup(img, selected_look):
    imgOriginal = img.copy()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY )
    try:
        faces = detector(imgGray)
    except Exception as e:
        print(e)
        return imgGray


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

        # Add blush to the final image
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

        # Add eyeshadow to the final image
        imgFinal = cv2.addWeighted(imgFinal, 1, imgLensLeft, 0.4, 0)
        imgFinal = cv2.addWeighted(imgFinal, 1, imgLensRight, 0.4, 0)

        return imgFinal
