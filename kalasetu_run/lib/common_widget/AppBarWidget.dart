import 'package:flutter/material.dart';
import 'package:flutter_ecommerce_app/components/AppSignIn.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

PreferredSizeWidget appBarWidget(context) {
  return AppBar(
    elevation: 0.0,
    centerTitle: true,
    title: Image.asset(
      "assets/images/ic_app.png",
      width: 140,
      height: 60,
      fit: BoxFit.contain,
    ),
    actions: <Widget>[
      IconButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => AppSignIn()),
          );
        },
        icon: Icon(FontAwesomeIcons.user),
        color: Color(0xFF323232),
      ),
    ],
  );
}
