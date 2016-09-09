from weakref import ref, WeakKeyDictionary


class WeakKeyDictionaryWithCallback(WeakKeyDictionary):
    """
    Implementation of WeakKeyDictionary with callback support
    """
    def set(self, key, value, callback=None):
        """
        Add the record to the dictionary
        :param key:
        :param value:
        :param callback: called when deletes the record
        :return:
        """
        if callback and callable(callback):
            def _remove_with_callback(*args, **kwargs):
                callback(*args, **kwargs)
                self._remove(*args, **kwargs)

            remove = _remove_with_callback
        else:
            remove = self._remove
        self.data[ref(key, remove)] = value
