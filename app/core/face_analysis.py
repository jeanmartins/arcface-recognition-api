from insightface.app import FaceAnalysis
import ssl
import onnxruntime as ort


ssl._create_default_https_context = ssl._create_unverified_context
available_providers = ort.get_available_providers()


if "CUDAExecutionProvider" in available_providers:
    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    ctx_id = 0
else:
    providers = ["CPUExecutionProvider"]
    ctx_id = -1
    
face_app  = FaceAnalysis(name="buffalo_l", providers=providers)

face_app.prepare(ctx_id=ctx_id)
