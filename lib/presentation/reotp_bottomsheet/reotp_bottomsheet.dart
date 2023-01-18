import 'controller/reotp_controller.dart';
import 'package:flutter/material.dart';
import 'package:rrar_s_application2/core/app_export.dart';

// ignore_for_file: must_be_immutable
class ReotpBottomsheet extends StatelessWidget {
  ReotpBottomsheet(this.controller);

  ReotpController controller;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Container(
        padding: getPadding(
          left: 35,
          top: 22,
          right: 35,
          bottom: 22,
        ),
        decoration: AppDecoration.fillWhiteA700.copyWith(
          borderRadius: BorderRadiusStyle.roundedBorder42,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.end,
          mainAxisAlignment: MainAxisAlignment.start,
          children: [
            Padding(
              padding: getPadding(
                right: 1,
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  Padding(
                    padding: getPadding(
                      top: 7,
                      bottom: 7,
                    ),
                    child: Text(
                      "lbl4".tr,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.left,
                      style: AppStyle.txtNotoKufiArabicRegular12.copyWith(
                        height: getVerticalSize(
                          0.53,
                        ),
                      ),
                    ),
                  ),
                  Padding(
                    padding: getPadding(
                      left: 99,
                    ),
                    child: Text(
                      "lbl5".tr,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.left,
                      style: AppStyle.txtNotoKufiArabicMedium20Gray800.copyWith(
                        height: getVerticalSize(
                          1.00,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Card(
              clipBehavior: Clip.antiAlias,
              elevation: 0,
              margin: getMargin(
                top: 59,
                right: 2,
              ),
              color: ColorConstant.whiteA700,
              shape: RoundedRectangleBorder(
                side: BorderSide(
                  color: ColorConstant.cyan70001,
                  width: getHorizontalSize(
                    1.00,
                  ),
                ),
                borderRadius: BorderRadiusStyle.roundedBorder12,
              ),
              child: Container(
                height: getVerticalSize(
                  63.00,
                ),
                width: getHorizontalSize(
                  60.00,
                ),
                padding: getPadding(
                  left: 8,
                  top: 2,
                  right: 8,
                  bottom: 2,
                ),
                decoration: AppDecoration.outlineCyan70001.copyWith(
                  borderRadius: BorderRadiusStyle.roundedBorder12,
                ),
                child: Stack(
                  alignment: Alignment.centerRight,
                  children: [
                    Align(
                      alignment: Alignment.bottomCenter,
                      child: Container(
                        height: getVerticalSize(
                          1.00,
                        ),
                        width: getHorizontalSize(
                          43.00,
                        ),
                        margin: getMargin(
                          bottom: 8,
                        ),
                        decoration: BoxDecoration(
                          color: ColorConstant.blueGray7003a,
                        ),
                      ),
                    ),
                    Align(
                      alignment: Alignment.centerRight,
                      child: Container(
                        width: getHorizontalSize(
                          17.00,
                        ),
                        margin: getMargin(
                          right: 12,
                        ),
                        child: Text(
                          "lbl_52".tr,
                          maxLines: null,
                          textAlign: TextAlign.center,
                          style: AppStyle.txtCairoRegular3072.copyWith(
                            height: getVerticalSize(
                              1.00,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Padding(
              padding: getPadding(
                top: 26,
                right: 3,
                bottom: 236,
              ),
              child: Text(
                "lbl6".tr,
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.left,
                style: AppStyle.txtNotoKufiArabicRegular14Cyan70001.copyWith(
                  height: getVerticalSize(
                    1.00,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
