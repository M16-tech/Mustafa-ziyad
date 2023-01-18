import 'package:flutter/material.dart';
import 'package:rrar_s_application2/core/app_export.dart';

class CustomIconButton extends StatelessWidget {
  CustomIconButton(
      {this.shape,
      this.padding,
      this.variant,
      this.alignment,
      this.margin,
      this.width,
      this.height,
      this.child,
      this.onTap});

  IconButtonShape? shape;

  IconButtonPadding? padding;

  IconButtonVariant? variant;

  Alignment? alignment;

  EdgeInsetsGeometry? margin;

  double? width;

  double? height;

  Widget? child;

  VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return alignment != null
        ? Align(
            alignment: alignment ?? Alignment.center,
            child: _buildIconButtonWidget(),
          )
        : _buildIconButtonWidget();
  }

  _buildIconButtonWidget() {
    return Padding(
      padding: margin ?? EdgeInsets.zero,
      child: IconButton(
        iconSize: getSize(height ?? 0),
        padding: EdgeInsets.all(0),
        icon: Container(
          alignment: Alignment.center,
          width: getSize(width ?? 0),
          height: getSize(height ?? 0),
          padding: _setPadding(),
          decoration: _buildDecoration(),
          child: child,
        ),
        onPressed: onTap,
      ),
    );
  }

  _buildDecoration() {
    return BoxDecoration(
      color: _setColor(),
      borderRadius: _setBorderRadius(),
    );
  }

  _setPadding() {
    switch (padding) {
      case IconButtonPadding.PaddingAll23:
        return getPadding(
          all: 23,
        );
      default:
        return getPadding(
          all: 7,
        );
    }
  }

  _setColor() {
    switch (variant) {
      case IconButtonVariant.FillLightblue900:
        return ColorConstant.lightBlue900;
      case IconButtonVariant.FillTealA700:
        return ColorConstant.tealA700;
      default:
        return ColorConstant.red400;
    }
  }

  _setBorderRadius() {
    switch (shape) {
      case IconButtonShape.RoundedBorder35:
        return BorderRadius.circular(
          getHorizontalSize(
            35.00,
          ),
        );
      default:
        return BorderRadius.circular(
          getHorizontalSize(
            23.00,
          ),
        );
    }
  }
}

enum IconButtonShape {
  RoundedBorder23,
  RoundedBorder35,
}

enum IconButtonPadding {
  PaddingAll7,
  PaddingAll23,
}

enum IconButtonVariant {
  FillRed400,
  FillLightblue900,
  FillTealA700,
}
