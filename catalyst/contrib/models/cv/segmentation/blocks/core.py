# flake8: noqa
# @TODO: code formatting issue for 20.07 release
from abc import ABC, abstractmethod

import torch
from torch import nn
from torch.nn import functional as F

from catalyst.contrib.models.cv.segmentation.abn import ABN


def _get_block(
    in_channels: int,
    out_channels: int,
    abn_block: nn.Module = ABN,
    activation: str = "ReLU",
    kernel_size: int = 3,
    padding: int = 1,
    first_stride: int = 1,
    second_stride: int = 1,
    complexity: int = 1,
    **kwargs
):
    layers = [
        nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=first_stride,
            bias=False,
            **kwargs
        ),
        abn_block(out_channels, activation=activation),
    ]
    if complexity > 0:
        layers_list = [
            nn.Conv2d(
                out_channels,
                out_channels,
                kernel_size=kernel_size,
                padding=padding,
                stride=second_stride,
                bias=False,
                **kwargs
            ),
            abn_block(out_channels, activation=activation),
        ] * complexity
        layers = layers + layers_list
    block = nn.Sequential(*layers)
    return block


def _upsample(
    x: torch.Tensor,
    scale: int = None,
    size: int = None,
    interpolation_mode: str = "bilinear",
    align_corners: bool = True,
) -> torch.Tensor:
    if scale is None:
        x = F.interpolate(x, size=size, mode=interpolation_mode, align_corners=align_corners)
    else:
        x = F.interpolate(
            x, scale_factor=scale, mode=interpolation_mode, align_corners=align_corners
        )
    return x


class EncoderBlock(ABC, nn.Module):
    """@TODO: Docs (add description, `Example`). Contribution is welcome."""

    def __init__(self, in_channels: int, out_channels: int, in_strides: int = None):
        """
        Args:
            @TODO: Docs. Contribution is welcome.
        """
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.in_strides = in_strides

    @property
    @abstractmethod
    def out_strides(self) -> int:
        """@TODO: Docs. Contribution is welcome."""
        pass

    @property
    @abstractmethod
    def block(self) -> nn.Module:
        """@TODO: Docs. Contribution is welcome."""
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward call."""
        return self.block(x)


class DecoderBlock(ABC, nn.Module):
    """@TODO: Docs (add description, `Example`). Contribution is welcome."""

    def __init__(
        self,
        in_channels: int,
        enc_channels: int,
        out_channels: int,
        in_strides: int = None,
        *args,
        **kwargs
    ):
        """
        Args:
            @TODO: Docs. Contribution is welcome.
        """
        super().__init__()
        self.in_channels = in_channels
        self.enc_channels = enc_channels
        self.out_channels = out_channels
        self.in_strides = in_strides

        self.block = self._get_block(*args, **kwargs)

    @abstractmethod
    def _get_block(self, *args, **kwargs) -> nn.Module:
        pass

    @property
    def out_strides(self) -> int:
        """@TODO: Docs. Contribution is welcome."""
        return self.in_strides // 2 if self.in_strides is not None else None

    @abstractmethod
    def forward(self, bottom: torch.Tensor, left: torch.Tensor) -> torch.Tensor:
        """Forward call."""
        pass


__all__ = ["EncoderBlock", "DecoderBlock"]
