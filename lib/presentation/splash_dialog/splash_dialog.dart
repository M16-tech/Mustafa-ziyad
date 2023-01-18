import 'controller/splash_controller.dart';
import 'package:flutter/material.dart';
import 'package:rrar_s_application2/core/app_export.dart';

// ignore_for_file: must_be_immutable
class SplashDialog extends StatelessWidget {
  SplashDialog(this.controller);

  SplashController controller;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: getPadding(
        all: 8,
      ),
      decoration: AppDecoration.fillCyan400ce.copyWith(
        borderRadius: BorderRadiusStyle.roundedBorder97,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: getHorizontalSize(
              176.00,
            ),
            margin: getMargin(
              right: 1,
              bottom: 1,
            ),
            padding: getPadding(
              all: 13,
            ),
            decoration: AppDecoration.fillCyan60001.copyWith(
              borderRadius: BorderRadiusStyle.circleBorder88,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                Card(
                  clipBehavior: Clip.antiAlias,
                  elevation: 0,
                  margin: EdgeInsets.all(0),
                  color: ColorConstant.whiteA700,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadiusStyle.roundedBorder74,
                  ),
                  child: Container(
                    height: getSize(
                      149.00,
                    ),
                    width: getSize(
                      149.00,
                    ),
                    padding: getPadding(
                      left: 19,
                      top: 20,
                      right: 19,
                      bottom: 20,
                    ),
                    decoration: AppDecoration.fillWhiteA700.copyWith(
                      borderRadius: BorderRadiusStyle.roundedBorder74,
                    ),
                    child: Stack(
                      children: [
                        CustomImageView(
                          imagePath: ImageConstant.imgLogo1,
                          height: getVerticalSize(
                            104.00,
                          ),
                          width: getHorizontalSize(
                            110.00,
                          ),
                          alignment: Alignment.center,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
