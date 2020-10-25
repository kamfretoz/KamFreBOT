# CREDIT TO: Nekoka/Espy Tysm!
class DictObject(dict):
    def __getattr__(self, item):
        return self[item]
