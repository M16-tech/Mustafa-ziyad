import 'package:rrar_s_application2/core/app_export.dart';
import 'package:rrar_s_application2/presentation/app_navigation_screen/models/app_navigation_model.dart';

class AppNavigationController extends GetxController {
  Rx<AppNavigationModel> appNavigationModelObj = AppNavigationModel().obs;

  @override
  void onReady() {
    super.onReady();
  }

  @override
  void onClose() {
    super.onClose();
  }
}
