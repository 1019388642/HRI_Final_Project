import cv2
from cv2 import aruco
from naoqi import ALProxy
import random
import numpy as np
import time
import threading
Nao_ip = '192.168.1.55'
Nao_port = 9559
ARUCO_DICT = {"DICT_5X5_50": cv2.aruco.DICT_5X5_50}#, "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
              #"DICT_5X5_250": cv2.aruco.DICT_5X5_250, "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000}

def ArUCOdetection(img):
  #for (arname, arDict) in ARUCO_DICT:
  dict_ar = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)
  param_ar = cv2.aruco.DetectorParameters_create()
  (corners, ids, rejected) = cv2.aruco.detectMarkers(img, dict_ar, parameters=param_ar)
  return len(corners)

def neckRegulator(motion_proxy):

  motion_proxy.setStiffnesses(['HeadYaw', 'HeadPitch'], [1.0, 1.0])

  motion_proxy.angleInterpolationWithSpeed('Head', [0., 0.], 0.2)#[1., 1.], isAbsolute=True)

def rock(motion_proxy):
  start = time.time()
  while (time.time() - start < 3):
    motion_proxy.closeHand('LHand')
  time.sleep(1)

def paper(motion_proxy):
  start = time.time()
  while (time.time() - start < 3):
    motion_proxy.openHand('LHand')
    motion_proxy.angleInterpolationWithSpeed('LWristYaw', -1, 1)
  time.sleep(1)

def scissors(motion_proxy):
  start = time.time()
  while (time.time() - start < 3):
    motion_proxy.setAngles(['LHand'], [0.5], 0.9)
    motion_proxy.angleInterpolationWithSpeed('LWristYaw', 1, 1)
  time.sleep(1)

def shakingArm(motion_proxy, tts_proxy, rand_gest):
  word = ['One', 'Two', 'Three']
  for i in range(3):
    #motion_proxy.angleInterpolationWithSpeed(['LHand'], [0.0], 0.9)
    motion_proxy.angleInterpolationWithSpeed('LShoulderPitch', -0.1, 0.8)
    tts_proxy.say(word[i])
    #time.sleep(0.1)
    motion_proxy.angleInterpolationWithSpeed('LShoulderPitch', 0.3, 0.8)
    #time.sleep(0.1)
  tts_proxy.say(rand_gest)
  #time.sleep(0.1)
  if rand_gest == 'rock':
    motion_proxy.angleInterpolationWithSpeed('LShoulderPitch', -0.3, 0.5)
    rock(motion_proxy)
    time.sleep(2)
  elif rand_gest == 'paper':
    motion_proxy.angleInterpolationWithSpeed('LShoulderPitch', -0.3, 0.5)
    paper(motion_proxy)
    time.sleep(2)
  else:
    motion_proxy.angleInterpolationWithSpeed('LShoulderPitch', 0.3, 0.5)
    scissors(motion_proxy)
    time.sleep(2)

def arTagReco(videoProxy, subscriber):
  img = videoProxy.getImageRemote(subscriber)
  if img != None:

    width = img[0]
    height = img[1]
    layer = img[2]
    array = img[6]
    img_str = str(bytearray(array))
    image = np.fromstring(img_str, np.uint8).reshape(height, width, layer)
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resize_img = cv2.resize(gray_img, (800, 800))
    num = ArUCOdetection(resize_img)
    if num == None:
      num = 0
    return num
def judge(gesture_rand, gesture_reco):
  if gesture_rand == 'rock':
    if gesture_reco == 1:
      return 'Fair'
    elif gesture_reco == 2:
      return 'Lose'
    elif gesture_reco == 3:
      return 'Win'
  elif gesture_rand == 'paper':
    if gesture_reco == 1:
      return 'Lose'
    elif gesture_reco == 2:
      return 'Win'
    elif gesture_reco == 3:
      return 'Fair'
  elif gesture_rand == 'scissor':
    if gesture_reco == 1:
      return 'Win'
    elif gesture_reco == 2:
      return 'Fair'
    elif gesture_reco == 3:
      return 'Lose'


def main():
  proxy = ALProxy("ALVideoDevice", Nao_ip, Nao_port)
  tts = ALProxy("ALTextToSpeech", Nao_ip, Nao_port)

  touch = ALProxy('ALTouch', Nao_ip, Nao_port)

  subscriber = proxy.subscribeCamera("demo", 0, 3, 13, 1)
  motion_proxy = ALProxy('ALMotion', Nao_ip, Nao_port)
  neckRegulator(motion_proxy)
  start_time = time.time()
  while(True):
    time.sleep(0.1)
    trigger = (touch.getStatus()[0][1])
    if time.time() - start_time > 10:
      tts.say("Do you want to play a game? Then know my head!")
      start_time = time.time()
    if trigger == True:
      print('yes')
      tts.say("OK! Let's play!")
      time.sleep(0.5)
      rand_gesture = random.choice(['rock', 'paper', 'scissor'])

      shakingArm(motion_proxy, tts, rand_gesture)

      num = arTagReco(proxy, subscriber)
      while num == None or num == 0:
        num = arTagReco(proxy, subscriber)
      print(num, rand_gesture)
      result = judge(rand_gesture, num)
      if result == 'Fair':
        tts.say('What a pity! You almost Win!')
      elif result == 'Win':
        tts.say('Congrates! Human beats AI')
      else:
        tts.say('No way! I win ha ha ha')
      time.sleep(2)
      tts.say('This round is over, do  you want to play one more time?')
      time.sleep(1)



main()


