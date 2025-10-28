import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

class BottomNavBarWidget extends StatelessWidget {
  const BottomNavBarWidget({
    super.key,
    this.currentIndex = 0,
    this.onItemSelected,
    this.onCameraTap,
  });

  final int currentIndex;
  final ValueChanged<int>? onItemSelected;
  final VoidCallback? onCameraTap;

  @override
  Widget build(BuildContext context) {
    final int selectedIndex = currentIndex >= 2 ? currentIndex + 1 : currentIndex;
    return BottomNavigationBar(
      type: BottomNavigationBarType.fixed,
      currentIndex: selectedIndex,
      items: const <BottomNavigationBarItem>[
        BottomNavigationBarItem(
          icon: Icon(Icons.home),
          label: 'Home',
        ),
        BottomNavigationBarItem(
          icon: Icon(FontAwesomeIcons.heart),
          label: 'Wish List',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.camera_alt),
          label: 'Camera',
        ),
        BottomNavigationBarItem(
          icon: Icon(FontAwesomeIcons.shoppingBag),
          label: 'Cart',
        ),
        BottomNavigationBarItem(
          icon: Icon(FontAwesomeIcons.dashcube),
          label: 'Dashboard',
        ),
      ],
      selectedItemColor: const Color(0xFFAA292E),
      onTap: (index) {
        if (index == 2) {
          onCameraTap?.call();
          return;
        }
        final int adjustedIndex = index > 2 ? index - 1 : index;
        (onItemSelected ?? (_) {})(adjustedIndex);
      },
    );
  }
}
