class SmalltalkError(Exception):
    pass


class SmalltalkParserError(SmalltalkError):
    pass


class MessageArgCountError(SmalltalkError):
    pass


class DoesNotUnderstand(SmalltalkError):
    pass


