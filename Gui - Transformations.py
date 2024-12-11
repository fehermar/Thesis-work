# importing module
import csv
import numpy as np
import cv2

# reading CSV file
filename = open("C:\\Users\\buvr_\\Documents\\BUVR\\UR\\FOT\\FOT.csv")
file = csv.DictReader(filename)



timestamp = []
TCP_x = []
TCP_y = []
TCP_z = []
TCP_roll = []
TCP_pitch = []
TCP_yaw = []


for col in file:
    timestamp.append(col['timestamp'])
    TCP_x.append(col['actual_TCP_pose_0'])
    TCP_y.append(col['actual_TCP_pose_1'])
    TCP_z.append(col['actual_TCP_pose_2'])
    TCP_roll.append(col['actual_TCP_pose_3'])
    TCP_pitch.append(col['actual_TCP_pose_4'])
    TCP_yaw.append(col['actual_TCP_pose_5'])


x = np.array(TCP_x, dtype='float')*100
y = np.array(TCP_y, dtype='float')*100
z = np.array(TCP_z, dtype='float')*100
roll= np.array(TCP_roll, dtype='float')
pitch = np.array(TCP_pitch, dtype='float')
yaw = np.array(TCP_yaw, dtype='float')

#y -> negatív irány közepe 5,75 cm
y_offset = 5.75
#z -> lefele 10 cm +?
z_offset = 10


# printing list data
#print('x: ', x)

def R_matrix(i):#, pitch, yaw):
    R_x = np.array([
        [1, 0, 0],
        [0, np.cos(roll[i]), -np.sin(roll[i])],
        [0, np.sin(roll[i]), np.cos(roll[i])]
    ])

    R_y = np.array([
        [np.cos(pitch[i]), 0, np.sin(pitch[i])],
        [0, 1, 0],
        [-np.sin(pitch[i]), 0, np.cos(pitch[i])]
    ])

    R_z = np.array([
        [np.cos(yaw[i]), -np.sin(yaw[i]), 0],
        [np.sin(yaw[i]), np.cos(yaw[i]), 0],
        [0, 0, 1]
    ])

    R = R_z @ R_y @ R_x
    return R

def transform(i, point_cloud, R):#, xx, yy, zz):
    for j in range(point_cloud.shape[0]):
        v = np.array([point_cloud[j, 0], point_cloud[j, 1], point_cloud[j, 2]])

        v = v @ R.T

        v[0] += x[i]
        v[1] += y[i] + y_offset
        v[2] += z[i] + z_offset

        point_cloud[j, 0] = v[0]
        point_cloud[j, 1] = v[1]
        point_cloud[j, 2] = v[2]

    return point_cloud

######## end of code

######## example

def save_ply(filename, point_cloud):
    with open(filename, 'w') as f:
        f.write(f"ply\nformat ascii 1.0\n")
        f.write(f"element vertex {len(point_cloud)}\n")
        f.write("property float x\nproperty float y\nproperty float z\nproperty uchar intensity\n")
        f.write("end_header\n")
        for point in point_cloud:
            x, y, z, intensity = point
            f.write(f"{x} {y} {z} {int(intensity)}\n")



'''ONE FRAME EXAMPLE'''

video = cv2.VideoCapture("C:\\Users\\buvr_\\Videos\\new_folder\\Videos\\pentek_last_3.avi")


if video.isOpened():
    ret, frame_example = video.read()
    if ret:
        gray_frame_example = cv2.cvtColor(frame_example, cv2.COLOR_BGR2GRAY)

gray_frame_example_flattened = gray_frame_example.flatten()


xm = np.linspace(-5.5, 5.5, 480)
ym = np.array([0])
zm = np.linspace(0, 8.7, 640)

Xm, Ym, Zm = np.meshgrid(xm, ym, zm, indexing = 'ij')

xf = Xm.flatten()
yf = Ym.flatten()
zf = Zm.flatten()

point_cloud_example = []

for j in range(gray_frame_example_flattened.shape[0]):
    point_cloud_example.append([xf[j], yf[j], zf[j], gray_frame_example_flattened[j]])

save_ply('C:\\Users\\buvr_\\Documents\\BUVR\\UR\\FOT\\example_frame_pentek_3_2.ply', point_cloud=np.array(point_cloud_example))

transformed_point_cloud_example = transform(0, point_cloud=np.array(point_cloud_example), R=R_matrix(0))

save_ply('C:\\Users\\buvr_\\Documents\\BUVR\\UR\\FOT\\example_frame_pentek_3_transformed_2.ply', transformed_point_cloud_example)
