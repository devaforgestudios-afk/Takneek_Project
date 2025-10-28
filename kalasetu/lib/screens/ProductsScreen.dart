
import 'package:flutter/material.dart';
import 'package:flutter_ecommerce_app/common_widget/AppBarWidget.dart';
import 'package:flutter_ecommerce_app/common_widget/CircularProgress.dart';
import 'package:flutter_ecommerce_app/common_widget/GridTilesProducts.dart';
import 'package:flutter_ecommerce_app/models/ProductsModel.dart';

class ProductsScreen extends StatefulWidget {
  final String name;
  final String slug;

  const ProductsScreen({Key? key, required this.name, required this.slug})
      : super(key: key);

  @override
  _ProductsScreenState createState() => _ProductsScreenState();
}

class _ProductsScreenState extends State<ProductsScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: appBarWidget(context),
      body: Container(
          alignment: Alignment.topLeft,
          padding: EdgeInsets.only(left: 10, right: 10),
          child: ProductListWidget(
            slug: widget.slug,
          )),
    );
  }
}

class ProductListWidget extends StatelessWidget {
  final String slug;

  const ProductListWidget({Key? key, required this.slug}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<ProductsModels?>(
      future: getProductList(slug, false),
      builder: (context, AsyncSnapshot<ProductsModels?> snapshot) {
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

ProductsModels? products;

Future<ProductsModels?> getProductList(String slug, bool isSubList) async {
  return products;
}

Widget createListView(
    BuildContext context, AsyncSnapshot<ProductsModels?> snapshot) {
  final values = snapshot.data;
  final List<Results> results = values?.results ?? [];
  return GridView.count(
    crossAxisCount: 2,
//    physics: NeverScrollableScrollPhysics(),
    padding: EdgeInsets.all(1.0),
    childAspectRatio: 8.0 / 12.0,
    children: List<Widget>.generate(results.length, (index) {
      return GridTile(
          child: GridTilesProducts(
        name: results[index].name ?? '',
        imageUrl: results[index].imageUrls?[0] ?? '',
        slug: results[index].slug ?? '',
        price: results[index].maxPrice ?? '',
      ));
    }),
  );
}
