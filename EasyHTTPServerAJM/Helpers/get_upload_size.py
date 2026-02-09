class GetUploadSize:
    SHORT_HAND = {'to_bytes': 'bytes',
                  'to_kilobytes': 'KB',
                  'to_megabytes': 'MB',
                  'to_gigabytes': 'GB',
                  'to_terabytes': 'TB'}
    KB_FACTOR = 1024**1
    MB_FACTOR = 1024**2
    GB_FACTOR = 1024**3
    TB_FACTOR = 1024**4

    def __init__(self, bytes_size: float):
        self.bytes_size = bytes_size

    @classmethod
    def auto_convert(cls, bytes_size: float):
        if bytes_size < cls.KB_FACTOR:
            return 'to_bytes', bytes_size
        elif bytes_size < cls.MB_FACTOR:
            return 'to_kilobytes', cls.to_kilobytes(bytes_size)
        elif bytes_size < cls.GB_FACTOR:
            return 'to_megabytes', cls.to_megabytes(bytes_size)
        elif bytes_size < cls.TB_FACTOR:
            return 'to_gigabytes', cls.to_gigabytes(bytes_size)
        else:
            return 'to_terabytes', cls.to_terabytes(bytes_size)

    @classmethod
    def to_kilobytes(cls, bytes_size: float):
        return cls(bytes_size).bytes_size / cls.KB_FACTOR

    @classmethod
    def to_megabytes(cls, bytes_size: float):
        return cls(bytes_size).bytes_size / cls.MB_FACTOR

    @classmethod
    def to_gigabytes(cls, bytes_size: float):
        return cls(bytes_size).bytes_size / cls.GB_FACTOR

    @classmethod
    def to_terabytes(cls, bytes_size: float):
        return cls(bytes_size).bytes_size / cls.TB_FACTOR

    @classmethod
    def conversion_to_str(cls, method_name: str, bytes_size: float):
        if method_name == 'auto_convert':
            method_name, converted_value = cls.auto_convert(bytes_size)
            return f"{converted_value:.2f} {cls.SHORT_HAND[method_name]}"
        try:
            method = getattr(cls, method_name)(bytes_size)
        except AttributeError:
            print(f"Method {method_name} not found")
            return f"{bytes_size:.2f} bytes"
        return f"{method:.2f} {cls.SHORT_HAND[method_name]}"
