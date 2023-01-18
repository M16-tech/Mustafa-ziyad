import '../controller/dashboard_one_controller.dart';
import '../models/dashboard_one_item_model.dart';
import 'package:flutter/material.dart';
import 'package:rrar_s_application2/core/app_export.dart';

// ignore: must_be_immutable
class DashboardOneItemWidget extends StatelessWidget {
  DashboardOneItemWidget(this.dashboardOneItemModelObj);

  DashboardOneItemModel dashboardOneItemModelObj;

  var controller = Get.find<DashboardOneController>();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: getPadding(
        left: 22,
        top: 18,
        right: 22,
        bottom: 18,
      ),
      decoration: AppDecoration.fillOrange4003f.copyWith(
        borderRadius: BorderRadiusStyle.roundedBorder24,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            height: getVerticalSize(
              41.00,
            ),
            width: getHorizontalSize(
              75.00,
            ),
            margin: getMargin(
              top: 7,
              bottom: 14,
            ),
            child: Stack(
              alignment: Alignment.center,
              children: [
                Align(
                  alignment: Alignment.bottomCenter,
                  child: Padding(
                    padding: getPadding(
                      bottom: 2,
                    ),
                    child: Text(
                      "lbl_0".tr,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.left,
                      style: AppStyle.txtPoppinsSemiBold14.copyWith(
                        letterSpacing: getHorizontalSize(
                          0.10,
                        ),
                        height: getVerticalSize(
                          1.00,
                        ),
                      ),
                    ),
                  ),
                ),
                Align(
                  alignment: Alignment.center,
                  child: Container(
                    height: getVerticalSize(
                      41.00,
                    ),
                    width: getHorizontalSize(
                      75.00,
                    ),
                    child: Stack(
                      alignment: Alignment.centerLeft,
                      children: [
                        CustomImageView(
                          svgPath: ImageConstant.imgDashboardGray30001,
                          height: getVerticalSize(
                            41.00,
                          ),
                          width: getHorizontalSize(
                            75.00,
                          ),
                          alignment: Alignment.center,
                        ),
                        CustomImageView(
                          svgPath: ImageConstant.imgDashboardAmber700,
                          height: getVerticalSize(
                            41.00,
                          ),
                          width: getHorizontalSize(
                            62.00,
                          ),
                          alignment: Alignment.centerLeft,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: getPadding(
              right: 19,
              bottom: 1,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                Padding(
                  padding: getPadding(
                    right: 1,
                  ),
                  child: Text(
                    "lbl21".tr,
                    overflow: TextOverflow.ellipsis,
                    textAlign: TextAlign.left,
                    style:
                        AppStyle.txtNotoKufiArabicRegular12Bluegray400.copyWith(
                      height: getVerticalSize(
                        0.53,
                      ),
                    ),
                  ),
                ),
                Padding(
                  padding: getPadding(
                    top: 6,
                  ),
                  child: Text(
                    "lbl_0".tr,
                    overflow: TextOverflow.ellipsis,
                    textAlign: TextAlign.left,
                    style: AppStyle.txtNotoKufiArabicRegular16Gray900.copyWith(
                      height: getVerticalSize(
                        1.00,
                      ),
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
