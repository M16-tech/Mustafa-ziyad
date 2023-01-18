import '../dashboard_one_screen/widgets/dashboard_one_item_widget.dart';
import 'controller/dashboard_one_controller.dart';
import 'models/dashboard_one_item_model.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg_provider/flutter_svg_provider.dart' as fs;
import 'package:rrar_s_application2/core/app_export.dart';
import 'package:rrar_s_application2/widgets/app_bar/appbar_image.dart';
import 'package:rrar_s_application2/widgets/app_bar/custom_app_bar.dart';
import 'package:rrar_s_application2/widgets/custom_button.dart';

class DashboardOneScreen extends GetWidget<DashboardOneController> {
  @override
  Widget build(BuildContext context) {
    return SafeArea(
        child: Scaffold(
            backgroundColor: ColorConstant.whiteA700,
            body: SizedBox(
                width: size.width,
                child: SingleChildScrollView(
                    child: Container(
                        width: size.width,
                        child: Column(
                            mainAxisAlignment: MainAxisAlignment.start,
                            children: [
                              Container(
                                  width: size.width,
                                  padding: getPadding(top: 12, bottom: 12),
                                  decoration: BoxDecoration(
                                      image: DecorationImage(
                                          image: AssetImage(
                                              ImageConstant.imgGroup1),
                                          fit: BoxFit.cover)),
                                  child: Column(
                                      mainAxisAlignment: MainAxisAlignment.end,
                                      children: [
                                        CustomAppBar(
                                            height: getVerticalSize(60.00),
                                            title: AppbarImage(
                                                height: getVerticalSize(60.00),
                                                width:
                                                    getHorizontalSize(151.00),
                                                imagePath:
                                                    ImageConstant.imgLogo3,
                                                margin: getMargin(left: 16)),
                                            actions: [
                                              AppbarImage(
                                                  height: getSize(32.00),
                                                  width: getSize(32.00),
                                                  svgPath: ImageConstant
                                                      .imgNotification,
                                                  margin: getMargin(
                                                      left: 16,
                                                      top: 14,
                                                      right: 16,
                                                      bottom: 13),
                                                  onTap: onTapNotification2)
                                            ]),
                                        Container(
                                            width: getHorizontalSize(250.00),
                                            margin: getMargin(
                                                left: 55, top: 24, right: 55),
                                            padding: getPadding(
                                                left: 58,
                                                top: 104,
                                                right: 58,
                                                bottom: 104),
                                            decoration: BoxDecoration(
                                                image: DecorationImage(
                                                    image: fs.Svg(ImageConstant
                                                        .imgGroup16),
                                                    fit: BoxFit.cover)),
                                            child: Column(
                                                mainAxisAlignment:
                                                    MainAxisAlignment.center,
                                                children: [
                                                  Padding(
                                                      padding:
                                                          getPadding(top: 3),
                                                      child: Text("lbl20".tr,
                                                          overflow: TextOverflow
                                                              .ellipsis,
                                                          textAlign:
                                                              TextAlign.left,
                                                          style: AppStyle
                                                              .txtNotoKufiArabicBold20
                                                              .copyWith(
                                                                  height:
                                                                      getVerticalSize(
                                                                          1.00))))
                                                ]))
                                      ])),
                              Container(
                                  width: size.width,
                                  margin: getMargin(top: 49),
                                  decoration: AppDecoration.fillWhiteA700,
                                  child: Column(
                                      mainAxisAlignment:
                                          MainAxisAlignment.start,
                                      children: [
                                        Padding(
                                            padding:
                                                getPadding(left: 16, right: 16),
                                            child: Obx(() => ListView.separated(
                                                physics:
                                                    BouncingScrollPhysics(),
                                                shrinkWrap: true,
                                                separatorBuilder:
                                                    (context, index) {
                                                  return SizedBox(
                                                      height: getVerticalSize(
                                                          12.00));
                                                },
                                                itemCount: controller
                                                    .dashboardOneModelObj
                                                    .value
                                                    .dashboardOneItemList
                                                    .length,
                                                itemBuilder: (context, index) {
                                                  DashboardOneItemModel model =
                                                      controller
                                                          .dashboardOneModelObj
                                                          .value
                                                          .dashboardOneItemList[index];
                                                  return DashboardOneItemWidget(
                                                      model);
                                                }))),
                                        Container(
                                            width: size.width,
                                            margin: getMargin(top: 239),
                                            padding: getPadding(
                                                left: 25,
                                                top: 19,
                                                right: 25,
                                                bottom: 19),
                                            decoration: AppDecoration
                                                .fillLightblue900e5
                                                .copyWith(
                                                    borderRadius:
                                                        BorderRadiusStyle
                                                            .roundedBorder37),
                                            child: Row(
                                                mainAxisAlignment:
                                                    MainAxisAlignment.center,
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
                                                  CustomButton(
                                                      height: 36,
                                                      width: 96,
                                                      text: "lbl17".tr,
                                                      margin: getMargin(
                                                          left: 36, bottom: 1),
                                                      suffixWidget: Container(
                                                          margin: getMargin(
                                                              left: 12),
                                                          child: CustomImageView(
                                                              svgPath: ImageConstant
                                                                  .imgDashboardWhiteA70001))),
                                                  Padding(
                                                      padding: getPadding(
                                                          left: 36,
                                                          top: 7,
                                                          bottom: 6),
                                                      child: Text("lbl18".tr,
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
                                                          .imgHomeGray300,
                                                      height: getSize(24.00),
                                                      width: getSize(24.00),
                                                      margin: getMargin(
                                                          left: 12,
                                                          top: 6,
                                                          right: 1,
                                                          bottom: 7))
                                                ]))
                                      ]))
                            ]))))));
  }

  onTapNotification2() {
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
