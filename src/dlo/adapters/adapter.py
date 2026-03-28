from abc import ABC, abstractmethod

from dlo.common.exceptions import errors
from dlo.core.models.resources import Model


class Adapter(ABC):
    def create(self, model: Model):
        if model.compiled is False:
            raise errors.DloRuntimeError(
                f"Model `{model.name}` was not complied but tried to create it"
            )

        return self._create(model)

    @abstractmethod
    def execute(self): ...

    @abstractmethod
    def fetch(self): ...

    @abstractmethod
    def _create(self, model: Model): ...
