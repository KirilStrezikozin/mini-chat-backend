class ContextRequiredToAccessAttributeError(PermissionError):
    def __init__(self, property_name: str, *args) -> None:
        super().__init__(
            f"Context required to access attribute {property_name}",
            *args,
        )
