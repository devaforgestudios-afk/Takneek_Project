import 'package:flutter/material.dart';
import 'package:flutter_ecommerce_app/common_widget/CircularProgress.dart';
import 'package:flutter_ecommerce_app/common_widget/GridTilesCategory.dart';

import '../models/BrandModel.dart';

BrandModel? brandModel;

class BrandHomePage extends StatefulWidget {
  final String slug;
  final bool isSubList;

  const BrandHomePage({Key? key, required this.slug, this.isSubList = false})
      : super(key: key);
  @override
  _BrandHomePageState createState() => _BrandHomePageState();
}

class _BrandHomePageState extends State<BrandHomePage> {
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<BrandModel?>(
      future: getCategoryList(widget.slug, widget.isSubList),
      builder: (context, AsyncSnapshot<BrandModel?> snapshot) {
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
    BuildContext context, AsyncSnapshot<BrandModel?> snapshot) {
  final values = snapshot.data;
  final List<Results> results = values?.results ?? [];
  return GridView.count(
    crossAxisCount: 3,
    padding: EdgeInsets.all(1.0),
    childAspectRatio: 8.0 / 9.0,
    children: List<Widget>.generate(results.length, (index) {
      return GridTile(
          child: GridTilesCategory(
              name: results[index].name ?? '',
              imageUrl: results[index].imageUrl ?? '',
              slug: results[index].slug ?? ''));
    }),
  );
}

Future<BrandModel?> getCategoryList(String slug, bool isSubList) async {
  return brandModel;
}

//https://api.evaly.com.bd/core/public/brands/?limit=20&page=1&category=bags-luggage-966bc8aac