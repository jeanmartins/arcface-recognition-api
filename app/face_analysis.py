from insightface.app import FaceAnalysis
import ssl


ssl._create_default_https_context = ssl._create_unverified_context

face_app  = FaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
face_app.prepare(ctx_id=0)
