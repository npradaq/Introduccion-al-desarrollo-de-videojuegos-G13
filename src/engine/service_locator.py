from src.engine.services.config_service import ConfigService
from src.engine.services.fonts_service import FontsService
from src.engine.services.images_service import ImagesService
from src.engine.services.scenes_service import ScenesService
from src.engine.services.sounds_service import SoundsService


class ServiceLocator:
    config_service = ConfigService()
    images_service = ImagesService()
    sounds_service = SoundsService()
    fonts_service = FontsService()
    scenes_service = ScenesService()
