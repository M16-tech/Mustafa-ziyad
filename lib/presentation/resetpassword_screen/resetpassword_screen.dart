import 'controller/resetpassword_controller.dart';
import 'package:flutter/material.dart';
import 'package:rrar_s_application2/core/app_export.dart';
import 'package:rrar_s_application2/widgets/app_bar/appbar_image.dart';
import 'package:rrar_s_application2/widgets/app_bar/custom_app_bar.dart';
import 'package:rrar_s_application2/widgets/custom_button.dart';
import 'package:rrar_s_application2/widgets/custom_icon_button.dart';

class ResetpasswordScreen extends GetWidget<ResetpasswordController> {
  @override
  Widget build(BuildContext context) {
    return SafeArea(
        child: Scaffold(
            backgroundColor: ColorConstant.whiteA700,
            appBar: CustomAppBar(
                height: getVerticalSize(102.00),
                title: AppbarImage(
                    height: getVerticalSize(60.00),
                    width: getHorizontalSize(151.00),
                    imagePath: ImageConstant.imgLogo3,
                    margin: getMargin(left: 22)),
                actions: [
                  AppbarImage(
                      height: getSize(42.00),
                      width: getSize(42.00),
                      svgPath: ImageConstant.imgNotification,
                      margin:
                          getMargin(left: 25, top: 31, right: 25, bottom: 28),
                      onTap: onTapNotification1)
                ],
                styleType: Style.bgStyle),
            body: Container(
                width: size.width,
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.start,
                    children: [
                      Align(
                          alignment: Alignment.centerRight,
                          child: Padding(
                              padding: getPadding(top: 27),
                              child: Row(
                                  mainAxisAlignment: MainAxisAlignment.end,
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text("msg7".tr,
                                        overflow: TextOverflow.ellipsis,
                                        textAlign: TextAlign.left,
                                        style: AppStyle
                                            .txtNotoKufiArabicMedium20Gray800
                                            .copyWith(
                                                height: getVerticalSize(1.00))),
                                    CustomImageView(
                                        svgPath:
                                            ImageConstant.imgMenuLightBlue900,
                                        height: getVerticalSize(15.00),
                                        width: getHorizontalSize(34.00),
                                        radius: BorderRadius.circular(
                                            getHorizontalSize(7.00)),
                                        margin: getMargin(
                                            left: 11, top: 7, bottom: 15))
                                  ]))),
                      Align(
                          alignment: Alignment.center,
                          child: Container(
                              margin: getMargin(left: 16, top: 19, right: 16),
                              padding: getPadding(
                                  left: 12, top: 7, right: 12, bottom: 7),
                              decoration: AppDecoration.outlineCyan70002
                                  .copyWith(
                                      borderRadius:
                                          BorderRadiusStyle.roundedBorder12),
                              child: Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    CustomImageView(
                                        svgPath: ImageConstant.imgContrast,
                                        height: getVerticalSize(12.00),
                                        width: getHorizontalSize(17.00),
                                        margin: getMargin(
                                            left: 1, top: 11, bottom: 11)),
                                    Spacer(),
                                    Padding(
                                        padding: getPadding(top: 4),
                                        child: Text("msg8".tr,
                                            overflow: TextOverflow.ellipsis,
                                            textAlign: TextAlign.left,
                                            style: AppStyle
                                                .txtNotoKufiArabicRegular16Gray400
                                                .copyWith(
                                                    height: getVerticalSize(
                                                        1.00)))),
                                    CustomImageView(
                                        svgPath:
                                            ImageConstant.imgIcsharppassword,
                                        height: getSize(26.00),
                                        width: getSize(26.00),
                                        margin: getMargin(
                                            left: 12, top: 2, bottom: 6))
                                  ]))),
                      CustomIconButton(
                          height: 71,
                          width: 71,
                          margin: getMargin(left: 22, top: 24),
                          variant: IconButtonVariant.FillLightblue900,
                          shape: IconButtonShape.RoundedBorder35,
                          padding: IconButtonPadding.PaddingAll23,
                          child: CustomImageView(
                              svgPath: ImageConstant.imgArrowleft)),
                      Spacer(),
                      Container(
                          width: size.width,
                          padding: getPadding(
                              left: 14, top: 19, right: 14, bottom: 19),
                          decoration: AppDecoration.fillLightblue900e5.copyWith(
                              borderRadius: BorderRadiusStyle.roundedBorder37),
                          child: Row(children: [
                            CustomButton(
                                height: 36,
                                width: 83,
                                text: "lbl16".tr,
                                margin: getMargin(bottom: 1),
                                suffixWidget: Container(
                                    margin: getMargin(left: 12),
                                    child: CustomImageView(
                                        svgPath: ImageConstant
                                            .imgCameraWhiteA70001))),
                            Padding(
                                padding:
                                    getPadding(left: 36, top: 7, bottom: 6),
                                child: Text("lbl17".tr,
                                    overflow: TextOverflow.ellipsis,
                                    textAlign: TextAlign.left,
                                    style: AppStyle
                                        .txtNotoKufiArabicRegular12Gray300
                                        .copyWith(
                                            height: getVerticalSize(0.53)))),
                            CustomImageView(
                                svgPath: ImageConstant.imgDashboard,
                                height: getSize(24.00),
                                width: getSize(24.00),
                                margin: getMargin(left: 12, top: 6, bottom: 7)),
                            Padding(
                                padding:
                                    getPadding(left: 48, top: 7, bottom: 6),
                                child: Text("lbl18".tr,
                                    overflow: TextOverflow.ellipsis,
                                    textAlign: TextAlign.left,
                                    style: AppStyle
                                        .txtNotoKufiArabicRegular12Gray300
                                        .copyWith(
                                            height: getVerticalSize(0.53)))),
                            CustomImageView(
                                svgPath: ImageConstant.imgHomeGray300,
                                height: getSize(24.00),
                                width: getSize(24.00),
                                margin: getMargin(
                                    left: 12, top: 6, right: 13, bottom: 7))
                          ]))
                    ]))));
  }

  onTapNotification1() {
    Get.toNamed(AppRoutes.notfiScreen);
  }
}
