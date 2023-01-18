import '../controller/notfi_controller.dart';
import '../models/notfi_item_model.dart';
import 'package:flutter/material.dart';
import 'package:rrar_s_application2/core/app_export.dart';
import 'package:rrar_s_application2/widgets/custom_icon_button.dart';

// ignore: must_be_immutable
class NotfiItemWidget extends StatelessWidget {
  NotfiItemWidget(this.notfiItemModelObj);

  NotfiItemModel notfiItemModelObj;

  var controller = Get.find<NotfiController>();

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.topCenter,
      child: Container(
        padding: getPadding(
          top: 7,
          bottom: 7,
        ),
        decoration: AppDecoration.fillTealA70063.copyWith(
          borderRadius: BorderRadiusStyle.roundedBorder24,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            Padding(
              padding: getPadding(
                top: 3,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                mainAxisAlignment: MainAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      Padding(
                        padding: getPadding(
                          bottom: 3,
                        ),
                        child: Text(
                          "lbl_22_10_2020".tr,
                          overflow: TextOverflow.ellipsis,
                          textAlign: TextAlign.left,
                          style: AppStyle.txtNotoKufiArabicRegular10.copyWith(
                            height: getVerticalSize(
                              1.00,
                            ),
                          ),
                        ),
                      ),
                      Padding(
                        padding: getPadding(
                          left: 54,
                        ),
                        child: Text(
                          "msg9".tr,
                          overflow: TextOverflow.ellipsis,
                          textAlign: TextAlign.left,
                          style: AppStyle.txtNotoKufiArabicRegular12Bluegray900
                              .copyWith(
                            height: getVerticalSize(
                              0.53,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  Container(
                    width: getHorizontalSize(
                      198.00,
                    ),
                    margin: getMargin(
                      top: 5,
                    ),
                    child: Text(
                      "msg10".tr,
                      maxLines: null,
                      textAlign: TextAlign.right,
                      style: AppStyle.txtNotoKufiArabicRegular10Bluegray400
                          .copyWith(
                        height: getVerticalSize(
                          0.63,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            CustomIconButton(
              height: 47,
              width: 47,
              margin: getMargin(
                top: 8,
                bottom: 7,
              ),
              variant: IconButtonVariant.FillTealA700,
              child: CustomImageView(
                svgPath: ImageConstant.imgCheckmark,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
