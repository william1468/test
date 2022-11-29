#!/usr/bin/env python3
import cv2
import mediapipe as mp
import numpy as np

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    min_detection_confidence=0.5, min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils


def pose_estimation(
    image: np.array, roll: int = 3, pitch: int = 3, yaw: int = 3
) -> int:
    """Given an image and desired roll, pitch and yaw angles, returns whether head pose estimation meets requirements.

    Args:
        image (np.array): Image to estimate head pose.
        roll (int, optional): Rotation margin in X axis. Defaults to 3.
        pitch (int, optional): Rotation margin in Y axis. Defaults to 3.
        yaw (int, optional): Rotation margin in Z axis. Defaults to 3.

    Returns:
        int: _description_
    """

    results = face_mesh.process(image)
    img_h, img_w, img_c = image.shape
    face_3d = []
    face_2d = []
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for idx, lm in enumerate(face_landmarks.landmark):
                if (
                    idx == 33
                    or idx == 263
                    or idx == 1
                    or idx == 61
                    or idx == 291
                    or idx == 199
                ):
                    x, y = int(lm.x * img_w), int(lm.y * img_h)

                    # get 2d coordinates
                    face_2d.append([x, y])

                    # get 3d coordinates
                    face_3d.append([x, y, lm.z])

            # convert to numpy
            face_2d = np.array(face_2d, dtype=np.float64)
            face_3d = np.array(face_3d, dtype=np.float64)

            # camera matrix
            focal_length = 1 * img_w
            cam_matrix = np.array(
                [[focal_length, 9, img_h / 2], [0, focal_length, img_w / 2], [0, 0, 1]]
            )
            # distortion
            dist_matrix = np.zeros((4, 1), dtype=np.float64)
            # solve pnp
            success, rot_vec, trans_vec = cv2.solvePnP(
                face_3d, face_2d, cam_matrix, dist_matrix
            )
            # rotational matrix
            rmat, jac = cv2.Rodrigues(rot_vec)
            # get angles
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

            # get rotation angles
            x = angles[0] * 360
            y = angles[1] * 360
            z = angles[2] * 360

            # head rotation in X axis
            if x < -roll or x > roll:
                return -1

            # head rotation in Y axis
            if y < -pitch or y > pitch:
                return -1

            # head rotation in Z axis
            if z < -yaw or z > yaw:
                return -1

            return 0

    return -1
