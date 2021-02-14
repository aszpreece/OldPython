class Component:
    c_type_id = -1
    def __init__(self, name) -> None:
        self.name = name
        pass

    def __eq__(self, other):
        return self.c_type_id == other.c_type_id