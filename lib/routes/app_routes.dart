import 'package:rrar_s_application2/presentation/dashboard_screen/dashboard_screen.dart';
import 'package:rrar_s_application2/presentation/dashboard_screen/binding/dashboard_binding.dart';
import 'package:rrar_s_application2/presentation/resetpassword_screen/resetpassword_screen.dart';
import 'package:rrar_s_application2/presentation/resetpassword_screen/binding/resetpassword_binding.dart';
import 'package:rrar_s_application2/presentation/notfi_screen/notfi_screen.dart';
import 'package:rrar_s_application2/presentation/notfi_screen/binding/notfi_binding.dart';
import 'package:rrar_s_application2/presentation/dashboard_one_screen/dashboard_one_screen.dart';
import 'package:rrar_s_application2/presentation/dashboard_one_screen/binding/dashboard_one_binding.dart';
import 'package:rrar_s_application2/presentation/app_navigation_screen/app_navigation_screen.dart';
import 'package:rrar_s_application2/presentation/app_navigation_screen/binding/app_navigation_binding.dart';
import 'package:get/get.dart';

class AppRoutes {
  static const String dashboardScreen = '/dashboard_screen';

  static const String resetpasswordScreen = '/resetpassword_screen';

  static const String notfiScreen = '/notfi_screen';

  static const String dashboardOneScreen = '/dashboard_one_screen';

  static const String appNavigationScreen = '/app_navigation_screen';

  static String initialRoute = '/initialRoute';

  static List<GetPage> pages = [
    GetPage(
      name: dashboardScreen,
      page: () => DashboardScreen(),
      bindings: [
        DashboardBinding(),
      ],
    ),
    GetPage(
      name: resetpasswordScreen,
      page: () => ResetpasswordScreen(),
      bindings: [
        ResetpasswordBinding(),
      ],
    ),
    GetPage(
      name: notfiScreen,
      page: () => NotfiScreen(),
      bindings: [
        NotfiBinding(),
      ],
    ),
    GetPage(
      name: dashboardOneScreen,
      page: () => DashboardOneScreen(),
      bindings: [
        DashboardOneBinding(),
      ],
    ),
    GetPage(
      name: appNavigationScreen,
      page: () => AppNavigationScreen(),
      bindings: [
        AppNavigationBinding(),
      ],
    ),
    GetPage(
      name: initialRoute,
      page: () => DashboardScreen(),
      bindings: [
        DashboardBinding(),
      ],
    )
  ];
}
