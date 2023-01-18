import 'package:rrar_s_application2/core/app_export.dart';
import 'package:rrar_s_application2/presentation/dashboard_screen/models/dashboard_model.dart';

class DashboardController extends GetxController {
  Rx<DashboardModel> dashboardModelObj = DashboardModel().obs;

  @override
  void onReady() {
    super.onReady();
    Future.delayed(const Duration(milliseconds: 3000), () {
      Get.toNamed(AppRoutes.dashboardOneScreen);
    });
  }

  @override
  void onClose() {
    super.onClose();
  }
}
