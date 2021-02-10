from tkinter.font import Font as tkFont

class Font(tkFont):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self):
        params = []
        for param in ['family','size','weight','slant','underline','overstrike']:
            result = self.actual(param)
            if result:
                params.append(result)
            else:
                break
        return tuple(params)
