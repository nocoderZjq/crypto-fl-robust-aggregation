from .mlp import MLP
from .tiny_cnn import TinyCNN


def build_model(name: str, input_channels: int = 1, num_classes: int = 10):
    name = name.lower()
    if name == "mlp":
        return MLP(input_channels=input_channels, num_classes=num_classes)
    if name == "tiny_cnn":
        return TinyCNN(input_channels=input_channels, num_classes=num_classes)
    raise ValueError(f"Unknown model: {name}")
