import cv2
import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python as mp_python
import time
import numpy as np
from scipy.spatial.transform import Rotation
from .setCamera import SetCamera


class FaceMeshDetector:
    def __init__(self):
        self.MP_TASK_FILE = 'face_landmarker_v2_with_blendshapes.task'
        with open(self.MP_TASK_FILE, mode="rb") as f:
            f_buffer = f.read()

        base_options = mp_python.BaseOptions(model_asset_buffer=f_buffer)
        options = mp_python.vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_faces=1
        )
        self.model = mp_python.vision.FaceLandmarker.create_from_options(options)
        self.landmarks = None
        self.blendshapes = None
        self.rotation_matrix = None
        self.frame = None
        self.frame_flag = False

    def update(self, frame, frame_flag):
        self.frame, self.frame_flag = frame, frame_flag
        if not self.frame_flag:
            return
        frame_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=self.frame)
        mp_result = self.model.detect(frame_mp)
        if mp_result.face_landmarks:
            self.landmarks = [landmark_pb2.NormalizedLandmark(
                x=landmark.x, y=landmark.y, z=landmark.z) 
                for landmark in mp_result.face_landmarks[0]]
        else:
            self.landmarks = None
        if mp_result.face_blendshapes:
            self.blendshapes = [b.score for b in mp_result.face_blendshapes[0]]
        else:
            self.blendshapes = None
        if mp_result.facial_transformation_matrixes:
            self.rotation_matrix = mp_result.facial_transformation_matrixes[0]
        else:
            self.rotation_matrix = None

    def get_results(self):
        if self.landmarks is not None and self.blendshapes is not None and self.rotation_matrix is not None:

            lm = [[self.landmarks[i].x, self.landmarks[i].y, self.landmarks[i].z] for i in range(len(self.landmarks))]
            # lm = self.efilter_lm.filter_signal(np.array(lm))
            lm = np.array(lm)
            self.landmarks = [landmark_pb2.NormalizedLandmark(x=lm[i][0], y=lm[i][1], z=lm[i][2]) for i in range(lm.shape[0])]

            bs = np.array(self.blendshapes)
            # bs = self.efilter_bs.filter_signal(bs)
            self.blendshapes = list(bs)

            return self.landmarks, self.blendshapes, self.rotation_matrix
        else:
            return None, None, None

    def visualize_results(self):
        if not self.frame_flag:
            return
        annotated_image = np.copy(self.frame)
        face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        face_landmarks_proto.landmark.extend(self.landmarks)
        mp.solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style()
        )
        mp.solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_contours_style()
        )
        mp.solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_iris_connections_style()
        )
        annotated_image = cv2.flip(annotated_image, 1)
        cv2.imshow("Camera", annotated_image)
        cv2.waitKey(1)


# ==========================================================================
# 根据关键点坐标，检测人脸位姿
# ==========================================================================
class HeadPose:
    def __init__(self):
        self.yao = 0
        self.bai = 0
        self.dian = 0

    def pose_det(self, rm):
        r = Rotation.from_matrix(rm[:3, :3])
        result = r.as_euler('xyz', degrees=True)

        # 根据欧拉角设置仿真人头姿态变量值
        self.dian = -result[0]
        self.yao = -result[1]
        self.bai = -result[2]

        return [self.dian, self.yao, self.bai]


if __name__ == "__main__":
    fm = FaceMeshDetector()
    hp = HeadPose()
    sc = SetCamera(2)

    while True:
        image, image_flag = sc.start_camera(2)  # 启动摄像头
        if image_flag:                         # 如果摄像头成功采集图片, 则执行后续操作
            fm.update(image, image_flag)       # 调用关键点检测程序
            lm, bs, r_mat = fm.get_results()   # 获取关键点检测结果
            if lm is not None:
                fm.visualize_results()
                print(bs)
