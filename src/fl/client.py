from __future__ import annotations

from copy import deepcopy

import torch
from torch.utils.data import DataLoader, Dataset

from .aggregation import diff_states
from .attacks import flip_labels


class Client:
    def __init__(self, client_id: int, dataset: Dataset, indices: list[int], batch_size: int):
        self.client_id = client_id
        self.loader = DataLoader(
            torch.utils.data.Subset(dataset, indices),
            batch_size=batch_size,
            shuffle=True,
        )

    def train(
        self,
        global_model: torch.nn.Module,
        device: str,
        epochs: int,
        learning_rate: float,
        label_flip: bool = False,
        label_flip_mode: str = "reverse",
        num_classes: int = 10,
    ):
        model = deepcopy(global_model).to(device)
        start_state = {k: v.detach().cpu().clone() for k, v in global_model.state_dict().items()}
        model.train()
        optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
        criterion = torch.nn.CrossEntropyLoss()
        for _ in range(epochs):
            for x, y in self.loader:
                x = x.to(device)
                y = y.to(device)
                if label_flip:
                    y = flip_labels(y, num_classes=num_classes, mode=label_flip_mode)
                optimizer.zero_grad(set_to_none=True)
                loss = criterion(model(x), y)
                loss.backward()
                optimizer.step()
        return diff_states(model.state_dict(), start_state)
