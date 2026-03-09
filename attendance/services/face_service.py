"""人脸特征提取与匹配服务"""
from typing import List, Optional
import numpy as np
import face_recognition
from PIL import Image
import io


# 匹配阈值，越小越严格，默认 0.6，建议 0.5
TOLERANCE = 0.5


def extract_face_encoding(image) -> Optional[List[float]]:
    """
    从图片中提取人脸 128 维特征向量
    :param image: PIL Image 或文件对象
    :return: 特征列表，无人脸返回 None
    """
    if hasattr(image, 'read'):
        img_array = np.array(Image.open(image).convert('RGB'))
    else:
        img_array = np.array(image.convert('RGB'))
    encodings = face_recognition.face_encodings(img_array)
    if not encodings:
        return None
    # 取第一张人脸
    return encodings[0].tolist()


def match_face(known_encodings: list, known_ids: list, face_encoding: list) -> Optional[int]:
    """
    匹配人脸，返回对应人员 id
    :param known_encodings: 已知特征列表（每项为 list）
    :param known_ids: 对应人员 id 列表
    :param face_encoding: 待匹配特征
    :return: 匹配的人员 id，无匹配返回 None
    """
    if not known_encodings or not known_ids:
        return None
    enc = np.asarray(face_encoding, dtype=np.float64)
    known = [np.asarray(e, dtype=np.float64) for e in known_encodings]
    matches = face_recognition.compare_faces(known, enc, tolerance=TOLERANCE)
    for i, m in enumerate(matches):
        if m:
            return known_ids[i]
    return None
