import '../notfi_screen/widgets/notfi_item_widget.dart';
import 'controller/notfi_controller.dart';
import 'models/notfi_item_model.dart';
import 'package:flutter/material.dart';
import 'package:rrar_s_application2/core/app_export.dart';
import 'package:rrar_s_application2/widgets/app_bar/appbar_image.dart';
import 'package:rrar_s_application2/widgets/app_bar/custom_app_bar.dart';
import 'package:rrar_s_application2/widgets/custom_floating_button.dart';

class NotfiScreen extends GetWidget<NotfiController> {
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
                          getMargin(left: 25, top: 31, right: 25, bottom: 28))
                ],
                styleType: Style.bgStyle_1),
            body: Container(
                width: size.width,
                child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    mainAxisAlignment: MainAxisAlignment.start,
                    children: [
                      Padding(
                          padding: getPadding(top: 24),
                          child: Row(
                              mainAxisAlignment: MainAxisAlignment.end,
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text("lbl19".tr,
                                    overflow: TextOverflow.ellipsis,
                                    textAlign: TextAlign.left,
                                    style: AppStyle
                                        .txtNotoKufiArabicMedium20Gray800
                                        .copyWith(
                                            height: getVerticalSize(1.00))),
                                CustomImageView(
                                    imagePath:
                                        ImageConstant.imgMenuLightBlue90015x53,
                                    height: getVerticalSize(15.00),
                                    width: getHorizontalSize(37.00),
                                    radius: BorderRadius.circular(
                                        getHorizontalSize(7.00)),
                                    margin: getMargin(
                                        left: 12, top: 10, bottom: 12))
                              ])),
                      Container(
                          height: getVerticalSize(581.00),
                          width: size.width,
                          margin: getMargin(top: 23),
                          child: Stack(
                              alignment: Alignment.bottomCenter,
                              children: [
                                Align(
                                    alignment: Alignment.topCenter,
                                    child: Padding(
                                        padding: getPadding(
                                            left: 16, right: 16, bottom: 50),
                                        child: Obx(() => ListView.separated(
                                            physics: BouncingScrollPhysics(),
                                            shrinkWrap: true,
                                            separatorBuilder: (context, index) {
                                              return SizedBox(
                                                  height:
                                                      getVerticalSize(11.00));
                                            },
                                            itemCount: controller.notfiModelObj
                                                .value.notfiItemList.length,
                                            itemBuilder: (context, index) {
                                              NotfiItemModel model = controller
                                                  .notfiModelObj
                                                  .value
                                                  .notfiItemList[index];
                                              return NotfiItemWidget(model);
                                            })))),
                                Align(
                                    alignment: Alignment.bottomCenter,
                                    child: Container(
                                        width: size.width,
                                        margin: getMargin(top: 506),
                                        padding: getPadding(all: 25),
                                        decoration: AppDecoration
                                            .fillLightblue900e5
                                            .copyWith(
                                                borderRadius: BorderRadiusStyle
                                                    .roundedBorder37),
                                        child: Row(
                                            mainAxisAlignment:
                                                MainAxisAlignment.center,
                                            children: [
                                              Padding(
                                                  padding: getPadding(top: 1),
                                                  child: Text("lbl16".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
                                                      style: AppStyle
                                                          .txtNotoKufiArabicRegular12Gray300
                                                          .copyWith(
                                                              height:
                                                                  getVerticalSize(
                                                                      0.53)))),
                                              CustomImageView(
                                                  svgPath:
                                                      ImageConstant.imgCamera,
                                                  height: getSize(24.00),
                                                  width: getSize(24.00),
                                                  margin: getMargin(
                                                      left: 12, bottom: 1),
                                                  onTap: () {
                                                    onTapImgCamera();
                                                  }),
                                              Padding(
                                                  padding: getPadding(
                                                      left: 48, top: 1),
                                                  child: Text("lbl17".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
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
                                                      left: 12, bottom: 1)),
                                              Padding(
                                                  padding: getPadding(
                                                      left: 48, top: 1),
                                                  child: Text("lbl18".tr,
                                                      overflow:
                                                          TextOverflow.ellipsis,
                                                      textAlign: TextAlign.left,
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
                                                      right: 1,
                                                      bottom: 1))
                                            ])))
                              ]))
                    ])),
            floatingActionButton: CustomFloatingButton(
                height: 47,
                width: 47,
                child: CustomImageView(
                    svgPath: ImageConstant.imgClose,
                    height: getVerticalSize(23.50),
                    width: getHorizontalSize(23.50)))));
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
