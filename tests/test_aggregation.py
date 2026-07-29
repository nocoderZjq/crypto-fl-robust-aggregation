from collections import OrderedDict

import torch

from src.crypto.secure_aggregation import secure_average_deltas
from src.fl.aggregation import average_deltas


def test_secure_aggregation_equals_plain_average():
    deltas = [
        OrderedDict(weight=torch.tensor([1.0, 2.0]), bias=torch.tensor([1.0])),
        OrderedDict(weight=torch.tensor([3.0, 4.0]), bias=torch.tensor([3.0])),
        OrderedDict(weight=torch.tensor([5.0, 6.0]), bias=torch.tensor([5.0])),
    ]
    plain = average_deltas(deltas)
    secure = secure_average_deltas(deltas, seed=1)
    for key in plain:
        assert torch.allclose(plain[key], secure[key], atol=1e-6)
