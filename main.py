import cv2
import mediapipe as mp
import pyautogui
import keyboard as kb
import win32api, win32con
import configparser

parser = configparser.ConfigParser()
parser.read("config.ini")

DISTPATH = ""

usingRelative = False # Determine mouse movement

smoothing = parser.getboolean('DEFAULT','smoothing') # Absolute smoothing
smoothingValue = parser.getint('DEFAULT','smoothingValue') # Determine how much smoothing (Kinda chunky)
offsetx = parser.getint('DEFAULT','offsetx')
offsety = parser.getint('DEFAULT','offsety')
absoluteareax = parser.getfloat('DEFAULT','absoluteareax')
absoluteareay = parser.getfloat('DEFAULT','absoluteareay')
absoluteoffsetx = parser.getfloat('DEFAULT','absoluteoffsetx')
absoluteoffsety = parser.getfloat('DEFAULT','absoluteoffsety')
relativesensx = parser.getint('DEFAULT','relativesensx')
relativesensy = parser.getint('DEFAULT','relativesensy')
clickenabled = parser.getboolean('DEFAULT','clickenabled')
thumbclicklenancy = parser.getfloat('DEFAULT','thumbclicklenancy')
displayWebcam = parser.getboolean('DEFAULT','displayWebcam')
switchstylebind = parser.get('DEFAULT','switchstylebind')
exitkey = parser.get('DEFAULT','exitkey')

maxnumhands = parser.getint('TRACKING-SENSITIVITY', 'maxnumhands')
detectionconfidence = parser.getfloat('TRACKING-SENSITIVITY', 'detectionconfidence')
trackingconfidence = parser.getfloat('TRACKING-SENSITIVITY', 'trackingconfidence')

pastX = 0
pastY = 0
difX = 0.0
difY = 0.0

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.08

cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=maxnumhands,
                      min_detection_confidence=detectionconfidence,
                      min_tracking_confidence=trackingconfidence)
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0
finalx = 960.0
finaly = 540.0

def mapToScreenX(val):
    global pastX
    global finalx
    # 65535 pixels
    scale = 65535/absoluteareax
    finalx = scale - (scale * (val+absoluteoffsetx))
    finalx = min(scale, finalx)
    finalx = max(0, finalx)
    smoothResX = scale/1920
    if smoothing and abs(finalx - pastX) > (smoothResX * smoothingValue):
        pastX = finalx
        return int(pastX)
    elif not smoothing:
        return int(finalx)
    else:
        return int(pastX)

def mapToScreenY(val):
    global pastY
    global finaly
    scale = 65535/absoluteareay
    val = 1-val
    finaly = scale - (scale *(val+absoluteoffsety))
    print(val)
    finaly = min(scale, finaly)
    finaly = max(0, finaly)
    smoothResY = scale/1080
    if smoothing and abs(finaly - pastY) > (smoothResY * smoothingValue):
        pastY = finaly
        return int(pastY)
    elif not smoothing:
        return int(finaly)
    else:
        return int(pastY)


def relativeFPS(lmx, lmy):
    global difX, difY
    lmx = int(lmx*100) - offsetx
    lmy = int(lmy*100) - offsety 
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(-lmx * relativesensx), int(lmy * relativesensy))

    difX = lmx
    difY = lmy

def triggerClick(ix, tx):
    if clickenabled:
        if abs(ix - tx) > thumbclicklenancy:
            pyautogui.click()


count = 0
  


while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lm1 = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
            lm2 = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_MCP]
            lm3 = handLms.landmark[mpHands.HandLandmark.THUMB_TIP]
            if usingRelative:
                relativeFPS(lm1.x, lm1.y)
                triggerClick(lm2.x, lm3.x)
            else:
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE,mapToScreenX(lm1.x), mapToScreenY(lm1.y))
                triggerClick(lm2.x, lm3.x)
            h, w, c = img.shape
            cx, cy = int(lm1.x *w), int(lm1.y*h)
            if id ==0:
                cv2.circle(img, (cx,cy), 3, (255,0,255), cv2.FILLED)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)


    if kb.is_pressed(switchstylebind):
        usingRelative = not usingRelative

    if displayWebcam:
        cv2.imshow("Image", img)
    cv2.waitKey(1)
    if kb.is_pressed(exitkey):
        exit()