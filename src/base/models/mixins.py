from django.db import models

#------------------------------------------------
# Auto Remove File related to model instance
#------------------------------------------------

class CleanupFileQuerysetMixin:

    def update(self, **kwargs):
        file_fnames = [f.name for f in self.model.get_file_fields()]
        file_to_delete = {f: list() for f in file_fnames}

        updated_file_fnames = [fname for fname in file_fnames if fname in kwargs]
        if updated_file_fnames:
            if (
                self._result_cache is None
            ):  # queryset not evaluated, fetch only required fields
                values = self.values(*updated_file_fnames)
            for fname in updated_file_fnames:
                for item in values:
                    file_to_delete[fname].append(item[fname])
            else:  # queryset already evaluated
                for fname in updated_file_fnames:
                    for instance in self:
                        file_to_delete[fname].append(getattr(instance, fname).name)

        result = super().update(**kwargs)

        for fname, paths in file_to_delete.items():
            self.model.delete_files(fname, paths)

        return result

    def delete(self):
        file_fnames = [f.name for f in self.model.get_file_fields()]
        file_to_delete = {f: list() for f in file_fnames}

        if (
            self._result_cache is None
        ):  # queryset not evaluated, fetch only required fields
            values = self.values(*file_fnames)
            for fname in file_fnames:
                for item in values:
                    file_to_delete[fname].append(item[fname])
        else:  # queryset already evaluated
            for fname in file_fnames:
                for instance in self:
                    file_to_delete[fname].append(getattr(instance, fname).name)

        result = super().delete()

        for fname, paths in file_to_delete.items():
            self.model.delete_files(fname, paths)

        return result


class CleanupFileModelMixin(models.Model):

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        file_state = {}
        for field in self.get_file_fields():
            file_state[field.name] = getattr(self, field.name).name

        setattr(self, '_init_file_state', file_state)

    def save(self, *args, **kwargs):
        for field_name in self._get_dirty_file_fields():
            self.delete_files(field_name, [self._init_file_state[field_name]])
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        for field in self.get_file_fields():
            self.delete_files(field.name, [getattr(self, field.name).name])
        return super().delete(using=using, keep_parents=keep_parents)

    def _get_dirty_file_fields(self):
        initial_state = getattr(self, '_init_file_state', {})

        dirty = []
        for fname, val in initial_state.items():
            current_val = getattr(self, fname).name
            if current_val != val:
                dirty.append(fname)
        return dirty

    @classmethod
    def get_file_fields(cls):
        return [field for field in cls._meta.get_fields() if hasattr(field, 'storage')]

    @classmethod
    def delete_files(cls, field_name, file_paths):
        storage = cls._meta.get_field(field_name).storage
        for item in file_paths:
            if item:  # exclude None or empty string
                storage.delete(item)
