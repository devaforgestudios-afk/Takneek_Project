import 'package:flutter/material.dart';
import 'package:flutter_ecommerce_app/common_widget/AppBarWidget.dart';
import 'package:flutter_ecommerce_app/common_widget/BottomNavBarWidget.dart';
import 'package:flutter_ecommerce_app/common_widget/DrawerWidget.dart';
import 'package:flutter_ecommerce_app/common_widget/camera/CameraCaptureSheet.dart';
import 'package:flutter_ecommerce_app/screens/HomeScreen.dart';
import 'package:flutter_ecommerce_app/screens/ShoppingCartScreen.dart';
import 'package:flutter_ecommerce_app/screens/WishListScreen.dart';

const Color kAppSurfaceColor = Color(0xFFDADAC9);

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: MyHomePage(),
      theme: ThemeData(
          fontFamily: 'Roboto',
          primaryColor: kAppSurfaceColor,
          primaryColorDark: kAppSurfaceColor,
          scaffoldBackgroundColor: kAppSurfaceColor,
          canvasColor: kAppSurfaceColor,
          appBarTheme: const AppBarTheme(
            backgroundColor: kAppSurfaceColor,
            surfaceTintColor: Colors.transparent,
            elevation: 0,
          ),
          drawerTheme: const DrawerThemeData(
            backgroundColor: kAppSurfaceColor,
          ),
          bottomNavigationBarTheme: const BottomNavigationBarThemeData(
            backgroundColor: kAppSurfaceColor,
          )),
      debugShowCheckedModeBanner: false,
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageNewState createState() => _MyHomePageNewState();
}

class _MyHomePageNewState extends State<MyHomePage> {
  int _currentIndex = 0;
  final List<Widget> viewContainer = [
    HomeScreen(),
    WishListScreen(),
    ShoppingCartScreen(),
    HomeScreen()
  ];

  void _onItemSelected(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  Future<void> _showCameraSheet() async {
    final capture = await showModalBottomSheet<CameraCaptureResult>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => const CameraCaptureSheet(),
    );

    if (!mounted || capture == null) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Captured image saved to ${capture.fileName}'),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: appBarWidget(context),
        drawer: DrawerWidget(),
        body: IndexedStack(
          index: _currentIndex,
          children: viewContainer,
        ),
        bottomNavigationBar: BottomNavBarWidget(
          currentIndex: _currentIndex,
          onItemSelected: _onItemSelected,
        ),
        floatingActionButton: FloatingActionButton.large(
          onPressed: _showCameraSheet,
          backgroundColor: const Color(0xFFAA292E),
          foregroundColor: Colors.white,
          shape: const CircleBorder(),
          child: const Icon(Icons.camera_alt, size: 32),
        ),
        floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      ),
    );
  }
}

