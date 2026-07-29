from __future__ import annotations

import torch
from sklearn.metrics import f1_score


@torch.no_grad()
def evaluate(model, loader, device: str = "cpu") -> dict[str, float]:
    model.eval()
    criterion = torch.nn.CrossEntropyLoss(reduction="sum")
    total_loss = 0.0
    total = 0
    correct = 0
    y_true: list[int] = []
    y_pred: list[int] = []
    for x, y in loader:
        x = x.to(device)
        y = y.to(device)
        logits = model(x)
        total_loss += float(criterion(logits, y).item())
        pred = logits.argmax(dim=1)
        correct += int((pred == y).sum().item())
        total += int(y.numel())
        y_true.extend(y.cpu().tolist())
        y_pred.extend(pred.cpu().tolist())
    return {
        "test_accuracy": correct / max(total, 1),
        "test_loss": total_loss / max(total, 1),
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
    }
