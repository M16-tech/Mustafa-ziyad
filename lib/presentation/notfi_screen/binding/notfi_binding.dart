import '../controller/notfi_controller.dart';
import 'package:get/get.dart';

class NotfiBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => NotfiController());
  }
}
