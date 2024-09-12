from __future__ import annotations

import logging

from coola.utils.imports import numpy_available

logger = logging.getLogger(__name__)


@numpy_available
def check_numpy() -> None:
    logger.info("Checking numpy package...")
    import numpy as np  # local import because it is an optional dependency

    assert np.array_equal(np.ones((2, 3)) + np.ones((2, 3)), np.full((2, 3), 2.0))


def main() -> None:
    check_numpy()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
