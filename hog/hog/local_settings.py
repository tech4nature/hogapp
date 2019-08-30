from .settings import *
import tempfile

tmp_dir = tempfile.TemporaryDirectory().name
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
MEDIA_ROOT = tmp_dir
MEDIA_URL = tmp_dir + "/"
