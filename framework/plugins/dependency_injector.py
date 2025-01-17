from typing import Optional

from framework.core.interfaces.lifecycle import DependencyInjector
from framework.core.utils.datautils import is_builtin_class_instance


class Inject:
    def __init__(self, name=None):
        self.name = name


class KartaDependencyInjector(DependencyInjector):
    objects: Optional[dict[str, object]] = {}

    def __init__(self):
        self.objects = {
            'dependency_injector': self,
        }

    def register(self, name: str, value: object) -> object:
        previous_object = self.objects[name] if name in self.objects.keys() else None
        self.objects[name] = value
        return previous_object

    def inject(self, *list_of_objects) -> bool:
        for object_to_inject in list_of_objects:
            for field_name, field_value in object_to_inject.__dict__.items():
                if isinstance(field_value, Inject):
                    object_name_to_inject = field_value.name if field_value.name else field_name
                    if object_name_to_inject in self.objects.keys():
                        object_to_inject.__setattr__(field_name, self.objects[object_name_to_inject])
            if not is_builtin_class_instance(object_to_inject):
                for field_name, field_value in object_to_inject.__class__.__dict__.items():
                    if isinstance(field_value, Inject):
                        object_name_to_inject = field_value.name if field_value.name else field_name
                        if object_name_to_inject in self.objects.keys():
                            object_to_inject.__setattr__(field_name, self.objects[object_name_to_inject])
            # for obj_name, obj_value in self.objects.items():
            #     if obj_name in object_to_inject.__dict__.keys() or obj_name in object_to_inject.__class__.__dict__.keys():
            #         object_to_inject.__setattr__(obj_name, obj_value)
            if (('__post_inject__' in object_to_inject.__class__.__dict__.keys())
                    and callable(object_to_inject.__class__.__dict__['__post_inject__'])):
                object_to_inject.__class__.__dict__['__post_inject__'](object_to_inject)
        return True
