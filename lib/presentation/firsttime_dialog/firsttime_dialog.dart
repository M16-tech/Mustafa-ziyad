import 'controller/firsttime_controller.dart';
import 'package:flutter/material.dart';
import 'package:rrar_s_application2/core/app_export.dart';
import 'package:rrar_s_application2/widgets/custom_icon_button.dart';
import 'package:rrar_s_application2/presentation/reotp_bottomsheet/reotp_bottomsheet.dart';
import 'package:rrar_s_application2/presentation/reotp_bottomsheet/controller/reotp_controller.dart';

// ignore_for_file: must_be_immutable
class FirsttimeDialog extends StatelessWidget {
  FirsttimeDialog(this.controller);

  FirsttimeController controller;

  @override
  Widget build(BuildContext context) {
    return Container(
        padding: getPadding(left: 17, top: 14, right: 17, bottom: 14),
        decoration: AppDecoration.fillWhiteA700
            .copyWith(borderRadius: BorderRadiusStyle.roundedBorder42),
        child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.end,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Padding(
                  padding: getPadding(right: 3),
                  child: Text("lbl".tr,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.left,
                      style: AppStyle.txtNotoKufiArabicMedium20
                          .copyWith(height: getVerticalSize(1.00)))),
              Padding(
                  padding: getPadding(right: 3),
                  child: Text("msg".tr,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.left,
                      style: AppStyle.txtNotoKufiArabicRegular14
                          .copyWith(height: getVerticalSize(1.00)))),
              Container(
                  margin: getMargin(top: 35, right: 3),
                  padding: getPadding(left: 16, top: 6, right: 16, bottom: 6),
                  decoration: AppDecoration.outlineCyan70001.copyWith(
                      borderRadius: BorderRadiusStyle.roundedBorder12),
                  child: Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Padding(
                            padding: getPadding(top: 9),
                            child: Text("lbl2".tr,
                                overflow: TextOverflow.ellipsis,
                                textAlign: TextAlign.left,
                                style: AppStyle.txtCairoRegular1536
                                    .copyWith(height: getVerticalSize(1.00)))),
                        CustomImageView(
                            svgPath: ImageConstant.imgUser,
                            height: getSize(24.00),
                            width: getSize(24.00),
                            margin: getMargin(left: 6, top: 8, bottom: 5))
                      ])),
              Container(
                  margin: getMargin(top: 12, right: 3),
                  padding: getPadding(left: 16, top: 7, right: 16, bottom: 7),
                  decoration: AppDecoration.outlineCyan70002.copyWith(
                      borderRadius: BorderRadiusStyle.roundedBorder12),
                  child:
                      Row(mainAxisAlignment: MainAxisAlignment.end, children: [
                    Padding(
                        padding: getPadding(top: 6),
                        child: Text("lbl3".tr,
                            overflow: TextOverflow.ellipsis,
                            textAlign: TextAlign.left,
                            style: AppStyle.txtCairoRegular1536
                                .copyWith(height: getVerticalSize(1.00)))),
                    CustomImageView(
                        svgPath: ImageConstant.imgCall,
                        height: getSize(24.00),
                        width: getSize(24.00),
                        margin: getMargin(left: 12, top: 5, bottom: 5))
                  ])),
              CustomIconButton(
                  height: 71,
                  width: 71,
                  margin: getMargin(top: 63, bottom: 2),
                  variant: IconButtonVariant.FillLightblue900,
                  shape: IconButtonShape.RoundedBorder35,
                  padding: IconButtonPadding.PaddingAll23,
                  alignment: Alignment.centerLeft,
                  onTap: () {
                    onTapBtnArrowleft();
                  },
                  child: CustomImageView(svgPath: ImageConstant.imgArrowleft))
            ]));
  }

  onTapBtnArrowleft() {
    Get.bottomSheet(
      ReotpBottomsheet(
        Get.put(
          ReotpController(),
        ),
      ),
      isScrollControlled: true,
    );
  }
}
