import numpy as np
import cv2
import camera_config

cv2.namedWindow("left")
cv2.namedWindow("right")
cv2.namedWindow("left_r")
cv2.namedWindow("right_r")
cv2.namedWindow("depth")  #分别打开左右以及图像深度框图
cv2.moveWindow("left", 0, 0)
cv2.moveWindow("right", 640, 0)
cv2.moveWindow("left_r", 0, 480)
cv2.moveWindow("right_r", 640, 480)
cv2.moveWindow("depth", 1280, 0)  #设定窗口位置
cv2.createTrackbar("num", "depth", 0, 10, lambda x: None)
cv2.createTrackbar("blockSize", "depth", 5, 255, lambda x: None)  #设置双滑条

cap = cv2.VideoCapture(2)
cap.set(3, 1280)
cap.set(4, 480)  #打开并设置摄像头

def callbackFunc(e, x, y, f, p):
  if e == cv2.EVENT_LBUTTONDOWN:
    print(threeD[y][x])  #设置回传函数，鼠标点击时回传信息

cv2.setMouseCallback("depth", callbackFunc, None)  #点击depth图触发函数

while True:
  ret, frame = cap.read()
  frame1 = frame[0:480, 0:640]
  frame2 = frame[0:480, 640:1280]  #割开双目图像

  img1_rectified = cv2.remap(frame1, camera_config.left_map1, camera_config.left_map2, cv2.INTER_LINEAR)
  img2_rectified = cv2.remap(frame2, camera_config.right_map1, camera_config.right_map2, cv2.INTER_LINEAR)  #依据MATLAB测量数据重建无畸变图片

  imgL = cv2.cvtColor(img1_rectified, cv2.COLOR_BGR2GRAY)
  imgR = cv2.cvtColor(img2_rectified, cv2.COLOR_BGR2GRAY)  #BGR图像转灰度图

  num = cv2.getTrackbarPos("num", "depth")
  blockSize = cv2.getTrackbarPos("blockSize", "depth")  #在depth图上增加滑条

  if blockSize % 2 == 0:
    blockSize += 1
  if blockSize < 5:
    blockSize = 5

  stereo = cv2.StereoSGBM_create(0, 16, 9)  #立体匹配，由滑条数值决定numDisparities与blockSize
  stereo.setPreFilterCap(63)
  stereo.setBlockSize(9)
  stereo.setP1(8 * 9 * 9)
  stereo.setP2(32 * 9 * 9)
  stereo.setMinDisparity(0)
  stereo.setNumDisparities(160)
  stereo.setUniquenessRatio(10)
  stereo.setSpeckleWindowSize(100)
  stereo.setSpeckleRange(32)
  stereo.setDisp12MaxDiff(1)
  disparity = stereo.compute(imgL, imgR)

  disp = cv2.normalize(disparity, disparity, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)  #归一化函数算法

  threeD = cv2.reprojectImageTo3D(disparity.astype(np.float32)/16., camera_config.Q)  #计算三维坐标数据值

  cv2.imshow("left", frame1)
  cv2.imshow("right", frame2)
  cv2.imshow("left_r", imgL)
  cv2.imshow("right_r", imgR)
  cv2.imshow("depth", disp)  #显示出修正畸变前后以及深度图的双目画面

  key = cv2.waitKey(1)
  if key == ord("q"):
    break
  elif key == ord("s"):
    cv2.imwrite("./snapshot/BM_left.jpg", imgL)
    cv2.imwrite("./snapshot/BM_right.jpg", imgR)
    cv2.imwrite("./snapshot/BM_depth.jpg", disp)

cap.release()
cv2.destroyAllWindows()