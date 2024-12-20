import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def calculate_angle(a,b,c):
    a = np.array(a) # first 
    b = np.array(b) # mid
    c = np.array(c) # end

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360-angle
    
    return angle 


# VIDEO FEED
cap = cv2.VideoCapture(0)

#curl counter 

counter = 0
stage = None

# setup mediapipe instances
with mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5) as pose:

    while cap.isOpened():
        ret, frame = cap.read()

        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
      
        # Make detection
        results = pose.process(image)
    
        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark

            # get coordinates
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            
            # calculate angles 
            angle = calculate_angle(shoulder, elbow, wrist)

            # visualization 
            cv2.putText(image, str(angle),
                        tuple(np.multiply(elbow,[640, 480]).astype(int)),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5 , (255,255,255), 2,  cv2.LINE_AA
                              )
            

            # curl counter logic 
            if angle > 160:
                stage = "down"

            if angle < 30 and stage == "down":
                stage= "up"
                counter +=1
                print(counter)
        except:
            pass


        #  render curl counter 
        #  setup status box 
        cv2.rectangle(image, (0,0), (225,73), (245,117,16),-1)


        # rep data in box 
        cv2.putText(image,'REPS', (15,12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),1, cv2.LINE_AA)
        cv2.putText(image, str(counter),
                    (10,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        

        # stage data 
        cv2.putText(image,'STAGE', (80,12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),1, cv2.LINE_AA)
        cv2.putText(image, stage,
                    (90,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        




        # render detection
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(245,11,66), thickness= 2, circle_radius= 2),
                                  mp_drawing.DrawingSpec(color=(245,66,230), thickness= 2, circle_radius= 2)
                                  )


        


        cv2.imshow('Mediapipe Feed', image)
    
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        
cap.release()
cv2.destroyAllWindows()



