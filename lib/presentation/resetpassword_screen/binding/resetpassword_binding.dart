import '../controller/resetpassword_controller.dart';
import 'package:get/get.dart';

class ResetpasswordBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => ResetpasswordController());
  }
}
