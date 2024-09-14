from __future__ import annotations

from coola import objects_are_equal
from coola.testing import numpy_available, torch_available


@numpy_available
def test_numpy() -> None:
    import numpy as np  # local import because it is an optional dependency

    assert objects_are_equal(np.ones((2, 3)) + np.ones((2, 3)), np.full((2, 3), 2.0))


@torch_available
def test_torch() -> None:
    import torch  # local import because it is an optional dependency

    assert objects_are_equal(torch.ones(2, 3) + torch.ones(2, 3), torch.full((2, 3), 2.0))
