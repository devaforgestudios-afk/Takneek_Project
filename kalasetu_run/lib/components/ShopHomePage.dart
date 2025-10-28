
import 'package:flutter/material.dart';
import 'package:flutter_ecommerce_app/common_widget/CircularProgress.dart';
import 'package:flutter_ecommerce_app/common_widget/GridTilesCategory.dart';
import 'package:flutter_ecommerce_app/models/ShopModel.dart';

ShopModel? shopModel;

class ShopHomePage extends StatefulWidget {
  final String slug;
  final bool isSubList;

  const ShopHomePage({Key? key, required this.slug, this.isSubList = false})
      : super(key: key);
  @override
  _ShopHomePageState createState() => _ShopHomePageState();
}

class _ShopHomePageState extends State<ShopHomePage> {
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<ShopModel?>(
      future: getCategoryList(widget.slug, widget.isSubList),
      builder: (context, AsyncSnapshot<ShopModel?> snapshot) {
        switch (snapshot.connectionState) {
          case ConnectionState.none:
          case ConnectionState.waiting:
            return CircularProgress();
          default:
            if (snapshot.hasError)
              return Text('Error: ${snapshot.error}');
            else
              return createListView(context, snapshot);
        }
      },
    );
  }
}

Widget createListView(
    BuildContext context, AsyncSnapshot<ShopModel?> snapshot) {
  final values = snapshot.data;
  final List<Data> results = values?.data ?? [];
  return GridView.count(
    crossAxisCount: 3,
    padding: EdgeInsets.all(1.0),
    childAspectRatio: 8.0 / 9.0,
    children: List<Widget>.generate(results.length, (index) {
      return GridTile(
          child: GridTilesCategory(
              name: results[index].shopName ?? '',
              imageUrl: results[index].shopImage ?? '',slug:results[index].slug ?? ''));
    }),
  );
}

Future<ShopModel?> getCategoryList(String slug, bool isSubList) async {
  return shopModel;
}
//https://api.evaly.com.bd/core/public/category/shops/bags-luggage-966bc8aac/?page=1&limit=15