import 'dart:ui';
import 'package:flutter/material.dart';

class ColorConstant {
  static Color red40063 = fromHex('#63eb5757');

  static Color orange4003f = fromHex('#3ffea72e');

  static Color red400 = fromHex('#eb5757');

  static Color black9003f = fromHex('#3f000000');

  static Color lightBlue900 = fromHex('#186692');

  static Color teal600 = fromHex('#008280');

  static Color lightBlue900E5 = fromHex('#e5186692');

  static Color blueGray80002 = fromHex('#44444f');

  static Color black900 = fromHex('#000000');

  static Color cyan400Ce = fromHex('#ce13cbd0');

  static Color blueGray800 = fromHex('#275a5b');

  static Color blueGray900 = fromHex('#2f3032');

  static Color cyan60003 = fromHex('#00b8b5');

  static Color tealA700 = fromHex('#00cc99');

  static Color gray400 = fromHex('#b3b3b3');

  static Color gray500 = fromHex('#939393');

  static Color blueGray400 = fromHex('#8a8a8a');

  static Color tealA70063 = fromHex('#6300cc99');

  static Color gray800 = fromHex('#3f3f3f');

  static Color gray900 = fromHex('#1b1b1b');

  static Color blueGray80001 = fromHex('#285b5b');

  static Color gray300 = fromHex('#dadada');

  static Color cyan60001 = fromHex('#07b6bb');

  static Color cyan60002 = fromHex('#01b3b6');

  static Color blueGray7003a = fromHex('#3a515151');

  static Color cyan6003f = fromHex('#3f00a7cd');

  static Color bluegray400 = fromHex('#888888');

  static Color whiteA70001 = fromHex('#fefefe');

  static Color cyan70001 = fromHex('#009aa3');

  static Color cyan70002 = fromHex('#009ca4');

  static Color cyan600 = fromHex('#00b9ba');

  static Color cyan700 = fromHex('#0098a2');

  static Color whiteA700 = fromHex('#ffffff');

  static Color fromHex(String hexString) {
    final buffer = StringBuffer();
    if (hexString.length == 6 || hexString.length == 7) buffer.write('ff');
    buffer.write(hexString.replaceFirst('#', ''));
    return Color(int.parse(buffer.toString(), radix: 16));
  }
}
