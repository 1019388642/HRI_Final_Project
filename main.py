import cv2
from cv2 import aruco
from naoqi import ALProxy

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

def paper(motion_proxy):
  motion_proxy.openHand('LHand')

def scissors(motion_proxy):
  motion_proxy.setAngles(['LHand'], [0.47], 0.9)
  time.sleep(0.3)

def shakingArm(motion_proxy):
  for i in range(3):
    motion_proxy.angleInterpolationWithSpeed('LShoulderPitch', -0.3, 0.3)
    time.sleep(0.3)
    motion_proxy.angleInterpolationWithSpeed('LShoulderPitch', 0.3, 0.3)
    time.sleep(0.3)

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

  subscriber = proxy.subscribeCamera("demo", 0, 3, 13, 1)
  motion_proxy = ALProxy('ALMotion', Nao_ip, Nao_port)
  neckRegulator(motion_proxy)
  #shakingArm(motion_proxy)
  scissors(motion_proxy)
  while(True):
    '''  
    img = proxy.getImageRemote(subscriber)
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
      print(num)
      if num == 3:
        tts.say('Paper')
        time.sleep(1)
      elif num == 2:
        tts.say('scissor')
        time.sleep(1)
      elif num == 1:
        tts.say('Rock')
        time.sleep(1)
    '''
    num = arTagReco(proxy, subscriber)

    print(num)

main()


