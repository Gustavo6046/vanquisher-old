"""CFFI build hook for Poetry."""

import warnings

try:
    import cffi

except ImportError:
    warnings.warn(
        ImportWarning(
            "CFFI is not available, skipping CFFI build. "
            "Expect fallbacks with excruciatingly slow performance. Have fun."
        )
    )

    def build(_setup_kwargs):
        """Poetry-friendly p.aceholder."""
        ...


else:

    def build(setup_kwargs):
        """Build CFFI modules."""
        extensions = [
            # List CFFI buildscripts here.
            "vanquisher.game.terrain._build_interpolate:ffibuilder"
        ]

        setup_kwargs.update({"cffi_modules": extensions})
