# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules

datas = [('*.db', '.'), ('*.txt', '.'), ('dist\\models', 'face_recognition_models\\models')]
hiddenimports = ['cv2', 'dlib', 'face_recognition', 'face_recognition_models', 'face_recognition.api', 'face_recognition_models.detection_cnn', 'face_recognition_models.face_recognition_model_v1', 'face_recognition_models.pose_predictor_five_point', 'face_recognition_models.pose_predictor_68_point', 'PIL', 'numpy', 'pandas', 'sqlite3', 'tkinter', 'database', 'FR', 'reports']
datas += collect_data_files('dlib')
datas += collect_data_files('face_recognition')
datas += collect_data_files('face_recognition_models')
hiddenimports += collect_submodules('face_recognition_models')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('C:\\Users\\ohanu\\.conda\\envs\\face_recognition_env\\Library\\bin\\*.dll', '.')],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('v', None, 'OPTION')],
    name='AI_Attendance_System',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
