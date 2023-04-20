import cv2
from cv2 import aruco
from naoqi import ALProxy
import random
import numpy as np
import time

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
  #motion_proxy.angleInterpolationWithSpeed('LHand', 1.0, 0.5)
  motion_proxy.closeHand('LHand')
  #motion_proxy.setAngles(['LHand'], [0.0], 0.9)
  time.sleep(1)

def paper(motion_proxy):
  #motion_proxy.setAngles(['LHand'], [1.0], 0.9)
  motion_proxy.openHand('LHand')
  time.sleep(1)

def scissors(motion_proxy):
  motion_proxy.setAngles(['LHand'], [0.6], 0.9)
  time.sleep(1)

def shakingArm(motion_proxy, tts_proxy, rand_gest):
  word = ['rock', 'paper', 'scissor']
  for i in range(3):
    motion_proxy.angleInterpolationWithSpeed(['LHand'], [0.0], 0.9)
    motion_proxy.angleInterpolationWithSpeed('LShoulderPitch', -0.3, 0.3)
    tts_proxy.say(word[i])
    time.sleep(0.2)
    motion_proxy.angleInterpolationWithSpeed('LShoulderPitch', 0.3, 0.3)
    time.sleep(0.2)
  tts_proxy.say(rand_gest)
  time.sleep(0.2)
  if rand_gest == 'rock':
    print('1')
    motion_proxy.angleInterpolationWithSpeed('LShoulderPitch', -0.3, 0.3)
    rock(motion_proxy)
    time.sleep(2)
  elif rand_gest == 'paper':
    print('2')
    motion_proxy.angleInterpolationWithSpeed('LShoulderPitch', -0.3, 0.3)
    paper(motion_proxy)
    time.sleep(2)
  else:
    print('3')
    motion_proxy.angleInterpolationWithSpeed('LShoulderPitch', 0.3, 0.3)
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

def main():
  proxy = ALProxy("ALVideoDevice", Nao_ip, Nao_port)
  tts = ALProxy("ALTextToSpeech", Nao_ip, Nao_port)
  mem = ALProxy('ALMemory', Nao_ip, Nao_port)
  asr = ALProxy('ALSpeechRecognition', Nao_ip, Nao_port)
  touch = ALProxy('ALTouch', Nao_ip, Nao_port)
  #asr.setLanguage('English')
  #vocabulary = ['yes', 'no', 'ok']
  #asr.pause(True)
  #asr.setParameter('Sensitivity', 1)
  #asr.setParameter('NbHypotheses', 2)
  #asr.setVocabulary(vocabulary, True)
  #asr.pause(False)
  #asr.get
  #asr.subscribe('Test_ASR')
  #asr.setAudioExpression(True)
  #print(asr.getParameter('Sensitivity'))
  #print(asr.getAudioExpression())
  #time.sleep(20)
  subscriber = proxy.subscribeCamera("demo", 0, 3, 13, 1)
  motion_proxy = ALProxy('ALMotion', Nao_ip, Nao_port)
  neckRegulator(motion_proxy)
  scissors(motion_proxy)
  paper(motion_proxy)
  while(True):
    time.sleep(0.1)
    #num = arTagReco(proxy, subscriber)
    #shakingArm(motion_proxy, tts, rand_gesture)
    trigger = (touch.getStatus()[0][1])
    if trigger == True:
      print('yes')
      tts.say("OK! Let's play!")
      time.sleep(0.5)
      rand_gesture = random.choice(['rock', 'paper', 'scissor'])
      shakingArm(motion_proxy, tts, rand_gesture)
      num = arTagReco(proxy, subscriber)



main()


