from io import TextIOBase


class SimpleString(str):
    def __repr__(self) -> str:
        return "Simple(" + super().__repr__() + ")"


class ErrorString(str):
    def __repr__(self) -> str:
        return "Error(" + super().__repr__() + ")"


class BulkString(str):
    def __repr__(self) -> str:
        return "Bulk(" + super().__repr__() + ")"


class RESPArray(list["RESPValue"]):
    def __repr__(self) -> str:
        return "RESPArray(" + super().__repr__() + ")"

# TODO: handle null bulk string and array


class NilBulkString():
    def __repr__(self) -> str:
        return "Bulk(nil)"


class NilArray():
    def __repr__(self) -> str:
        return "RESPArray(nil)"


RESPValue = SimpleString | BulkString | ErrorString | RESPArray | NilBulkString | NilArray


def parse_resp_value(data: TextIOBase) -> RESPValue:
    # if isinstance(data, StringIO):
    #     print("data:", repr(data.getvalue()))
    match data.read(1):
        case "+":
            return SimpleString(data.readline())
        case "-":
            return ErrorString(data.readline())
        case "$":
            length = int(data.readline())
            if length == -1:
                return NilBulkString()
            text = data.read(length)
            assert data.read(2) == "\r\n"
            return BulkString(text)
        case "*":
            length = int(data.readline())
            if length == -1:
                return NilArray()
            return RESPArray([parse_resp_value(data) for _ in range(length)])
        case "":
            raise EOFError()
        case c:
            raise Exception("Unsupported request:", c+data.readline())


def serialize_resp_value(value: RESPValue) -> str:
    match value:
        case SimpleString(s):
            return f"+{s}\r\n"
        case ErrorString(s):
            return f"-{s}\r\n"
        case BulkString(s):
            return f"${len(s)}\r\n{s}\r\n"
        case RESPArray(a):
            return f"*{len(a)}\r\n" + "".join(map(serialize_resp_value, a))
        case NilBulkString():
            return "$-1\r\n"
        case NilArray():
            return "*-1\r\n"
