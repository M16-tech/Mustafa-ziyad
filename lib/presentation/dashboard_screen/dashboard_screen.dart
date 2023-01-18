import 'controller/dashboard_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart' as fs;
import 'package:rrar_s_application2/core/app_export.dart';
import 'package:rrar_s_application2/widgets/app_bar/appbar_image.dart';
import 'package:rrar_s_application2/widgets/app_bar/custom_app_bar.dart';
import 'package:rrar_s_application2/widgets/custom_button.dart';

class DashboardScreen extends GetWidget<DashboardController> {
  @override
  Widget build(BuildContext context) {
    return SafeArea(
        child: Scaffold(
            backgroundColor: ColorConstant.whiteA700,
            body: Container(
                width: size.width,
                child: Column(
                    mainAxisAlignment: MainAxisAlignment.start,
                    children: [
                      Container(
                          width: size.width,
                          padding: getPadding(top: 12, bottom: 12),
                          decoration: BoxDecoration(
                              image: DecorationImage(
                                  image: AssetImage(ImageConstant.imgGroup1),
                                  fit: BoxFit.cover)),
                          child: Column(
                              mainAxisAlignment: MainAxisAlignment.end,
                              children: [
                                CustomAppBar(
                                    height: getVerticalSize(60.00),
                                    title: AppbarImage(
                                        height: getVerticalSize(60.00),
                                        width: getHorizontalSize(151.00),
                                        imagePath: ImageConstant.imgLogo3,
                                        margin: getMargin(left: 16)),
                                    actions: [
                                      AppbarImage(
                                          height: getSize(32.00),
                                          width: getSize(32.00),
                                          svgPath:
                                              ImageConstant.imgNotification,
                                          margin: getMargin(
                                              left: 16,
                                              top: 14,
                                              right: 16,
                                              bottom: 13),
                                          onTap: onTapNotification)
                                    ]),
                                Container(
                                    height: getVerticalSize(220.00),
                                    width: getHorizontalSize(226.00),
                                    margin: getMargin(top: 12),
                                    padding: getPadding(
                                        left: 62,
                                        top: 47,
                                        right: 62,
                                        bottom: 47),
                                    decoration: BoxDecoration(
                                        image: DecorationImage(
                                            image: fs.Svg(
                                                ImageConstant.imgGroup24),
                                            fit: BoxFit.cover)),
                                    child: Stack(
                                        alignment: Alignment.bottomCenter,
                                        children: [
                                          Align(
                                              alignment: Alignment.topRight,
                                              child: Container(
                                                  width:
                                                      getHorizontalSize(61.00),
                                                  margin: getMargin(right: 17),
                                                  decoration: AppDecoration
                                                      .txtOutlineBlack9003f,
                                                  child: Text("lbl_29".tr,
                                                      maxLines: null,
                                                      textAlign:
                                                          TextAlign.center,
                                                      style: AppStyle
                                                          .txtCairoBold544
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00))))),
                                          Align(
                                              alignment: Alignment.bottomCenter,
                                              child: Container(
                                                  width:
                                                      getHorizontalSize(100.00),
                                                  margin: getMargin(bottom: 2),
                                                  child: Text("lbl7".tr,
                                                      maxLines: null,
                                                      textAlign:
                                                          TextAlign.center,
                                                      style: AppStyle
                                                          .txtCairoRegular224
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00)))))
                                        ])),
                                Container(
                                    width: getHorizontalSize(105.00),
                                    margin: getMargin(top: 4),
                                    child: Text("lbl_id_3344556".tr,
                                        maxLines: null,
                                        textAlign: TextAlign.center,
                                        style: AppStyle.txtCairoBold192
                                            .copyWith(
                                                height: getVerticalSize(1.00))))
                              ])),
                      Expanded(
                          child: SingleChildScrollView(
                              child: Container(
                                  width: size.width,
                                  margin: getMargin(top: 14),
                                  child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      mainAxisAlignment:
                                          MainAxisAlignment.start,
                                      children: [
                                        Align(
                                            alignment: Alignment.center,
                                            child: Row(
                                                mainAxisAlignment:
                                                    MainAxisAlignment.center,
                                                crossAxisAlignment:
                                                    CrossAxisAlignment.start,
                                                children: [
                                                  Text("lbl8".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
                                                      style: AppStyle
                                                          .txtCairoRegular256
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00))),
                                                  Container(
                                                      height: getSize(12.00),
                                                      width: getSize(12.00),
                                                      margin: getMargin(
                                                          left: 12,
                                                          top: 14,
                                                          bottom: 20),
                                                      decoration: BoxDecoration(
                                                          color: ColorConstant
                                                              .cyan60003,
                                                          borderRadius:
                                                              BorderRadius.circular(
                                                                  getHorizontalSize(
                                                                      6.00))))
                                                ])),
                                        Align(
                                            alignment: Alignment.centerRight,
                                            child: Padding(
                                                padding: getPadding(top: 14),
                                                child: Row(
                                                    mainAxisAlignment:
                                                        MainAxisAlignment.end,
                                                    crossAxisAlignment:
                                                        CrossAxisAlignment
                                                            .start,
                                                    children: [
                                                      Text("lbl9".tr,
                                                          overflow: TextOverflow
                                                              .ellipsis,
                                                          textAlign:
                                                              TextAlign.left,
                                                          style: AppStyle
                                                              .txtNotoKufiArabicMedium20Gray800
                                                              .copyWith(
                                                                  height:
                                                                      getVerticalSize(
                                                                          1.00))),
                                                      CustomImageView(
                                                          imagePath: ImageConstant
                                                              .imgMenuLightBlue90015x53,
                                                          height:
                                                              getVerticalSize(
                                                                  15.00),
                                                          width:
                                                              getHorizontalSize(
                                                                  53.00),
                                                          radius: BorderRadius
                                                              .circular(
                                                                  getHorizontalSize(
                                                                      7.00)),
                                                          margin: getMargin(
                                                              left: 13,
                                                              top: 9,
                                                              bottom: 13))
                                                    ]))),
                                        Padding(
                                            padding:
                                                getPadding(left: 18, top: 10),
                                            child: Row(children: [
                                              Padding(
                                                  padding:
                                                      getPadding(bottom: 1),
                                                  child: Text("lbl10".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
                                                      style: AppStyle
                                                          .txtNotoKufiArabicRegular16
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00)))),
                                              Padding(
                                                  padding: getPadding(
                                                      left: 53, top: 1),
                                                  child: Text("msg2".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
                                                      style: AppStyle
                                                          .txtNotoKufiArabicRegular16Bluegray400
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00))))
                                            ])),
                                        Padding(
                                            padding:
                                                getPadding(left: 16, top: 3),
                                            child: Row(children: [
                                              Padding(
                                                  padding:
                                                      getPadding(bottom: 1),
                                                  child: Text(
                                                      "lbl_ammar_wifi".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
                                                      style: AppStyle
                                                          .txtNotoKufiArabicRegular16
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00)))),
                                              Padding(
                                                  padding: getPadding(
                                                      left: 55, top: 1),
                                                  child: Text("lbl11".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
                                                      style: AppStyle
                                                          .txtNotoKufiArabicRegular16Bluegray400
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00))))
                                            ])),
                                        Padding(
                                            padding:
                                                getPadding(left: 16, top: 2),
                                            child: Row(children: [
                                              Padding(
                                                  padding:
                                                      getPadding(bottom: 2),
                                                  child: Text(
                                                      "lbl_07830200030".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
                                                      style: AppStyle
                                                          .txtNotoKufiArabicRegular16
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00)))),
                                              Padding(
                                                  padding: getPadding(
                                                      left: 51, top: 2),
                                                  child: Text("lbl12".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
                                                      style: AppStyle
                                                          .txtNotoKufiArabicRegular16Bluegray400
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00))))
                                            ])),
                                        Align(
                                            alignment: Alignment.center,
                                            child: Container(
                                                height: getVerticalSize(1.00),
                                                width:
                                                    getHorizontalSize(328.00),
                                                margin: getMargin(top: 10),
                                                decoration: BoxDecoration(
                                                    color: ColorConstant
                                                        .gray300))),
                                        Align(
                                            alignment: Alignment.centerRight,
                                            child: Padding(
                                                padding: getPadding(top: 12),
                                                child: Row(
                                                    mainAxisAlignment:
                                                        MainAxisAlignment.end,
                                                    crossAxisAlignment:
                                                        CrossAxisAlignment
                                                            .start,
                                                    children: [
                                                      Text("msg3".tr,
                                                          overflow: TextOverflow
                                                              .ellipsis,
                                                          textAlign:
                                                              TextAlign.left,
                                                          style: AppStyle
                                                              .txtNotoKufiArabicMedium20Gray800
                                                              .copyWith(
                                                                  height:
                                                                      getVerticalSize(
                                                                          1.00))),
                                                      CustomImageView(
                                                          imagePath: ImageConstant
                                                              .imgMenuLightBlue90015x53,
                                                          height:
                                                              getVerticalSize(
                                                                  15.00),
                                                          width:
                                                              getHorizontalSize(
                                                                  43.00),
                                                          radius: BorderRadius
                                                              .circular(
                                                                  getHorizontalSize(
                                                                      7.00)),
                                                          margin: getMargin(
                                                              left: 24,
                                                              top: 10,
                                                              bottom: 12))
                                                    ]))),
                                        Padding(
                                            padding: getPadding(
                                                left: 20, top: 9, right: 90),
                                            child: Row(
                                                mainAxisAlignment:
                                                    MainAxisAlignment
                                                        .spaceBetween,
                                                children: [
                                                  Padding(
                                                      padding:
                                                          getPadding(bottom: 1),
                                                      child: Text(
                                                          "lbl_chat1".tr,
                                                          overflow: TextOverflow
                                                              .ellipsis,
                                                          textAlign:
                                                              TextAlign.left,
                                                          style: AppStyle
                                                              .txtNotoKufiArabicRegular16
                                                              .copyWith(
                                                                  height:
                                                                      getVerticalSize(
                                                                          1.00)))),
                                                  Padding(
                                                      padding:
                                                          getPadding(top: 1),
                                                      child: Text("lbl13".tr,
                                                          overflow: TextOverflow
                                                              .ellipsis,
                                                          textAlign:
                                                              TextAlign.left,
                                                          style: AppStyle
                                                              .txtNotoKufiArabicRegular16Bluegray400
                                                              .copyWith(
                                                                  height:
                                                                      getVerticalSize(
                                                                          1.00))))
                                                ])),
                                        Padding(
                                            padding:
                                                getPadding(left: 20, top: 3),
                                            child: Row(children: [
                                              Padding(
                                                  padding:
                                                      getPadding(bottom: 1),
                                                  child: Text(
                                                      "lbl_22_10_2022".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
                                                      style: AppStyle
                                                          .txtNotoKufiArabicRegular16
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00)))),
                                              Padding(
                                                  padding: getPadding(
                                                      left: 38, top: 1),
                                                  child: Text("msg4".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
                                                      style: AppStyle
                                                          .txtNotoKufiArabicRegular16Bluegray400
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00))))
                                            ])),
                                        Padding(
                                            padding:
                                                getPadding(left: 22, top: 3),
                                            child: Row(children: [
                                              Padding(
                                                  padding:
                                                      getPadding(bottom: 2),
                                                  child: Text(
                                                      "lbl_22_11_2022".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
                                                      style: AppStyle
                                                          .txtNotoKufiArabicRegular16
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00)))),
                                              Padding(
                                                  padding: getPadding(
                                                      left: 40, top: 2),
                                                  child: Text("msg5".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
                                                      style: AppStyle
                                                          .txtNotoKufiArabicRegular16Bluegray400
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00))))
                                            ])),
                                        Padding(
                                            padding: getPadding(
                                                left: 20, top: 1, right: 90),
                                            child: Row(
                                                mainAxisAlignment:
                                                    MainAxisAlignment
                                                        .spaceBetween,
                                                children: [
                                                  Container(
                                                      height: getVerticalSize(
                                                          32.00),
                                                      width: getHorizontalSize(
                                                          67.00),
                                                      child: Stack(
                                                          alignment: Alignment
                                                              .topCenter,
                                                          children: [
                                                            CustomImageView(
                                                                svgPath:
                                                                    ImageConstant
                                                                        .imgMenu,
                                                                height:
                                                                    getVerticalSize(
                                                                        29.00),
                                                                width:
                                                                    getHorizontalSize(
                                                                        67.00),
                                                                radius: BorderRadius
                                                                    .circular(
                                                                        getHorizontalSize(
                                                                            13.00)),
                                                                alignment: Alignment
                                                                    .bottomCenter),
                                                            Align(
                                                                alignment:
                                                                    Alignment
                                                                        .topCenter,
                                                                child: Text(
                                                                    "lbl14".tr,
                                                                    overflow:
                                                                        TextOverflow
                                                                            .ellipsis,
                                                                    textAlign:
                                                                        TextAlign
                                                                            .left,
                                                                    style: AppStyle
                                                                        .txtNotoKufiArabicRegular16WhiteA700
                                                                        .copyWith(
                                                                            height:
                                                                                getVerticalSize(1.00))))
                                                          ])),
                                                  Text("msg6".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
                                                      style: AppStyle
                                                          .txtNotoKufiArabicRegular16Bluegray400
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00)))
                                                ])),
                                        Padding(
                                            padding:
                                                getPadding(left: 20, top: 5),
                                            child: Row(children: [
                                              Text("lbl_10000_iqd".tr,
                                                  overflow:
                                                      TextOverflow.ellipsis,
                                                  textAlign: TextAlign.left,
                                                  style: AppStyle
                                                      .txtNotoKufiArabicRegular16
                                                      .copyWith(
                                                          height:
                                                              getVerticalSize(
                                                                  1.00))),
                                              Padding(
                                                  padding: getPadding(left: 66),
                                                  child: Text("lbl15".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
                                                      style: AppStyle
                                                          .txtNotoKufiArabicRegular16Bluegray400
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      1.00))))
                                            ])),
                                        Container(
                                            width: size.width,
                                            margin: getMargin(top: 22),
                                            padding: getPadding(
                                                left: 15,
                                                top: 19,
                                                right: 15,
                                                bottom: 19),
                                            decoration: AppDecoration
                                                .fillLightblue900e5
                                                .copyWith(
                                                    borderRadius:
                                                        BorderRadiusStyle
                                                            .roundedBorder37),
                                            child: Row(
                                                mainAxisAlignment:
                                                    MainAxisAlignment.end,
                                                children: [
                                                  Padding(
                                                      padding: getPadding(
                                                          top: 7, bottom: 6),
                                                      child: Text("lbl16".tr,
                                                          overflow: TextOverflow
                                                              .ellipsis,
                                                          textAlign:
                                                              TextAlign.left,
                                                          style: AppStyle
                                                              .txtNotoKufiArabicRegular12Gray300
                                                              .copyWith(
                                                                  height:
                                                                      getVerticalSize(
                                                                          0.53)))),
                                                  CustomImageView(
                                                      svgPath: ImageConstant
                                                          .imgCamera,
                                                      height: getSize(24.00),
                                                      width: getSize(24.00),
                                                      margin: getMargin(
                                                          left: 12,
                                                          top: 6,
                                                          bottom: 7),
                                                      onTap: () {
                                                        onTapImgCamera();
                                                      }),
                                                  Padding(
                                                      padding: getPadding(
                                                          left: 48,
                                                          top: 7,
                                                          bottom: 6),
                                                      child: Text("lbl17".tr,
                                                          overflow: TextOverflow
                                                              .ellipsis,
                                                          textAlign:
                                                              TextAlign.left,
                                                          style: AppStyle
                                                              .txtNotoKufiArabicRegular12Gray300
                                                              .copyWith(
                                                                  height:
                                                                      getVerticalSize(
                                                                          0.53)))),
                                                  CustomImageView(
                                                      svgPath: ImageConstant
                                                          .imgDashboard,
                                                      height: getSize(24.00),
                                                      width: getSize(24.00),
                                                      margin: getMargin(
                                                          left: 12,
                                                          top: 6,
                                                          bottom: 7)),
                                                  CustomButton(
                                                      height: 36,
                                                      width: 104,
                                                      text: "lbl18".tr,
                                                      margin: getMargin(
                                                          left: 36, bottom: 1),
                                                      suffixWidget: Container(
                                                          margin: getMargin(
                                                              left: 12),
                                                          child: CustomImageView(
                                                              svgPath:
                                                                  ImageConstant
                                                                      .imgHome)))
                                                ]))
                                      ]))))
                    ]))));
  }

  onTapNotification() {
    Get.toNamed(AppRoutes.notfiScreen);
  }

  onTapImgCamera() async {
    await PermissionManager.askForPermission(Permission.camera);
    await PermissionManager.askForPermission(Permission.storage);
    List<String?>? imageList = [];
    await FileManager().showModelSheetForImage(getImages: (value) async {
      imageList = value;
    });
  }
}
