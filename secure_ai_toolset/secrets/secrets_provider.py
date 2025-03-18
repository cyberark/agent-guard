# this is a abstract class for secrets provider
import abc
import logging
from typing import Dict, Optional


class SecretProviderException(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class BaseSecretsProvider(abc.ABC):

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)

    @abc.abstractmethod
    def connect(self) -> bool:
        pass

    @abc.abstractmethod
    def store(self, key: str, secret: str) -> None:
        pass

    @abc.abstractmethod
    def get(self, key: str) -> Optional[str]:
        pass

    @abc.abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abc.abstractmethod
    def get_secret_dictionary(self) -> Optional[Dict]:
        pass

    @abc.abstractmethod
    def store_secret_dictionary(self, secret_dictionary: Dict):
        pass
