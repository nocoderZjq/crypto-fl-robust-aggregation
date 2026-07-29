import torch

from src.fl.attacks import flip_labels


def test_label_flip_default_mapping():
    y = torch.tensor([0, 1, 4, 9])
    assert flip_labels(y).tolist() == [9, 8, 5, 0]
