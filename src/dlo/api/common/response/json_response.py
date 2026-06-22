from fastapi.responses import ORJSONResponse


class MsgSpecJSONResponse(ORJSONResponse):
    """
    A response class that serializes data into JSON using the high-performance msgspec library
    """
