import '../controller/dashboard_one_controller.dart';
import 'package:get/get.dart';

class DashboardOneBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => DashboardOneController());
  }
}
